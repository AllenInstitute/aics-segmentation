# import
import numpy as np
import os
import sys
import glob
import pathlib

from aicssegmentation.core.vessel import vesselnessSliceBySlice, vesselness3D
from aicssegmentation.core.seg_dot import dot_slice_by_slice, dot_3d
from aicssegmentation.core.pre_processing_utils import intensity_normalization, edge_preserving_smoothing_3d
from scipy import ndimage as ndi
from skimage.morphology import remove_small_objects
from aicsimageprocessing import resize
from aicsimageio import AICSImage
from skimage.io import imsave
from argparse import ArgumentParser
from aicssegmentation.core.output_utils import save_segmentation, generate_segmentation_contour


def Workflow_son(struct_img, rescale_ratio, output_type, output_path, fn, output_func=None):
    ##########################################################################
    # PARAMETERS:
    #   note that these parameters are supposed to be fixed for the structure
    #   and work well accross different datasets
    ##########################################################################

    intensity_norm_param = [2, 30]
    vesselness_sigma = [1.2]
    vesselness_cutoff = 0.15
    minArea = 15

    dot_2d_sigma = 1
    dot_3d_sigma = 1.15
    ##########################################################################

    ###################
    # PRE_PROCESSING
    ###################
    # intenisty normalization (min/max)
    struct_img = intensity_normalization(struct_img, scaling_param=intensity_norm_param)

    # smoothing with boundary preserving smoothing
    structure_img_smooth = edge_preserving_smoothing_3d(struct_img)

    ###################
    # core algorithm
    ###################
    response_f3 = vesselness3D(structure_img_smooth, sigmas=vesselness_sigma,  tau=1, whiteonblack=True)
    response_f3 = response_f3 > vesselness_cutoff

    response_s3_1 = dot_3d(structure_img_smooth, log_sigma=dot_3d_sigma)
    response_s3_3 = dot_3d(structure_img_smooth, log_sigma=3)

    bw_small_inverse = remove_small_objects(response_s3_1>0.03, min_size=150)
    bw_small = np.logical_xor(bw_small_inverse, response_s3_1>0.02)

    bw_medium = np.logical_or(bw_small, response_s3_1>0.07)
    bw_large = np.logical_or(response_s3_3>0.2, response_f3>0.25)
    bw = np.logical_or( np.logical_or(bw_small, bw_medium), bw_large)

    ###################
    # POST-PROCESSING
    ###################
    bw = remove_small_objects(bw>0, min_size=minArea, connectivity=1, in_place=False)
    for zz in range(bw.shape[0]):
        bw[zz,: , :] = remove_small_objects(bw[zz,:,:], min_size=3, connectivity=1, in_place=False)

    seg = remove_small_objects(bw>0, min_size=minArea, connectivity=1, in_place=False)

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
