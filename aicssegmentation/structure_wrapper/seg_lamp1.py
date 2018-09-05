import numpy as np
import os
from argparse import ArgumentParser
from aicsimage import processing, io
from .vessel import vesselness3D, vesselness2D
from scipy import ndimage as ndi
from skimage.morphology import remove_small_objects, dilation, erosion, ball, disk, skeletonize, skeletonize_3d
from .utils import histogram_otsu
import math
from skimage.measure import label

'''
drug:
0: vehicle
1: Brefeldin
2: Paclitaxol
3: Staurosporine
4: s-Nitro-Blebbistatin
5: Rapamycin
'''

def LAMP1(img, drug_type):

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
    dynamic_range = 20
    minArea = 50
    ves_th_2d =0.1
    hole_min = 100
    hole_max = 4900 #1600
    log_sigma_1 = 9
    log_sigma_th_1 = 0.1
    log_sigma_2 = 5
    log_sigma_th_2 = 0.05
    log_sigma_3 = 1
    log_sigma_th_3 = 0.02
    ##########################################################################

    # intenisty normalization (min/max)
    max_range = min(np.max(struct_img), np.median(struct_img) + dynamic_range*np.std(struct_img))
    struct_img[struct_img>max_range] = max_range
    struct_img = (struct_img - struct_img.min() + 1e-8)/(max_range - struct_img.min() + 1e-8)

    struct_img_smooth = ndi.gaussian_filter(struct_img, sigma=1, mode='nearest', truncate=3.0)
    mip = np.amax(struct_img_smooth,axis=0)

    bw2d = np.zeros_like(struct_img)
    for zi in range(struct_img.shape[0]):
        raw = ndi.gaussian_filter(struct_img[zi,:,:], sigma=1, mode='nearest', truncate=3.0)   
        tmp = np.concatenate((raw,mip),axis=1)
        ves2s_tmp = vesselness2D(tmp,scale_range=(1,3),scale_step=1,tau=1.0,whiteonblack=True)

        ves2s = np.zeros_like(mip)
        ves2s[:,:struct_img.shape[2]-2]= ves2s_tmp[:,:struct_img.shape[2]-2]
        
        back_lab = label(ves2s < ves_th_2d, connectivity=1)

        out = np.copy(back_lab)
        component_sizes = np.bincount(back_lab.ravel())
        too_big = component_sizes >hole_max
        too_big_mask = too_big[back_lab]
        out[too_big_mask] = 0
        too_small = component_sizes <hole_min
        too_small_mask = too_small[back_lab]
        out[too_small_mask] = 0

        bw_ves = ves2s > ves_th_2d

        response1 = -1*(log_sigma_1**2)*ndi.filters.gaussian_laplace(raw, log_sigma_1)
        log_bw = response1>log_sigma_th_1

        response2 = -1*(log_sigma_2**2)*ndi.filters.gaussian_laplace(raw, log_sigma_2)
        log_bw = np.logical_or(log_bw, response2>log_sigma_th_2)

        response3 = -1*(log_sigma_3**2)*ndi.filters.gaussian_laplace(raw, log_sigma_3)
        log_bw = np.logical_or(log_bw, response3>log_sigma_th_3)

        bw2d[zi,:,:] = np.logical_or( np.logical_or(log_bw, bw_ves), out>0 )

    bw = remove_small_objects(bw2d>0, min_size=minArea, connectivity=1, in_place=False)
    
    return bw

def Brefeldin(struct_img):
    bw = Vehicle(struct_img)

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

def LAMP1_HiPSC_Pipeline(struct_img,rescale_ratio):
    ##########################################################################
    # PARAMETERS:
    #   note that these parameters are supposed to be fixed for the structure
    #   and work well accross different datasets
    dynamic_range = 20
    minArea = 50
    ves_th_2d =0.1
    hole_min = 100
    hole_max = 1600
    log_sigma_1 = 9
    log_sigma_th_1 = 0.1
    log_sigma_2 = 5
    log_sigma_th_2 = 0.05
    log_sigma_3 = 1
    log_sigma_th_3 = 0.02
    ##########################################################################

    # intenisty normalization (min/max)
    max_range = min(np.max(struct_img), np.median(struct_img) + dynamic_range*np.std(struct_img))
    struct_img[struct_img>max_range] = max_range
    struct_img = (struct_img - struct_img.min() + 1e-8)/(max_range - struct_img.min() + 1e-8)

    struct_img_smooth = ndi.gaussian_filter(struct_img, sigma=1, mode='nearest', truncate=3.0)
    mip = np.amax(struct_img_smooth,axis=0)

    bw2d = np.zeros_like(struct_img)
    for zi in range(struct_img.shape[0]):
        raw = ndi.gaussian_filter(struct_img[zi,:,:], sigma=1, mode='nearest', truncate=3.0)   
        tmp = np.concatenate((raw,mip),axis=1)
        ves2s_tmp = vesselness2D(tmp,scale_range=(1,3),scale_step=1,tau=1.0,whiteonblack=True)

        ves2s = np.zeros_like(mip)
        ves2s[:,:struct_img.shape[2]-2]= ves2s_tmp[:,:struct_img.shape[2]-2]
        
        back_lab = label(ves2s < ves_th_2d, connectivity=1)

        out = np.copy(back_lab)
        component_sizes = np.bincount(back_lab.ravel())
        too_big = component_sizes >hole_max
        too_big_mask = too_big[back_lab]
        out[too_big_mask] = 0
        too_small = component_sizes <hole_min
        too_small_mask = too_small[back_lab]
        out[too_small_mask] = 0

        bw_ves = ves2s > ves_th_2d

        response1 = -1*(log_sigma_1**2)*ndi.filters.gaussian_laplace(raw, log_sigma_1)
        log_bw = response1>log_sigma_th_1

        response2 = -1*(log_sigma_2**2)*ndi.filters.gaussian_laplace(raw, log_sigma_2)
        log_bw = np.logical_or(log_bw, response2>log_sigma_th_2)

        response3 = -1*(log_sigma_3**2)*ndi.filters.gaussian_laplace(raw, log_sigma_3)
        log_bw = np.logical_or(log_bw, response3>log_sigma_th_3)

        bw2d[zi,:,:] = np.logical_or( np.logical_or(log_bw, bw_ves), out>0 )

    bw = remove_small_objects(bw2d>0, min_size=minArea, connectivity=1, in_place=False)
    
    return bw