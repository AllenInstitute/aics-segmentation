###### import functions ####
import numpy as np
import os
from skimage.morphology import remove_small_objects, watershed, dilation, ball
from ..core.pre_processing_utils import intensity_normalization, image_smoothing_gaussian_3d
from ..core.seg_dot import dot_slice_by_slice, dot_2d_slice_by_slice_wrapper
from skimage.filters import threshold_triangle, threshold_otsu
from skimage.measure import label
from aicsimageprocessing import resize

#### do not remove ####
from aicssegmentation.core.output_utils import  save_segmentation, generate_segmentation_contour

def Workflow_fbl_labelfree_4dn(struct_img, rescale_ratio, output_type, output_path, fn, output_func=None):
    ##########################################################################
    # PARAMETERS:
    minArea = 5
    low_level_min_size = 7000
    s2_param  = [[0.5, 0.1]]
    intensity_scaling_param = [0.5, 19.5]
    gaussian_smoothing_sigma = 1

    ##########################################################################

    ###################
    # PRE_PROCESSING 
    ###################
    # intenisty normalization 
    struct_norm = intensity_normalization(struct_img, scaling_param=intensity_scaling_param)

    # smoothing 
    struct_smooth = image_smoothing_gaussian_3d(struct_norm, sigma=gaussian_smoothing_sigma)

    ###################
    # core algorithm
    ###################
    # step 1: low level thresholding
    #global_otsu = threshold_otsu(structure_img_smooth)
    global_tri = threshold_triangle(struct_smooth)
    global_median = np.percentile(struct_smooth,50)

    th_low_level = (global_tri + global_median)/2
    bw_low_level = struct_smooth > th_low_level
    bw_low_level = remove_small_objects(bw_low_level, min_size=low_level_min_size, connectivity=1, in_place=True)

    # step 2: high level thresholding
    bw_high_level = np.zeros_like(bw_low_level)
    lab_low, num_obj = label(bw_low_level, return_num=True, connectivity=1)
    for idx in range(num_obj):
        single_obj = (lab_low==(idx+1))
        local_otsu = threshold_otsu(struct_smooth[single_obj])
        bw_high_level[np.logical_and(struct_smooth>local_otsu*1.2, single_obj)]=1

    # step 3: finer segmentation
    response2d = dot_2d_slice_by_slice_wrapper(struct_smooth, s2_param)
    bw_finer = remove_small_objects(response2d, min_size=minArea, connectivity=1, in_place=True)

    # merge finer level detection into high level coarse segmentation to include outside dim parts
    bw_high_level[bw_finer>0]=1

    ###################
    # POST-PROCESSING 
    # make sure the variable name of final segmentation is 'seg'
    ###################
    seg = remove_small_objects(bw_high_level, min_size=minArea, connectivity=1, in_place=True)

    # output
    seg = seg>0
    seg = seg.astype(np.uint8)
    seg[seg>0]=255

    if output_type == 'default': 
        # the default final output
        save_segmentation(seg, False, output_path, fn)
    elif output_type == 'array':
        return seg
    elif output_type == 'array_with_contour':
        return (seg, generate_segmentation_contour(seg))
    else:
        print('your can implement your output hook here, but not yet')
        quit()



