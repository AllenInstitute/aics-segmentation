import numpy as np
import os
from ..core.vessel import vesselnessSliceBySlice
from ..pre_processing_utils import intensity_normalization, boundary_preserving_smoothing_3d
from scipy import ndimage as ndi
from skimage.morphology import remove_small_objects

def SEC61B_HiPSC_Pipeline(struct_img,rescale_ratio):
    ##########################################################################
    # PARAMETERS:
    #   note that these parameters are supposed to be fixed for the structure
    #   and work well accross different datasets

    intensity_norm_param = [2.5, 7.5]
    vesselness_sigma = [1]
    vesselness_cutoff = 0.15
    minArea = 15
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

    # smoothing with boundary preserving smoothing
    structure_img_smooth = boundary_preserving_smoothing_3d(struct_img)

    ###################
    # core algorithm
    ###################

    # 2d vesselness slice by slice
    response = vesselnessSliceBySlice(structure_img_smooth, sigmas=vesselness_sigma,  tau=1, whiteonblack=True)
    bw = response > vesselness_cutoff
    
    ###################
    # POST-PROCESSING
    ###################
    bw = remove_small_objects(bw>0, min_size=minArea, connectivity=1, in_place=False)
    for zz in range(bw.shape[0]):
        bw[zz,:,:] = remove_small_objects(bw[zz,:,:], min_size=3, connectivity=1, in_place=False)

    seg = remove_small_objects(bw>0, min_size=minArea, connectivity=1, in_place=False)

    # output
    seg = seg>0
    seg = seg.astype(np.uint8)
    seg[seg>0]=255

    return seg

