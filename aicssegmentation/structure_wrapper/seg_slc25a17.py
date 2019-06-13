import numpy as np
import os
from skimage.morphology import remove_small_objects, watershed, dilation, ball
from ..core.pre_processing_utils import intensity_normalization, image_smoothing_gaussian_slice_by_slice
from ..core.seg_dot import dot_3d
from skimage.feature import peak_local_max
from scipy.ndimage import distance_transform_edt
from skimage.measure import label
from aicssegmentation.core.output_utils import save_segmentation, SLC25A17_output
from aicsimageprocessing import resize


def Workflow_slc25a17(struct_img,rescale_ratio, output_type, output_path, fn, output_func=None):
    ##########################################################################
    # PARAMETERS:
    #   note that these parameters are supposed to be fixed for the structure
    #   and work well accross different datasets

    intensity_norm_param = [2, 36]
    gaussian_smoothing_sigma = 1
    gaussian_smoothing_truncate_range = 3.0
    dot_3d_sigma = 1
    dot_3d_cutoff = 0.045 #0.03 #0.04
    minArea = 3 #5
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

    # smoothing with gaussian filter
    structure_img_smooth = image_smoothing_gaussian_slice_by_slice(struct_img, sigma=gaussian_smoothing_sigma, truncate_range=gaussian_smoothing_truncate_range)

    out_img_list.append(structure_img_smooth.copy())
    out_name_list.append('im_smooth')

    ###################
    # core algorithm
    ###################

    # step 1: LOG 3d 
    response = dot_3d(structure_img_smooth, log_sigma=dot_3d_sigma)
    bw = response > dot_3d_cutoff

    bw = remove_small_objects(bw>0, min_size=minArea, connectivity=1, in_place=False)

    out_img_list.append(bw.copy())
    out_name_list.append('interm_mask')

    # step 2: 'local_maxi + watershed' for cell cutting
    local_maxi = peak_local_max(struct_img,labels=label(bw), min_distance=2, indices=False)

    out_img_list.append(local_maxi.copy())
    out_name_list.append('interm_local_max')

    distance = distance_transform_edt(bw)
    im_watershed = watershed(-1*distance, label(dilation(local_maxi, selem=ball(1))), mask=bw, watershed_line=True)

    ###################
    # POST-PROCESSING
    ###################
    seg = remove_small_objects(im_watershed, min_size=minArea, connectivity=1, in_place=False)

    ###### HACK: Only for 2019 April Release #####
    if np.count_nonzero(seg>0)<50000:
        print('FLAG: please check the meta data of the original CZI for QC')
        
    # output
    seg = seg>0
    seg = seg.astype(np.uint8)
    seg[seg>0]=255

    out_img_list.append(seg.copy())
    out_name_list.append('bw_final')

    if output_type == 'default': 
        # the default final output
        save_segmentation(seg, False, output_path, fn)
    elif output_type == 'AICS_pipeline':
        # pre-defined output function for pipeline data
        save_segmentation(seg, True, output_path, fn)
    elif output_type == 'customize':
        # the hook for passing in a customized output function
        #output_fun(out_img_list, out_name_list, output_path, fn)
        print('please provide custom output function')
    else:
        # the hook for pre-defined RnD output functions (AICS internal)
        img_list, name_list = SLC25A17_output(out_img_list, out_name_list, output_type, output_path, fn)
        if output_type == 'QCB':
            return img_list, name_list
