import numpy as np
import os
from skimage.morphology import remove_small_objects
from ..pre_processing_utils import intensity_normalization, image_smoothing_gaussian_slice_by_slice
from ..core.seg_dot import dot_3d, dot_slice_by_slice
from skimage.measure import label
import math
import numba as nb 

@nb.njit
def replace_where(arr, needle, replace):
    arr = arr.ravel()
    needles = set(needle)
    for idx in range(arr.size):
        if arr[idx] in needles:
            arr[idx] = replace

def GJA1_HiPSC_Pipeline(struct_img,rescale_ratio):
    ##########################################################################
    # PARAMETERS:
    #   note that these parameters are supposed to be fixed for the structure
    #   and work well accross different datasets

    intensity_norm_param = [1, 40]
    gaussian_smoothing_sigma = 1
    gaussian_smoothing_truncate_range = 3.0
    dot_3d_sigma = 1
    dot_3d_cutoff = 0.031 # 0.025
    dot_2d_cutoff = 0.0175
    minArea = 5
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
    structure_img_smooth = image_smoothing_gaussian_slice_by_slice(struct_img, sigma=gaussian_smoothing_sigma, truncate_range=gaussian_smoothing_truncate_range)

    ###################
    # core algorithm
    ###################

    # step 1: LOG 3d 
    response = dot_3d(structure_img_smooth, log_sigma=dot_3d_sigma)
    bw = response > dot_3d_cutoff
    bw = remove_small_objects(bw>0, min_size=minArea, connectivity=1, in_place=False)
    '''
    response2d = dot_slice_by_slice(structure_img_smooth, log_sigma=dot_3d_sigma)
    bw2d = response2d > dot_2d_cutoff

    for zz in range(bw.shape[0]):
        bw_tmp = bw[zz,:,:]
        if np.any(bw_tmp):
            lab_tmp, num_tmp = label(bw_tmp, return_num=True, connectivity=2)
            ids = lab_tmp[bw2d[zz,:,:]]
            
            s1 = np.unique(ids)
            s2 = np.arange(1,num_tmp+1)
            s0 = np.setdiff1d(s2,s1)
            replace_where(lab_tmp, s0, 0)
            
            bw[zz,:,:] = lab_tmp>0
    '''
    
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

def Connexin_drug(img, drug_type):

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

'''@nb.njit
def replace_where(arr, needle, replace):
    arr = arr.ravel()
    needles = set(needle)
    for idx in range(arr.size):
        if arr[idx] in needles:
            arr[idx] = replace

def Connexin_HiPSC_Pipeline(struct_img,rescale_ratio):
    ##########################################################################
    # PARAMETERS:
    #   note that these parameters are supposed to be fixed for the structure
    #   and work well accross different datasets
    dynamic_range = 50
    log_sigma = 1 # 1.5
    log_th = 0.0125 #0.03
    min_size = 4
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

    # basic filter
    filter_out = -1*(log_sigma**2)*ndi.filters.gaussian_laplace(img_smooth, log_sigma)
    bw_basic = remove_small_objects(filter_out > log_th, min_size=2*min_size, connectivity=3, in_place=True)

    for zz in range(bw_basic.shape[0]):
        bw_tmp = bw_basic[zz,:,:]
        if np.any(bw_tmp):
            lab_tmp, num_tmp = label(bw_tmp, return_num=True, connectivity=2)
            out_2ds = -1*(log_sigma**2)*ndi.filters.gaussian_laplace(ndi.gaussian_filter(struct_img[zz,:,:], sigma=1, mode='nearest', truncate=3.0) , log_sigma)
            bw_2ds = out_2ds>0.01
            ids = lab_tmp[bw_2ds]
            
            s1 = np.unique(ids)
            s2 = np.arange(1,num_tmp+1)
            s0 = np.setdiff1d(s2,s1)
            replace_where(lab_tmp, s0, 0)
            
            bw_basic[zz,:,:] = lab_tmp>0

    bw_final = bw_basic

  
    if rescale_ratio>0:
        bw_final = processing.resize(bw_final, [1, 1/rescale_ratio, 1/rescale_ratio], method="nearest")

    bw_final = bw_final.astype(np.uint8)
    bw_final[bw_final>0.5]=255

    return bw_final

'''