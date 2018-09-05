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

def ACTB(img, drug_type):

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
    minArea = 40
    dynamic_range = 7
    ##########################################################################

    max_range = min(np.max(struct_img), np.median(struct_img) + dynamic_range*np.std(struct_img))
    struct_img[struct_img>max_range] = max_range
    struct_img = (struct_img - struct_img.min() + 1e-8)/(max_range - struct_img.min() + 1e-8)

    struct_img = ndi.gaussian_filter(struct_img, sigma=1, mode='nearest', truncate=3.0)
    #print(np.mean(struct_img))

    response = vesselness3D(struct_img, scale_range=(1,3), scale_step=1,  tau=1, whiteonblack=True)
    # range = (1,3) --> sigma = 1, 2 (3 is not included)

    # thresholding the response
    bw = response>thresh_3d
    bw = remove_small_objects(bw, min_size=minArea, connectivity=1, in_place=False)

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
    thresh_3d_low = 0.03
    thresh_3d_high = 0.1
    minArea = 40
    dynamic_range = 6
    ##########################################################################

    max_range = min(np.max(struct_img), np.median(struct_img) + dynamic_range*np.std(struct_img))
    struct_img[struct_img>max_range] = max_range
    struct_img = (struct_img - struct_img.min() + 1e-8)/(max_range - struct_img.min() + 1e-8)

    struct_img = ndi.gaussian_filter(struct_img, sigma=1, mode='nearest', truncate=3.0)
    #print(np.mean(struct_img))

    response = vesselness3D(struct_img, scale_range=(1,3), scale_step=1,  tau=1, whiteonblack=True)
    # range = (1,3) --> sigma = 1, 2 (3 is not included)

    # thresholding the response
    bw = response>thresh_3d_low

    # find the cut place
    z_seg_num = np.zeros(bw.shape[0])
    for zidx in range(bw.shape[0]):
        z_seg_num[zidx] = np.count_nonzero(bw[zidx,:,:])

    try:
        cut_plane = round(histogram_otsu(z_seg_num)*bw.shape[0]).astype(int)
    except ValueError:
        #print(z_seg_num)
        print('error in computing cut plane')
        cut_plane = struct_img.shape[0]//2

    bw2 = response>thresh_3d_high

    bw[:cut_plane,:,:]=bw2[:cut_plane,:,:]

    bw = remove_small_objects(bw, min_size=minArea, connectivity=1, in_place=False)
    return bw 

def Rapamycin(struct_img):
    bw = Vehicle(struct_img)

    return bw 