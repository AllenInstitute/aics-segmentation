import numpy as np
import os
from skimage.morphology import remove_small_objects
from skimage.measure import label
from ..core.vessel import vesselnessSliceBySlice
from ..core.seg_dot import dot_slice_by_slice
from ..core.pre_processing_utils import intensity_normalization, image_smoothing_gaussian_slice_by_slice
from aicssegmentation.core.output_utils import save_segmentation, LAMP1_output
from aicsimageprocessing import resize


def LAMP1_HiPSC_Pipeline(struct_img,rescale_ratio, output_type, output_path, fn, output_func=None):
    ##########################################################################
    # PARAMETERS:
    #   note that these parameters are supposed to be fixed for the structure
    #   and work well accross different datasets
    intensity_scaling_param = [3, 19]
    gaussian_smoothing_sigma = 1
    gaussian_smoothing_truncate_range = 3.0

    minArea = 15
    ves_th_2d =0.1

    vesselness_sigma = [1]
    vesselness_cutoff = 0.15

    #hole_min = 60
    hole_max = 1600

    log_sigma_1 = 5
    log_cutoff_1 = 0.09
    log_sigma_2 = 2.5
    log_cutoff_2 = 0.07
    log_sigma_3 = 1
    log_cutoff_3 = 0.01
    ##########################################################################

    out_img_list = []
    out_name_list = []

    # intenisty normalization
    struct_img = intensity_normalization(struct_img, scaling_param=intensity_scaling_param)

    out_img_list.append(struct_img.copy())
    out_name_list.append('im_norm')

    if rescale_ratio>0:
        struct_img = resize(struct_img, [1, rescale_ratio, rescale_ratio], method="cubic")
        struct_img = (struct_img - struct_img.min() + 1e-8)/(struct_img.max() - struct_img.min() + 1e-8)
        gaussian_smoothing_truncate_range = gaussian_smoothing_truncate_range * rescale_ratio

    structure_img_smooth = image_smoothing_gaussian_slice_by_slice(struct_img, sigma=gaussian_smoothing_sigma, truncate_range=gaussian_smoothing_truncate_range)

    out_img_list.append(structure_img_smooth.copy())
    out_name_list.append('im_smooth')

    # spot detection
    response1 = dot_slice_by_slice(structure_img_smooth, log_sigma=log_sigma_1)
    bw1 = response1> log_cutoff_1
    response2 = dot_slice_by_slice(structure_img_smooth, log_sigma=log_sigma_2)
    bw2 = response2> log_cutoff_2
    bw_spot = np.logical_or(bw1, bw2)
    response3 = dot_slice_by_slice(structure_img_smooth, log_sigma=log_sigma_3)
    bw3 = response3> log_cutoff_3
    bw_spot = np.logical_or(bw_spot, bw3)

    # ring/filament detection
    ves = vesselnessSliceBySlice(structure_img_smooth, sigmas=vesselness_sigma,  tau=1, whiteonblack=True)
    bw_ves = ves> vesselness_cutoff

    # fill holes
    partial_fill = np.logical_or(bw_spot, bw_ves)

    out_img_list.append(partial_fill.copy())
    out_name_list.append('interm_before_hole')

    holes = np.zeros_like(partial_fill)
    for zz in range(partial_fill.shape[0]):
        background_lab = label(~partial_fill[zz,:,:], connectivity=1)

        out = np.copy(background_lab)
        component_sizes = np.bincount(background_lab.ravel())
        too_big = component_sizes >hole_max
        too_big_mask = too_big[background_lab]
        out[too_big_mask] = 0
        #too_small = component_sizes <hole_min
        #too_small_mask = too_small[background_lab]
        #out[too_small_mask] = 0

        holes[zz,:,:] = out

    full_fill = np.logical_or(partial_fill, holes)

    seg = remove_small_objects(full_fill, min_size=minArea, connectivity=1, in_place=False)

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
        img_list, name_list = LAMP1_output(out_img_list, out_name_list, output_type, output_path, fn)
        if output_type == 'QCB':
            return img_list, name_list



