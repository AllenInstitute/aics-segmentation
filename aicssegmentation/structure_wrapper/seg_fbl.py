import numpy as np
import os
from skimage.morphology import remove_small_objects, watershed, dilation, ball
from ..pre_processing_utils import intensity_normalization, image_smoothing_gaussian_3d
from ..core.seg_dot import dot_slice_by_slice
from skimage.filters import threshold_triangle, threshold_otsu
from skimage.measure import label


def FBL_HiPSC_Pipeline(struct_img,rescale_ratio):
    ##########################################################################
    # PARAMETERS:
    #   note that these parameters are supposed to be fixed for the structure
    #   and work well accross different datasets

    intensity_norm_param = [0.5, 18]
    gaussian_smoothing_sigma = 1
    gaussian_smoothing_truncate_range = 3.0
    dot_2d_sigma = 1
    dot_2d_cutoff = 0.01
    minArea = 5
    low_level_min_size = 700
    ##########################################################################

    ###################
    # PRE_PROCESSING
    ###################
    # intenisty normalization (min/max)
    struct_img = intensity_normalization(struct_img, scaling_param=intensity_norm_param)
    
    # rescale if needed
    if rescale_ratio>0:
        struct_img = processing.resize(struct_img, [1, rescale_ratio, rescale_ratio], method="cubic")
        struct_img = (struct_img - struct_img.min() + 1e-8)/(struct_img.max() - struct_img.min() + 1e-8)
        gaussian_smoothing_truncate_range = gaussian_smoothing_truncate_range * rescale_ratio

    # smoothing with gaussian filter
    structure_img_smooth = image_smoothing_gaussian_3d(struct_img, sigma=gaussian_smoothing_sigma, truncate_range=gaussian_smoothing_truncate_range)

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

    # step 2: high level thresholding
    bw_high_level = np.zeros_like(bw_low_level)
    lab_low, num_obj = label(bw_low_level, return_num=True, connectivity=1)
    for idx in range(num_obj):
        single_obj = (lab_low==(idx+1))
        local_otsu = threshold_otsu(structure_img_smooth[single_obj])
        bw_high_level[np.logical_and(structure_img_smooth>local_otsu, single_obj)]=1

    # step 3: finer segmentation
    response2d = dot_slice_by_slice(structure_img_smooth, log_sigma=dot_2d_sigma)
    bw_finer = remove_small_objects(response2d>dot_2d_cutoff, min_size=minArea, connectivity=1, in_place=True)

    # merge finer level detection into high level coarse segmentation to include outside dim parts
    bw_high_level[bw_finer>0]=1

    ###################
    # POST-PROCESSING
    ###################
    seg = remove_small_objects(bw_high_level>0, min_size=minArea, connectivity=1, in_place=False)

    # output
    seg = seg>0
    seg = seg.astype(np.uint8)
    seg[seg>0]=255

    return seg

