import numpy as np
import os
from argparse import ArgumentParser
from aicsimage import processing, io
from .vessel import vesselness3D, vesselness2D
from scipy import ndimage as ndi
from skimage.morphology import remove_small_objects, dilation, erosion, ball, disk, skeletonize, skeletonize_3d
from .utils import histogram_otsu
from skimage.filters import threshold_triangle, threshold_otsu
from scipy.ndimage.morphology import binary_fill_holes
from skimage.measure import label as cc_label
import math
import numba as nb 

'''
drug:
0: vehicle
1: Brefeldin
2: Paclitaxol
3: Staurosporine
4: s-Nitro-Blebbistatin
5: Rapamycin
'''

def NPM_drug(img, drug_type):

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

@nb.njit
def replace_where(arr, needle, replace):
    arr = arr.ravel()
    needles = set(needle)
    for idx in range(arr.size):
        if arr[idx] in needles:
            arr[idx] = replace

def NPM_HiPSC_Pipeline(struct_img,rescale_ratio):
    ##########################################################################
    # PARAMETERS:
    #   note that these parameters are supposed to be fixed for the structure
    #   and work well accross different datasets
    dynamic_range = 16
    low_level_min_size = 700
    fine_level_min_size = 5
    log_sigma = 2
    log_sigma_extra = 1
    log_th = 0.02
    standard_xy = 0.108
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

    # get different levels of threshold
    global_otsu = threshold_otsu(img_smooth)
    global_tri = threshold_triangle(img_smooth)
    global_median = np.percentile(img_smooth,50)

    th_low_level = (global_tri + global_median)/2

    # low level thresholding
    bw_low_level = img_smooth>th_low_level
    bw_low_level = remove_small_objects(bw_low_level, min_size=low_level_min_size, connectivity=1, in_place=True)

    '''
    # prune the low level bw mask to remove the extra top/bottom caused by PSF
    # criteria: (FRAME-WISE) there must be at least a few, say 10, pixels inside each cc
    # whose intensity is larger than global_otsu
    bw_prune = np.zeros_like(bw_low_level)
    for z_idx in range(img_smooth.shape[0]):
        single_frame = bw_low_level[z_idx,:,:].copy()
        single_frame_raw = img_smooth[z_idx,:,:]
        lab_low_level, num_obj_low_level = cc_label(single_frame,return_num=True,connectivity=1)

        for idx in range(num_obj_low_level):
            single_cc = (lab_low_level==(idx+1))
            single_raw = single_frame_raw[single_cc]
            if np.count_nonzero(single_raw>global_otsu)<10:
                lab_low_level[lab_low_level==(idx+1)]=0

        bw_prune[z_idx,:,:] = lab_low_level>0
    '''
    bw_prune = bw_low_level.copy()

    bw_high_level = np.zeros_like(bw_prune)
    lab_prune, num_obj_prune = cc_label(bw_prune,return_num=True,connectivity=1)
    for idx in range(num_obj_prune):
        single_obj = (lab_prune==(idx+1))
        local_otsu = threshold_otsu(img_smooth[single_obj])
        bw_high_level[np.logical_and(img_smooth>local_otsu, single_obj)]=1

    bw_finer = np.zeros_like(bw_high_level)
    holes = np.zeros_like(bw_high_level)

    for z_idx in range(img_smooth.shape[0]):
        frame_mask = bw_low_level[z_idx,:,:]
        high_level_mask = bw_high_level[z_idx,:,:]
        if np.any(frame_mask>0):
            frame_raw = img_smooth[z_idx,:,:]
            bright_out = -1*(log_sigma**2)*ndi.filters.gaussian_laplace(frame_raw, log_sigma)
            bright_bw = bright_out>log_th
            bright_bw[frame_mask==0]=0

            inner_mask = erosion(binary_fill_holes(high_level_mask>0),selem=disk(1))>0

            dark_out = -1*(log_sigma**2)*ndi.filters.gaussian_laplace(1-frame_raw, log_sigma)
            dark_out_extra = -1*(log_sigma_extra**2)*ndi.filters.gaussian_laplace(1-frame_raw, log_sigma_extra)
            
            dark_bw = np.logical_or(dark_out>log_th,dark_out_extra>log_th) 
            dark_bw[~inner_mask]=0

            holes[z_idx,:,:] = dark_bw
    
            final_bw = np.logical_or(high_level_mask, bright_bw)
            final_bw[dark_bw>0]=0
            bw_finer[z_idx,:,:] = final_bw

    bw_finer = remove_small_objects(bw_finer, min_size=fine_level_min_size, connectivity=1, in_place=True)

    if rescale_ratio>0:
        bw_finer = processing.resize(bw_finer, [1, 1/rescale_ratio, 1/rescale_ratio], method="nearest")
        #bw_high_level = processing.resize(bw_high_level, [1, 1/rescale_ratio, 1/rescale_ratio], method="nearest")

    bw_finer = bw_finer.astype(np.uint8)
    bw_finer[bw_finer>0]=255
  
    #bw_high_level = bw_high_level.astype(np.uint8)
    #bw_high_level[bw_high_level>0]=255
   
    #holes = holes.astype(np.uint8)
    #holes[holes>0]=255

    return bw_finer