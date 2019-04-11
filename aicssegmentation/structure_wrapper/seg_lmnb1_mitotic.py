import numpy as np

# package for io 
from aicsimageio import AICSImage, omeTifWriter                            

# function for core algorithm
from aicssegmentation.core.vessel import filament_2d_wrapper
from aicssegmentation.core.pre_processing_utils import intensity_normalization, image_smoothing_gaussian_3d
from aicssegmentation.core.utils import get_middle_frame, hole_filling, get_3dseed_from_mid_frame
from skimage.morphology import remove_small_objects, watershed, dilation, ball
from skimage.segmentation import find_boundaries
from aicssegmentation.core.output_utils import save_segmentation
from aicsimageprocessing import resize


def Workflow_lmnb1_mitotic(struct_img,rescale_ratio, output_type, output_path, fn, output_func=None):
    ##########################################################################
    # PARAMETERS:
    #   note that these parameters are supposed to be fixed for the structure
    #   and work well accross different datasets

    intensity_norm_param = [4000]
    gaussian_smoothing_sigma = 1
    gaussian_smoothing_truncate_range = 3.0
    f2_param = [[0.5, 0.01]]
    minArea = 5
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

    # smoothing with boundary preserving smoothing
    structure_img_smooth = image_smoothing_gaussian_3d(struct_img, sigma=gaussian_smoothing_sigma, truncate_range=gaussian_smoothing_truncate_range)

    out_img_list.append(structure_img_smooth.copy())
    out_name_list.append('im_smooth')

    ###################
    # core algorithm
    ###################

    # 2d filament filter on the middle frame 
    bw = filament_2d_wrapper(structure_img_smooth, f2_param)
    
    ###################
    # POST-PROCESSING
    ###################
    bw = remove_small_objects(bw>0, min_size=minArea, connectivity=1, in_place=False)

    # output
    seg = bw>0
    seg = seg.astype(np.uint8)
    seg[seg>0]=255

    out_img_list.append(seg.copy())
    out_name_list.append('bw_final')

    if output_type == 'default': 
        # the default final output
        save_segmentation(seg, False, output_path, fn)
    else:
        print('your can implement your output hook here, but not yet')
        quit()