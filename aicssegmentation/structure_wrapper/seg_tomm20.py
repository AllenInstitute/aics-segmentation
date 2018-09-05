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

def TOMM20(img, drug_type):

    print('tom20+drug is not supported yet')
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
    print('tom20+drug is not supported yet')
    

def Brefeldin(struct_img):
    print('tom20+drug is not supported yet')

def Paclitaxol(struct_img):
    print('tom20+drug is not supported yet')

    
def Staurosporine(struct_img):
    print('tom20+drug is not supported yet')

def Blebbistatin(struct_img):
    print('tom20+drug is not supported yet')

def Rapamycin(struct_img):
    print('tom20+drug is not supported yet')

def TOMM20_HiPSC_Pipeline(struct_img,rescale_ratio):

    print('no done yet')
    ##########################################################################
    # PARAMETERS:
    #   note that these parameters are supposed to be fixed for the structure
    #   and work well accross different datasets
    dynamic_range = 20
    th3D = 0.07
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

    # basic filter
    response3d = vesselness3D(img_smooth, scale_range=(1,2), scale_step=1,  tau=1, whiteonblack=True)
    bw_final = remove_small_objects(response3d>th3D, min_size=min_size, connectivity=3, in_place=True)
  
    if rescale_ratio>0:
        bw_final = processing.resize(bw_final, [1, 1/rescale_ratio, 1/rescale_ratio], method="nearest")

    bw_final = bw_final.astype(np.uint8)
    bw_final[bw_final>0.5]=255

    return bw_final

def TOMM20_Cardio(struct_img,rescale_ratio):
    ##########################################################################
    # PARAMETERS:
    #   note that these parameters are supposed to be fixed for the structure
    #   and work well accross different datasets
    dynamic_range = 21
    th3D = 0.02
    min_size = 20
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
    response3d = vesselness3D(img_smooth, scale_range=(1,3), scale_step=1,  tau=1, whiteonblack=True)
    bw_final = remove_small_objects(response3d>th3D, min_size=min_size, connectivity=3, in_place=True)
  
    if rescale_ratio>0:
        bw_final = processing.resize(bw_final, [1, 1/rescale_ratio, 1/rescale_ratio], method="nearest")

    bw_final = bw_final.astype(np.uint8)
    bw_final[bw_final>0.5]=255

    return bw_final

def TOMM20_HiPSC_Pipeline(struct_img,rescale_ratio):

    ##########################################################################
    # PARAMETERS:
    #   note that these parameters are supposed to be fixed for the structure
    #   and work well accross different datasets
    # thresh_3d = 0.01
    thresh_2d = 0.14
    minArea = 12 # 20
    dynamic_range = 12
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

    #struct_img = ndi.gaussian_filter(struct_img, sigma=1, mode='nearest', truncate=3.0)
    #struct_img = processing.resize(struct_img, (1.0, args.resize, args.resize), method='cubic')
    #print(np.mean(struct_img))

    #response = vesselness3D(struct_img, scale_range=(1.25, 2), scale_step=1,  tau=1, whiteonblack=True)
    # range = (1,3) --> sigma = 1, 2 (3 is not included)
    mip= np.amax(struct_img,axis=0)
    response = np.zeros_like(struct_img)
    bw = np.zeros(struct_img.shape).astype(bool)
    for zz in range(struct_img.shape[0]):
        tmp = np.concatenate((struct_img[zz,:,:],mip),axis=1)
        tmp = vesselness2D(tmp, scale_range=(1.5,2), scale_step=1, tau=1, whiteonblack=True)
        bw[zz,:,:struct_img.shape[2]-2]=remove_small_objects( tmp[:,:struct_img.shape[2]-2]>thresh_2d, min_size= minArea, connectivity=1, in_place=False) 


    # thresholding the response
    #bw = response>thresh_2d

    bw = remove_small_objects(bw, min_size=minArea, connectivity=1, in_place=False)


    if rescale_ratio>0:
        bw= processing.resize(bw, [1, 1/rescale_ratio, 1/rescale_ratio], method="nearest")

    return bw 