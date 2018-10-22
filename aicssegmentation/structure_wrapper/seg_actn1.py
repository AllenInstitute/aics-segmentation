import numpy as np
import os
from skimage.morphology import remove_small_objects
from ..pre_processing_utils import intensity_normalization, image_smoothing_gaussian_3d
from ..core.vessel import vesselness3D


def ACTN1_HiPSC_Pipeline(struct_img,rescale_ratio):
    ##########################################################################
    # PARAMETERS:
    #   note that these parameters are supposed to be fixed for the structure
    #   and work well accross different datasets

    intensity_norm_param = [3, 15]  
    gaussian_smoothing_sigma = 1
    gaussian_smoothing_truncate_range = 3.0
    vesselness_sigma_1 = [1]
    vesselness_cutoff_1 = 0.2
    vesselness_sigma_2 = [0.25]
    vesselness_cutoff_2 = 0.05
    minArea = 5
    ##########################################################################

    ###################
    # PRE_PROCESSING
    ###################
    # intenisty normalization 
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

    # vesselness 3d 
    response_1 = vesselness3D(structure_img_smooth, sigmas=vesselness_sigma_1,  tau=1, whiteonblack=True)
    response_2 = vesselness3D(structure_img_smooth, sigmas=vesselness_sigma_2,  tau=1, whiteonblack=True)
    bw = np.logical_or(response_1 > vesselness_cutoff_1, response_2 > vesselness_cutoff_2) 
    
    ###################
    # POST-PROCESSING
    ###################
    seg = remove_small_objects(bw, min_size=minArea, connectivity=1, in_place=False)

    # output
    seg = seg>0
    seg = seg.astype(np.uint8)
    seg[seg>0]=255

    return seg


'''
drug:
0: vehicle
1: Brefeldin
2: Paclitaxol
3: Staurosporine
4: s-Nitro-Blebbistatin
5: Rapamycin
'''

def ACTN1_drug(img, drug_type):

    if drug_type==0:
        bw = Vehicle(img)
    elif drug_type==1:
        bw = Brefeldin(img)
    elif drug_type==2:
        bw = Paclitaxol(img)
    elif drug_type==3:
        bw = Staurosporine(img)
    elif drug_type==4:
        bw = Blebbistatin(img)
    elif drug_type==5:
        bw = Rapamycin(img)
    else:
        print('unsupported drug type')
        bw = None

    return bw 


def Vehicle(struct_img):
    ##########################################################################
    # PARAMETERS:
    #   note that these parameters are supposed to be fixed for the structure
    #   and work well accross different datasets
    thresh_3d = 0.1
    minArea = 5
    dynamic_range = 7
    ##########################################################################

    return bw 

def Brefeldin(struct_img):
    ##########################################################################
    # PARAMETERS:
    #   note that these parameters are supposed to be fixed for the structure
    #   and work well accross different datasets
    thresh_3d = 0.1
    minArea = 5
    dynamic_range = 7
    ##########################################################################

    return bw 

def Paclitaxol(struct_img):
    ##########################################################################
    # PARAMETERS:
    #   note that these parameters are supposed to be fixed for the structure
    #   and work well accross different datasets
    thresh_3d = 0.1
    minArea = 5
    dynamic_range = 7
    ##########################################################################

    return bw 

    
def Staurosporine(struct_img):
    ##########################################################################
    # PARAMETERS:
    #   note that these parameters are supposed to be fixed for the structure
    #   and work well accross different datasets
    thresh_3d = 0.1
    minArea = 5
    dynamic_range = 7
    ##########################################################################

    return bw 

def Blebbistatin(struct_img):
    ##########################################################################
    # PARAMETERS:
    #   note that these parameters are supposed to be fixed for the structure
    #   and work well accross different datasets
    thresh_3d = 0.1
    minArea = 5
    dynamic_range = 7
    ##########################################################################

    return bw 

def Rapamycin(struct_img):
    ##########################################################################
    # PARAMETERS:
    #   note that these parameters are supposed to be fixed for the structure
    #   and work well accross different datasets
    thresh_3d = 0.1
    minArea = 5
    dynamic_range = 7
    ##########################################################################

    return bw 


'''
def ACTN1_HiPSC_Pipeline(struct_img,rescale_ratio):
    ##########################################################################
    # PARAMETERS:
    #   note that these parameters are supposed to be fixed for the structure
    #   and work well accross different datasets
    thresh_3d = 0.05 #0.04
    minArea = 12
    dynamic_range = 10
    ##########################################################################

    # intenisty normalization (min/max)
    max_range = min(np.max(struct_img), np.median(struct_img) + dynamic_range*np.std(struct_img))
    struct_img[struct_img>max_range] = max_range
    struct_img = (struct_img - struct_img.min() + 1e-8)/(max_range - struct_img.min() + 1e-8)
    
    # rescale if needed
    
    if rescale_ratio>0:
        struct_img = processing.resize(struct_img, [1, rescale_ratio, rescale_ratio], method="cubic")
        struct_img = (struct_img - struct_img.min() + 1e-8)/(struct_img.max() - struct_img.min() + 1e-8)
        img_smooth = ndi.gaussian_filter(struct_img, sigma=1, mode='nearest', truncate=3.0*rescale_ratio)
    else:
        img_smooth = ndi.gaussian_filter(struct_img, sigma=1, mode='nearest', truncate=3.0)

    response = vesselness3D(img_smooth, scale_range=(1,3), scale_step=1,  tau=1, whiteonblack=True)
    # range = (1,3) --> sigma = 1, 2 (3 is not included)

    # thresholding the response
    bw = response>thresh_3d
    bw = remove_small_objects(bw, min_size=minArea, connectivity=3, in_place=False)

    for zz in range(bw.shape[0]):
        tmp = bw[zz,:,:]
        tmp = remove_small_objects(tmp, min_size=minArea//2, connectivity=2)
        bw[zz,:,:] = tmp

    if rescale_ratio>0:
        bw = processing.resize(bw, [1, 1/rescale_ratio, 1/rescale_ratio], method="nearest")
        #bw_high_level = processing.resize(bw_high_level, [1, 1/rescale_ratio, 1/rescale_ratio], method="nearest")

    bw = bw.astype(np.uint8)
    bw[bw>0]=255

    return bw
'''


