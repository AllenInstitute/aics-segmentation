import numpy as np
import os
from argparse import ArgumentParser
from aicsimage import processing, io
from .vessel import vesselness3D, vesselness2D
from scipy import ndimage as ndi
from skimage.morphology import remove_small_objects, dilation, erosion, ball, disk, skeletonize, skeletonize_3d
from .utils import histogram_otsu
import math

'''
drug:
0: vehicle
1: Brefeldin
2: Paclitaxol
3: Staurosporine
4: s-Nitro-Blebbistatin
5: Rapamycin
'''

def SEC61B(img, drug_type):

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
    thresh_3d = 0.25
    minArea = 30
    dynamic_range = 6
    ##########################################################################

    max_range = min(np.max(struct_img), np.median(struct_img) + dynamic_range*np.std(struct_img))
    struct_img[struct_img>max_range] = max_range
    struct_img = (struct_img - struct_img.min() + 1e-8)/(max_range - struct_img.min() + 1e-8)

    mip= np.amax(struct_img,axis=0)
    struct_img = ndi.gaussian_filter(struct_img, sigma=1, mode='nearest', truncate=3.0)
    #print(np.mean(struct_img))

    bw2d = np.zeros_like(struct_img)
    for zi in range(struct_img.shape[0]):
        tmp = np.concatenate((struct_img[zi,:,:],mip),axis=1)
        tmp_ves = vesselness2D(tmp, scale_range=(1,3), scale_step=1, tau=1, whiteonblack=True)
        bw2d[zi,:,:struct_img.shape[2]-2]=tmp_ves[:,:struct_img.shape[2]-2]>thresh_3d

    # thresholding the response
    bw = remove_small_objects(bw2d>0, min_size=minArea, connectivity=1, in_place=False)

    return bw 

def Brefeldin(struct_img):
    bw = Vehicle(struct_img)

    return bw 
    
    '''
    ##########################################################################
    # PARAMETERS:
    #   note that these parameters are supposed to be fixed for the structure
    #   and work well accross different datasets
    thresh_3d = 0.08
    minArea = 30
    dynamic_range = 6
    ##########################################################################

    max_range = min(np.max(struct_img), np.median(struct_img) + dynamic_range*np.std(struct_img))
    struct_img[struct_img>max_range] = max_range
    struct_img = (struct_img - struct_img.min() + 1e-8)/(max_range - struct_img.min() + 1e-8)

    mip= np.amax(struct_img,axis=0)
    struct_img = ndi.gaussian_filter(struct_img, sigma=1, mode='nearest', truncate=3.0)
    #print(np.mean(struct_img))

    bw2d = np.zeros_like(struct_img)
    for zi in range(struct_img.shape[0]):
        tmp = np.concatenate((struct_img[zi,:,:],mip),axis=1)
        tmp_ves = vesselness2D(tmp, scale_range=(1,2), scale_step=1, tau=1, whiteonblack=True)
        bw2d[zi,:,:struct_img.shape[2]-2]=tmp_ves[:,:struct_img.shape[2]-2]>thresh_3d

    # thresholding the response
    bw = remove_small_objects(bw2d, min_size=minArea, connectivity=1, in_place=False)

    return bw 
    '''

def Paclitaxol(struct_img):
    bw = Vehicle(struct_img)

    return bw 

    
def Staurosporine(struct_img):
    ##########################################################################
    # PARAMETERS:
    #   note that these parameters are supposed to be fixed for the structure
    #   and work well accross different datasets
    thresh_3d = 0.08
    minArea = 30
    dynamic_range = 6
    log_sigma = 7
    log_th = 0.15
    ##########################################################################

    max_range = min(np.max(struct_img), np.median(struct_img) + dynamic_range*np.std(struct_img))
    struct_img[struct_img>max_range] = max_range
    struct_img = (struct_img - struct_img.min() + 1e-8)/(max_range - struct_img.min() + 1e-8)

    mip= np.amax(struct_img,axis=0)
    struct_img = ndi.gaussian_filter(struct_img, sigma=1, mode='nearest', truncate=3.0)
    #print(np.mean(struct_img))

    bw2d = np.zeros_like(struct_img)
    for zi in range(struct_img.shape[0]):
        tmp = np.concatenate((struct_img[zi,:,:],mip),axis=1)
        tmp_ves = vesselness2D(tmp, scale_range=(1,2), scale_step=1, tau=1, whiteonblack=True)
        bw2d[zi,:,:struct_img.shape[2]-2]=tmp_ves[:,:struct_img.shape[2]-2]>thresh_3d

        response = -1*(log_sigma**2)*ndi.filters.gaussian_laplace(struct_img[zi,:,:], log_sigma)
        bw2d[zi,:,:] = np.logical_or(bw2d[zi,:,:], response>log_th)

    # thresholding the response
    bw = remove_small_objects(bw2d>0, min_size=minArea, connectivity=1, in_place=False)

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


def Sec61B_HiPSC_Pipeline(struct_img,rescale_ratio):

    ##########################################################################
    # PARAMETERS:
    #   note that these parameters are supposed to be fixed for the structure
    #   and work well accross different datasets
    thresh_3d = 0.12 # 0.28  # 0.12
    minArea = 10
    dynamic_range = 6
    ##########################################################################

    max_range = min(np.max(struct_img), np.median(struct_img) + dynamic_range*np.std(struct_img))
    struct_img[struct_img>max_range] = max_range
    struct_img = (struct_img - struct_img.min() + 1e-8)/(max_range - struct_img.min() + 1e-8)

    ## remove the first frame from every frame
    #for zz in range(struct_img.shape[0]):
    #    struct_img[zz,:,:] = struct_img[zz,:,:] - struct_img[0,:,:]
    #struct_img = (struct_img - struct_img.min() )/(struct_img.max() - struct_img.min())

    if rescale_ratio>0:
        struct_img = processing.resize(struct_img, [1, rescale_ratio, rescale_ratio], method="cubic")
        struct_img = (struct_img - struct_img.min() + 1e-8)/(struct_img.max() - struct_img.min() + 1e-8)
        img_smooth = ndi.gaussian_filter(struct_img, sigma=1, mode='nearest', truncate=3.0*rescale_ratio)
    else:
        img_smooth = ndi.gaussian_filter(struct_img, sigma=1, mode='nearest', truncate=3.0)

    mip= np.amax(img_smooth,axis=0)
    

    bw2d = np.zeros_like(img_smooth)
    for zi in range(img_smooth.shape[0]):
        tmp = np.concatenate((img_smooth[zi,:,:],mip),axis=1)
        tmp_ves = vesselness2D(tmp, scale_range=(1,2), scale_step=1, tau=1, whiteonblack=True)
        bw2d[zi,:,:img_smooth.shape[2]-2]=tmp_ves[:,:img_smooth.shape[2]-2]>thresh_3d

    bw = remove_small_objects(bw2d>0, min_size=minArea, connectivity=1, in_place=False)

    if rescale_ratio>0:
        bw= processing.resize(bw, [1, 1/rescale_ratio, 1/rescale_ratio], method="nearest")

    return bw 