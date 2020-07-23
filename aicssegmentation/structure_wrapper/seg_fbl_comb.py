import numpy as np
import os
from skimage.morphology import remove_small_objects, erosion, ball, dilation
from ..core.pre_processing_utils import intensity_normalization, image_smoothing_gaussian_3d
from ..core.seg_dot import dot_slice_by_slice
from skimage.filters import threshold_triangle, threshold_otsu
from skimage.measure import label
from scipy.ndimage.morphology import binary_fill_holes
from aicssegmentation.core.output_utils import save_segmentation, NPM1_output
from aicsimageprocessing import resize

from skimage.io import imread, imsave
from scipy.ndimage.measurements import center_of_mass as com
from scipy.ndimage import label as labeling

# for debugging
import pdb

def Workflow_fbl_comb(struct_img,rescale_ratio,output_type, output_path, fn, output_func=None):
    ##########################################################################
    # PARAMETERS:
    #   note that these parameters are supposed to be fixed for the structure
    #   and work well accross different datasets

    intensity_norm_param = [5, 10]
    gaussian_smoothing_sigma = 0.5
    gaussian_smoothing_truncate_range = 3.0
    dot_2d_sigma = 1
    dot_2d_sigma_extra = 3
    dot_2d_cutoff = 0.0325
    dot_2d_cutoff_extra = 0.01
    minArea = 2
    low_level_min_size = 500
    ##########################################################################

    out_img_list = []
    out_name_list = []

    ###################
    # PRE_PROCESSING
    ###################
    # intenisty normalization (min/max)
    struct_img = np.reciprocal(struct_img) # inverting to detect dark spot
    struct_img = intensity_normalization(struct_img, scaling_param=intensity_norm_param)

    out_img_list.append(struct_img.copy())
    out_name_list.append('im_norm')

    # rescale if needed
    # if rescale_ratio>0:
    #     struct_img = resize(struct_img, [1, rescale_ratio, rescale_ratio], method="cubic")
    #     struct_img = (struct_img - struct_img.min() + 1e-8)/(struct_img.max() - struct_img.min() + 1e-8)
    #     gaussian_smoothing_truncate_range = gaussian_smoothing_truncate_range * rescale_ratio

    # smoothing with gaussian filter
    structure_img_smooth = image_smoothing_gaussian_3d(struct_img, sigma=gaussian_smoothing_sigma, truncate_range=gaussian_smoothing_truncate_range)

    out_img_list.append(structure_img_smooth.copy())
    out_name_list.append('im_smooth')

    ###################
    # core algorithm
    ###################

    # step 1: low level thresholding
    # global_median_1 = np.percentile(structure_img_smooth,35)
    global_median_2 = np.percentile(structure_img_smooth,40) # 70 for M6M7, 30 for rest

    # th_low_level_1 = global_median_1
    th_low_level_2 = global_median_2
    # bw_low_level = (structure_img_smooth > th_low_level_1) + (structure_img_smooth > th_low_level_2)
    bw_low_level = structure_img_smooth > th_low_level_2
    bw_low_level = remove_small_objects(bw_low_level, min_size=low_level_min_size, connectivity=1, in_place=True)
    seg = dilation(bw_low_level, selem=ball(2))

    seg = np.invert(seg)
    seg = seg.astype(np.uint8)
    seg[seg>0]=255

    ####################
    # POST-Processing using other segmentations structures
    ####################

    other_segs_path = "/allen/aics/assay-dev/computational/data/Nucleus_structure_segmentation/fibrillarin_segmentation_improvement/M3/segmentations/"
    mem_segs_path = other_segs_path + fn + "_mem_segmentation.tiff"
    dna_segs_path = other_segs_path + fn + "_dna_segmentation.tiff"

    if not os.path.exists(mem_segs_path):
        mem_segs_path = other_segs_path + fn + ".ome_mem_segmentation.tiff"
        dna_segs_path = other_segs_path + fn + ".ome_dna_segmentation.tiff"
    # pdb.set_trace()
    mito_seed_path_root = "/allen/aics/assay-dev/computational/data/Nucleus_structure_segmentation/fibrillarin_segmentation_improvement/M3/mito_seg/"
    mito_seed_path = mito_seed_path_root + fn + "_mem_segmentation.tif"

    # Generate seed for mitotic cell
    # if not os.path.exists(mito_seed_path):
    #     mito_seed_path = mito_seed_path_root + fn + ".ome.tiff"
    mito_seed_3d = imread(mito_seed_path)

    if np.ndim(mito_seed_3d) == 4:
        mito_seed_3d = mito_seed_3d[:,:,:,0]
    mito_seed_img = np.max(mito_seed_3d, axis=0)
    mito_seed = com(mito_seed_img)

    # label the segmentations 
    # mem_label, num_feat_mem = labeling(imread(mem_segs_path)) # not labeling correctly
    dna_label, num_feat_dna = labeling(imread(dna_segs_path))

    # label 
    # label_mito = mem_label[int(np.floor(mem_label.shape[0]/2)),int(mito_seed[0]),int(mito_seed[1])]

    # seg = seg * ((mem_label == label_mito)*1)
    seg[mito_seed_3d == 0] = 0
    seg = dilation(seg, selem=ball(2))
    seg = seg.astype(np.uint8)
    seg[seg>0]=255
    seg[dna_label > 0] = 0

    

    out_img_list.append(seg.copy())
    out_name_list.append('bw_fine')

    fn += "_combined"

    if output_type == 'default':
        # the default final output
        save_segmentation(seg, False, output_path, fn)
    elif output_type == 'AICS_pipeline':
        # pre-defined output function for pipeline data
        save_segmentation(seg, True, output_path, fn)
    elif output_type == 'customize':
        # the hook for passing in a customized output function
        output_fun(out_img_list, out_name_list, output_path, fn)
    else:
        # the hook for pre-defined RnD output functions (AICS internal)
        img_list, name_list = NPM1_output(out_img_list, out_name_list, output_type, output_path, fn)
        if output_type == 'QCB':
            return img_list, name_list
