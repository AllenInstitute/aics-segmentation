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

def ATP2A2(img, drug_type):

    print('atp2a2+drug is not supported yet')
    quit()
    '''
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
    '''


def Vehicle(struct_img):
    print('atp2a2+drug is not supported yet')
    

def Brefeldin(struct_img):
    print('atp2a2+drug is not supported yet')

def Paclitaxol(struct_img):
    print('atp2a2+drug is not supported yet')

    
def Staurosporine(struct_img):
    print('atp2a2+drug is not supported yet')

def Blebbistatin(struct_img):
    print('atp2a2+drug is not supported yet')

def Rapamycin(struct_img):
    print('atp2a2+drug is not supported yet')

def ATP2A2_HiPSC_Pipeline(struct_img,rescale_ratio):
    ##########################################################################
    # PARAMETERS:
    #   note that these parameters are supposed to be fixed for the structure
    #   and work well accross different datasets
    dynamic_range = 15
    thresh_2d = 0.035
    min_size = 6
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

    mip= np.amax(img_smooth,axis=0)

    bw2d = np.zeros_like(struct_img)
    for zi in range(img_smooth.shape[0]):
        tmp = np.concatenate((img_smooth[zi,:,:],mip),axis=1)
        tmp_ves = vesselness2D(tmp, scale_range=(0.5,1), scale_step=1, tau=1, whiteonblack=True)
        bw2d[zi,:,:img_smooth.shape[2]-2]=tmp_ves[:,:img_smooth.shape[2]-2]>thresh_2d

    bw_final = remove_small_objects(bw2d>0, min_size=min_size, connectivity=1, in_place=False)
  
    if rescale_ratio>0:
        bw_final = processing.resize(bw_final, [1, 1/rescale_ratio, 1/rescale_ratio], method="nearest")

    bw_final = bw_final.astype(np.uint8)
    bw_final[bw_final>0.5]=255

    return bw_final

def ATP2A2_Cardio(struct_img,rescale_ratio):
    ##########################################################################
    # PARAMETERS:
    #   note that these parameters are supposed to be fixed for the structure
    #   and work well accross different datasets
    dynamic_range = 15
    thresh_2d = 0.035
    min_size = 6
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

    mip= np.amax(img_smooth,axis=0)

    bw2d = np.zeros_like(struct_img)
    for zi in range(img_smooth.shape[0]):
        tmp = np.concatenate((img_smooth[zi,:,:],mip),axis=1)
        tmp_ves = vesselness2D(tmp, scale_range=(0.5,1), scale_step=1, tau=1, whiteonblack=True)
        bw2d[zi,:,:img_smooth.shape[2]-2]=tmp_ves[:,:img_smooth.shape[2]-2]>thresh_2d

    bw_final = remove_small_objects(bw2d>0, min_size=min_size, connectivity=1, in_place=False)
  
    if rescale_ratio>0:
        bw_final = processing.resize(bw_final, [1, 1/rescale_ratio, 1/rescale_ratio], method="nearest")

    bw_final = bw_final.astype(np.uint8)
    bw_final[bw_final>0.5]=255

    return bw_final