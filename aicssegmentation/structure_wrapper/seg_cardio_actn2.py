import numpy as np
import os
from skimage.morphology import remove_small_objects
from ..core.pre_processing_utils import intensity_normalization, edge_preserving_smoothing_3d
from ..core.vessel import vesselness3D
from aicssegmentation.core.output_utils import save_segmentation, ACTN2_Cardio_output

def ACTN2_Cardio_Pipeline(struct_img,rescale_ratio, output_type, output_path, fn, output_func=None):
    ##########################################################################
    # PARAMETERS:
    #   note that these parameters are supposed to be fixed for the structure
    #   and work well accross different datasets

    intensity_norm_param = [1, 19]
    vesselness_sigma = [1]
    vesselness_cutoff = 0.02
    minArea = 15
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
        struct_img = processing.resize(struct_img, [1, rescale_ratio, rescale_ratio], method="cubic")
        struct_img = (struct_img - struct_img.min() + 1e-8)/(struct_img.max() - struct_img.min() + 1e-8)
    
    # smoothing with gaussian filter
    structure_img_smooth = edge_preserving_smoothing_3d(struct_img)  

    out_img_list.append(structure_img_smooth.copy())
    out_name_list.append('im_smooth')

    ###################
    # core algorithm
    ###################

    # vesselness 3d 
    response = vesselness3D(structure_img_smooth, sigmas=vesselness_sigma,  tau=1, whiteonblack=True)
    bw = response > vesselness_cutoff
    
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
        # the hook for other pre-defined RnD output functions (AICS internal)
        ACTN2_Cardio_output(out_img_list, out_name_list, output_type, output_path, fn)


