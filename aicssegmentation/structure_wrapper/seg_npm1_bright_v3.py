import numpy as np
import os
from skimage.morphology import remove_small_objects, erosion, ball, dilation
from ..core.pre_processing_utils import intensity_normalization, image_smoothing_gaussian_3d,image_smoothing_gaussian_slice_by_slice, edge_preserving_smoothing_3d
from ..core.seg_dot import dot_slice_by_slice
from skimage.filters import threshold_triangle, threshold_otsu
from skimage.measure import label
from scipy.ndimage.morphology import binary_fill_holes
from aicssegmentation.core.output_utils import save_segmentation, NPM1_output
from aicsimageprocessing import resize
from skimage.io import imread
from scipy.ndimage.measurements import center_of_mass as com
from scipy.ndimage import label as labeling
from aicssegmentation.core.vessel import vesselnessSliceBySlice


# for debugging
import pdb
from skimage.io import imsave

def Workflow_npm1_bright_v3_single(struct_img,mitotic_stage,rescale_ratio,output_type, output_path, fn, output_func=None):
    '''
    no high level thresholindg is used - step2
    '''
    ##########################################################################
    # Basic PARAMETERS:
    #   note that these parameters are supposed to be fixed for the structure
    #   and work well accross different datasets

    intensity_norm_param = [15, 5]
    gaussian_smoothing_sigma = 1
    gaussian_smoothing_truncate_range = 3.0
    dot_2d_sigma = 2
    dot_2d_sigma_extra = 3
    minArea = 8
    low_level_min_size = 300
    ##########################################################################

    out_img_list = []
    out_name_list = []

    ###################
    # PRE_PROCESSING
    ###################
    # intenisty normalization (min/max)
    struct_img = intensity_normalization(struct_img, scaling_param=intensity_norm_param)

    out_img_list.append(struct_img.copy())
    out_name_list.append('im_norm')

    # rescale if needed
    if rescale_ratio>0:
        struct_img = resize(struct_img, [1, rescale_ratio, rescale_ratio], method="cubic")
        struct_img = (struct_img - struct_img.min() + 1e-8)/(struct_img.max() - struct_img.min() + 1e-8)
        gaussian_smoothing_truncate_range = gaussian_smoothing_truncate_range * rescale_ratio


    structure_img_smooth = edge_preserving_smoothing_3d(struct_img, numberOfIterations=10, conductance=1.2, timeStep=0.0625)

    out_img_list.append(structure_img_smooth.copy())
    out_name_list.append('im_smooth')

    ###################
    # core algorithm
    ###################
    # mitotic stage should align to folder name
    
    mito_seed_path_root = "/allen/aics/assay-dev/computational/data/Nucleus_structure_segmentation/trainset/NPM1_norm1/mem/"
    mito_seed_path = mito_seed_path_root + fn.replace('.tiff', '.mem_seg.tiff')
    # # mito_seed_path_root = "/allen/aics/assay-dev/computational/data/Nucleus_structure_segmentation/fibrillarin_segmentation_improvement/" + mitotic_stage + "/mito_seg/"
    # # mito_seed_path = mito_seed_path_root + fn + "_mem_segmentation.tif"

    # # Generate seed for mitotic cell
    mito_3d = imread(mito_seed_path)
    if np.ndim(mito_3d) == 4:
        mito_3d = mito_3d[:,:,:,0]


    # specific case for presentation
    # mito_seed_path_root = '/allen/aics/assay-dev/computational/data/Nucleus_structure_segmentation/presentation/mem_seg/FBL_NPM1/'
    # mito_seed_path = mito_seed_path_root + fn.replace('.czi', '_mem_segmentation.tiff')
    # mito_3d = imread(mito_seed_path)
    # mito_3d = (mito_3d == 2).astype(np.uint8)
    ###############################


    bw_high_level = np.zeros_like(mito_3d)
    # lab_low, num_obj = label(bw_low_level, return_num=True, connectivity=1)
    object_img = structure_img_smooth[mito_3d>0]

    local_cutoff = threshold_otsu(structure_img_smooth)
    otsu_mito = threshold_otsu(structure_img_smooth[mito_3d>0])

    # pdb.set_trace()
    local_diff = (local_cutoff - otsu_mito)
    adaptive_factor = 0
    local_otsu = 0

    # vessel_cutoff = 0.95
    # slice_cutoff = 0.03
    # local_otsu = 1.9 * otsu_mito # It was 0.13
    # bw_high_level[np.logical_and(structure_img_smooth> local_otsu, mito_3d>0)]=1
    # bw_high_level = dilation(bw_high_level, selem=ball(1.5))

    if local_diff >= 0.33:
        vessel_cutoff = 0.045
        slice_cutoff = 0.03
    
    elif local_diff >= 0.10 and local_diff < 0.33:
        vessel_cutoff = 0.105
        slice_cutoff = 0.04
        local_otsu = 2.1 * otsu_mito
        bw_high_level[np.logical_and(structure_img_smooth> local_otsu, mito_3d>0)]=1
    
    # When FBL seg is very brgiht
    elif local_diff < 0.05:
        vessel_cutoff = 0.15
        slice_cutoff = 0.06
        local_otsu = 2.5 * otsu_mito
        bw_high_level[np.logical_and(structure_img_smooth> local_otsu, mito_3d>0)]=1

    # if local_diff >= 0.15:
    #     vessel_cutoff = 0.04
    #     slice_cutoff = 0.02
    
    # # When FBL seg is very brgiht
    # elif local_diff < 0.05:
    #     vessel_cutoff = 0.105
    #     slice_cutoff = 0.03
    #     local_otsu = 1.7 * otsu_mito
    #     bw_high_level[np.logical_and(structure_img_smooth> local_otsu, mito_3d>0)]=1



    # print(local_diff, local_otsu, np.percentile(structure_img_smooth[mito_3d>0],25))

    res3 = vesselnessSliceBySlice(structure_img_smooth, [1], tau=0.5, whiteonblack=True)
    res1 = dot_slice_by_slice(structure_img_smooth, 2)
    response_bright = np.logical_or(res1>slice_cutoff,res3>vessel_cutoff) 
    total_bright =  np.logical_or(response_bright,bw_high_level)

    bw_final = total_bright
    # pdb.set_trace()


    ###################
    # POST-PROCESSING
    ###################
    seg = remove_small_objects(bw_final, min_size=minArea, connectivity=1, in_place=True)

    seg = seg>0
    seg = seg.astype(np.uint8)
    seg[seg>0]=255


    out_img_list.append(seg.copy())
    out_name_list.append('bw_fine')

    fn = fn+"_npm_bright"

    if output_type == 'default':
        # the default final output
        save_segmentation(seg, False, output_path, fn)
    elif output_type == 'AICS_pipeline':
        # pre-defined output function for pipeline data
        save_segmentation(seg, True, output_path, fn)
    elif output_type == 'customize':
        # the hook for passing in a customized output function
        output_fun(out_img_list, out_name_list, output_path, fn)
    elif output_type == 'return':
        return seg
    elif output_type == 'return_both':
        return (seg, mito_3d)
    else:
        # the hook for pre-defined RnD output functions (AICS internal)
        img_list, name_list = NPM1_output(out_img_list, out_name_list, output_type, output_path, fn)
        if output_type == 'QCB':
            return img_list, name_list

    # pdb.set_trace()