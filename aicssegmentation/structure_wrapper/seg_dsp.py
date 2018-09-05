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

def DSP(img, drug_type):

    if drug_type==0:
        bw = Vehicle(img)
    elif drug_type==1:
        print('un-evaluated drug type')
        quit()
        #bw = Brefeldin(img)
    elif drug_type==2:
        bw = Paclitaxol(img)
    elif drug_type==3:
        bw = Staurosporine(img)
    elif drug_type==4:
        print('un-evaluated drug type')
        quit()
        #bw = Blebbistatin(img)
    elif drug_type==5:
        print('un-evaluated drug type')
        quit()
        #bw = Rapamycin(img)
    else:
        print('unsupported drug type')
        bw = None

    return bw 


def Vehicle(struct_img):
    ##########################################################################
    # PARAMETERS:
    #   note that these parameters are supposed to be fixed for the structure
    #   and work well accross different datasets
    thresh_log = 0.006
    minArea = 5
    log_sigma = 1
    ##########################################################################

    struct_img = (struct_img - struct_img.min() + 1e-8)/(struct_img.max()- struct_img.min() + 1e-8)
    img_smooth_2d = struct_img.copy()
    for zz in range(struct_img.shape[0]):
        tmp = img_smooth_2d[zz,:,:]
        tmp = ndi.gaussian_filter(tmp, sigma=1, mode='nearest', truncate=3.0)
        img_smooth_2d[zz,:,:]=tmp

    response = -1*(log_sigma**2)*ndi.filters.gaussian_laplace(img_smooth_2d, log_sigma)
    bw = response>thresh_log

    bw = remove_small_objects(bw, min_size=minArea, connectivity=1, in_place=False)

    return bw 


def Paclitaxol(struct_img):
    bw = Vehicle(struct_img)

    return bw 
    
def Staurosporine(struct_img):
    bw = Vehicle(struct_img)

    return bw 

