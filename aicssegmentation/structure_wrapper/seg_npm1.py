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

def NPM1_HiPSC_Pipeline(struct_img,rescale_ratio,output_type, output_path, fn, output_func=None):
    ##########################################################################
    # PARAMETERS:
    #   note that these parameters are supposed to be fixed for the structure
    #   and work well accross different datasets

    intensity_norm_param = [0.5, 15]
    gaussian_smoothing_sigma = 1
    gaussian_smoothing_truncate_range = 3.0
    dot_2d_sigma = 2
    dot_2d_sigma_extra = 1
    dot_2d_cutoff = 0.025
    minArea = 5
    low_level_min_size = 700
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
    structure_img_smooth = image_smoothing_gaussian_3d(struct_img, sigma=gaussian_smoothing_sigma, truncate_range=gaussian_smoothing_truncate_range)

    out_img_list.append(structure_img_smooth.copy())
    out_name_list.append('im_smooth')

    ###################
    # core algorithm
    ###################

    # step 1: low level thresholding
    #global_otsu = threshold_otsu(structure_img_smooth)
    global_tri = threshold_triangle(structure_img_smooth)
    global_median = np.percentile(structure_img_smooth,50)

    th_low_level = (global_tri + global_median)/2
    bw_low_level = structure_img_smooth > th_low_level
    bw_low_level = remove_small_objects(bw_low_level, min_size=low_level_min_size, connectivity=1, in_place=True)
    bw_low_level = dilation(bw_low_level, selem=ball(2))

    # step 2: high level thresholding
    local_cutoff = 0.333 * threshold_otsu(structure_img_smooth)
    bw_high_level = np.zeros_like(bw_low_level)
    lab_low, num_obj = label(bw_low_level, return_num=True, connectivity=1)
    for idx in range(num_obj):
        single_obj = (lab_low==(idx+1))
        local_otsu = threshold_otsu(structure_img_smooth[single_obj])
        if local_otsu > local_cutoff:
            bw_high_level[np.logical_and(structure_img_smooth>0.98*local_otsu, single_obj)]=1

    out_img_list.append(bw_high_level.copy())
    out_name_list.append('bw_coarse')

    response_bright = dot_slice_by_slice(structure_img_smooth, log_sigma=dot_2d_sigma)

    response_dark = dot_slice_by_slice(1 - structure_img_smooth, log_sigma=dot_2d_sigma)
    response_dark_extra = dot_slice_by_slice(1 - structure_img_smooth, log_sigma=dot_2d_sigma_extra)

    #inner_mask = bw_high_level.copy()
    #for zz in range(inner_mask.shape[0]):
    #    inner_mask[zz,:,:] = binary_fill_holes(inner_mask[zz,:,:])

    holes = np.logical_or(response_dark>dot_2d_cutoff , response_dark_extra>dot_2d_cutoff)
    #holes[~inner_mask] = 0

    bw_extra = response_bright>dot_2d_cutoff
    #bw_extra[~bw_high_level]=0
    bw_extra[~bw_low_level]=0

    bw_final = np.logical_or(bw_extra, bw_high_level)
    bw_final[holes]=0

    ###################
    # POST-PROCESSING
    ###################
    seg = remove_small_objects(bw_final, min_size=minArea, connectivity=1, in_place=True)

    # output
    seg = seg>0
    seg = seg.astype(np.uint8)
    seg[seg>0]=255

    out_img_list.append(seg.copy())
    out_name_list.append('bw_fine')

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
