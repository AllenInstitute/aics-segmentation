import numpy as np
import os
from skimage.morphology import remove_small_objects, erosion, ball, dilation
from ..pre_processing_utils import intensity_normalization, image_smoothing_gaussian_3d
from ..core.seg_dot import dot_3d
from skimage.measure import label
from skimage.filters import threshold_triangle, threshold_otsu
from aicssegmentation.core.utils import morphology_preserving_thinning

def ST6GAL1_HiPSC_Pipeline(struct_img,rescale_ratio):
    ##########################################################################
    # PARAMETERS:
    #   note that these parameters are supposed to be fixed for the structure
    #   and work well accross different datasets
    
    intensity_norm_param = [9, 19] 
    gaussian_smoothing_sigma = 1
    gaussian_smoothing_truncate_range = 3.0
    cell_wise_min_area = 1200
    dot_3d_sigma = 1.6
    dot_3d_cutoff = 0.04
    minArea = 10
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

    bw_high_level = morphology_preserving_thinning(bw_high_level, 1.6, 1)

    # LOG 3d to capture spots
    response = dot_3d(structure_img_smooth, log_sigma=dot_3d_sigma)
    bw_extra = response > dot_3d_cutoff

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

def ST6GAL1(img, drug_type):

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
    thresh_3d = 0.016
    minArea = 15
    dynamic_range = 20
    log_sigma = 2
    ##########################################################################

    max_range = min(np.max(struct_img), np.median(struct_img) + dynamic_range*np.std(struct_img))
    struct_img[struct_img>max_range] = max_range
    struct_img = (struct_img - struct_img.min() + 1e-8)/(max_range - struct_img.min() + 1e-8)

    struct_img = ndi.gaussian_filter(struct_img, sigma=1, mode='nearest', truncate=3.0)

    response = -1*(log_sigma**2)*ndi.filters.gaussian_laplace(struct_img, log_sigma)
    bw =response>thresh_3d

    bw = remove_small_objects(bw>0, min_size=minArea, connectivity=1, in_place=False)
    return bw

def Brefeldin(struct_img):
    ##########################################################################
    # PARAMETERS:
    #   note that these parameters are supposed to be fixed for the structure
    #   and work well accross different datasets
    thresh_log = 0.05
    minArea = 6
    dynamic_range = 20
    log_sigma = 3
    ##########################################################################

    max_range = min(np.max(struct_img), np.median(struct_img) + dynamic_range*np.std(struct_img))
    struct_img[struct_img>max_range] = max_range
    struct_img = (struct_img - struct_img.min() + 1e-8)/(max_range - struct_img.min() + 1e-8)

    bw2d = np.zeros_like(struct_img)
    for zi in range(struct_img.shape[0]):
        response = -1*(log_sigma**2)*ndi.filters.gaussian_laplace(ndi.gaussian_filter(struct_img[zi,:,:],sigma=1, mode='nearest', truncate=3.0), log_sigma)
        bw2d[zi,:,:]=response>thresh_log

    bw = remove_small_objects(bw2d>0, min_size=minArea, connectivity=1, in_place=False)

    return bw 

def Paclitaxol(struct_img):
    bw = Vehicle(struct_img)

    return bw 

def Staurosporine(struct_img):
    bw = Vehicle(struct_img)

    return bw 

def Blebbistatin(struct_img):
    ##########################################################################
    # PARAMETERS:
    #   note that these parameters are supposed to be fixed for the structure
    #   and work well accross different datasets
    thresh_3d = 0.03
    minArea = 10
    dynamic_range = 20
    log_sigma = 3
    log_th = 0.1
    ##########################################################################

    max_range = min(np.max(struct_img), np.median(struct_img) + dynamic_range*np.std(struct_img))
    struct_img[struct_img>max_range] = max_range
    struct_img = (struct_img - struct_img.min() + 1e-8)/(max_range - struct_img.min() + 1e-8)
    
    struct_img = ndi.gaussian_filter(struct_img, sigma=1, mode='nearest', truncate=3.0)
    mip= np.amax(struct_img,axis=0)

    bw2d = np.zeros_like(struct_img)
    for zi in range(struct_img.shape[0]):
        tmp = np.concatenate((struct_img[zi,:,:],mip),axis=1)
        tmp_ves = vesselness2D(tmp, scale_range=(1,4), scale_step=1, tau=1, whiteonblack=True)
        bw2d[zi,:,:struct_img.shape[2]-2]=tmp_ves[:,:struct_img.shape[2]-2]>thresh_3d

        response = -1*(log_sigma**2)*ndi.filters.gaussian_laplace(struct_img[zi,:,:], log_sigma)
        bw2d[zi,:,:] = np.logical_or(bw2d[zi,:,:], response>log_th)

    # thresholding the response
    bw = remove_small_objects(bw2d>0, min_size=minArea, connectivity=1, in_place=False)

    return bw 
    

def Rapamycin(struct_img):
    bw = Vehicle(struct_img)

    return bw