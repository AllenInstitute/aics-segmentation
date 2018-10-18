import numpy as np
import os
from skimage.morphology import remove_small_objects, watershed, dilation, ball
from ..pre_processing_utils import intensity_normalization, image_smoothing_gaussian_slice_by_slice
from ..core.seg_dot import dot_3d
from skimage.feature import peak_local_max
from scipy.ndimage import distance_transform_edt
from skimage.measure import label


def DSP_HiPSC_Pipeline(struct_img,rescale_ratio):
    ##########################################################################
    # PARAMETERS:
    #   note that these parameters are supposed to be fixed for the structure
    #   and work well accross different datasets

    intensity_norm_param = [8000]
    gaussian_smoothing_sigma = 1
    gaussian_smoothing_truncate_range = 3.0
    dot_3d_sigma = 1
    dot_3d_cutoff = 0.012
    minArea = 4
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

    # step 2: 'local_maxi + watershed' for cell cutting
    local_maxi = peak_local_max(struct_img,labels=label(bw), min_distance=2, indices=False)
    distance = distance_transform_edt(bw)
    im_watershed = watershed(-distance, label(dilation(local_maxi, selem=ball(1))), mask=bw, watershed_line=True)

    ###################
    # POST-PROCESSING
    ###################
    seg = remove_small_objects(im_watershed, min_size=minArea, connectivity=1, in_place=False)

    # output
    seg = seg>0
    seg = seg.astype(np.uint8)
    seg[seg>0]=255

    return seg



def DSP_drug(img, drug_type):

    '''
    drug:
    0: vehicle
    1: Brefeldin
    2: Paclitaxol
    3: Staurosporine
    4: s-Nitro-Blebbistatin
    5: Rapamycin
    '''

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

