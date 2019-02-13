import numpy as np
import os
from skimage.morphology import remove_small_objects, erosion, ball, dilation
from ..core.pre_processing_utils import intensity_normalization, image_smoothing_gaussian_3d
from ..core.seg_dot import dot_3d
from skimage.measure import label
from skimage.filters import threshold_triangle, threshold_otsu
from aicssegmentation.core.utils import topology_preserving_thinning
from aicssegmentation.core.output_utils import save_segmentation, ST6GAL1_output
from aicsimageprocessing import resize

def ST6GAL1_HiPSC_Pipeline(struct_img,rescale_ratio, output_type, output_path, fn, output_func=None):
    ##########################################################################
    # PARAMETERS:
    #   note that these parameters are supposed to be fixed for the structure
    #   and work well accross different datasets

    intensity_norm_param = [9, 19]
    gaussian_smoothing_sigma = 1
    gaussian_smoothing_truncate_range = 3.0
    cell_wise_min_area = 1200
    dot_3d_sigma = 1.6
    dot_3d_cutoff = 0.02
    minArea = 10
    thin_dist = 1
    thin_dist_preserve = 1.6
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

    # cell-wise local adaptive thresholding
    th_low_level = threshold_triangle(structure_img_smooth)

    bw_low_level = structure_img_smooth > th_low_level
    bw_low_level = remove_small_objects(bw_low_level, min_size=cell_wise_min_area, connectivity=1, in_place=True)
    bw_low_level = dilation(bw_low_level,selem=ball(2))

    bw_high_level = np.zeros_like(bw_low_level)
    lab_low, num_obj = label(bw_low_level, return_num=True, connectivity=1)

    for idx in range(num_obj):
        single_obj = lab_low==(idx+1)
        local_otsu = threshold_otsu(structure_img_smooth[single_obj>0])
        bw_high_level[np.logical_and(structure_img_smooth>local_otsu*0.98, single_obj)]=1

    # LOG 3d to capture spots
    response = dot_3d(structure_img_smooth, log_sigma=dot_3d_sigma)
    bw_extra = response > dot_3d_cutoff

    # thinning
    bw_high_level = topology_preserving_thinning(bw_high_level, thin_dist_preserve, thin_dist)

    # combine the two parts
    bw = np.logical_or(bw_high_level, bw_extra)

    ###################
    # POST-PROCESSING
    ###################
    seg = remove_small_objects(bw>0, min_size=minArea, connectivity=1, in_place=False)

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
        output_fun(out_img_list, out_name_list, output_path, fn)
    else:
        # the hook for pre-defined RnD output functions (AICS internal)
        img_list, name_list = ST6GAL1_output(out_img_list, out_name_list, output_type, output_path, fn)
        if output_type == 'QCB':
            return img_list, name_list
