import numpy as np
import matplotlib.pyplot as plt

import ipywidgets as widgets
from ipywidgets import interact, fixed
from IPython.display import display

from itkwidgets import view

def sliceViewer(im, zz):
    plt.imshow(im[zz,:,:])
    plt.show()

def explore_dot_3d(img, sigma, th, roi=[-1]):
    # roi = [x0, y0, x1, y1]
    if roi[0]<0:
        roi = [0,0,img.shape[1],img.shape[2]]

    im = img[:,roi[1]:roi[3],roi[0]:roi[2]]

    from aicssegmentation.core.seg_dot import dot_3d

    response = dot_3d(im, log_sigma=sigma)
    bw = response > th

    out = img_seg_combine(im,bw)
    return out

def explore_vesselness_3d(im, sigma, th, roi=[-1]):
    # roi = [x0, y0, x1, y1]
    if roi[0]<0:
        roi = [0,0,im.shape[1],im.shape[2]]

    from aicssegmentation.core.vessel import vesselness3D

    response = vesselness3D(im, sigmas=sigma,  tau=1, whiteonblack=True)
    bw = response > th

    out = img_seg_combine(im,bw, roi)
    return out

def explore_vesselness_2d(im, sigma, th, roi=[-1]):
    # roi = [x0, y0, x1, y1]
    if roi[0]<0:
        roi = [0,0,im.shape[1],im.shape[2]]

    from aicssegmentation.core.vessel import vesselnessSliceBySlice

    response = vesselnessSliceBySlice(im, sigmas=sigma,  tau=1, whiteonblack=True)
    bw = response > th

    out = img_seg_combine(im,bw, roi)
    return out

def blob2dExplorer_single(im, sigma, th):
    #from python_image_analysis.ptDetection import logSlice

    bw = logSlice(im,(sigma[0],sigma[1],1) , th)
    plt.imshow(im)
    plt.show()
    plt.imshow(bw)
    plt.show()

def blob2dExplorer_stack(im_stack, zz, sigma, th):
    #from python_image_analysis.ptDetection import logSlice

    im = im_stack[zz,:,:]

    print(im.shape)

    bw = logSlice(im,(sigma[0],sigma[1],1) , th)
    plt.imshow(im)
    plt.show()
    plt.imshow(bw)
    plt.show()

def vesselness2dExplorer(im, zz, sigma, th):
    #from python_image_analysis.vessel import vesselness2D

    mip= np.amax(im,axis=0)
    tmp = np.concatenate((im[zz,:,:],mip),axis=1)
    tmp = vesselness2D(tmp, scale_range=(sigma[0],sigma[1]+0.5,0.5), scale_step=1, tau=1, whiteonblack=True)
    ves = np.zeros_like(mip)
    ves[:,:im.shape[2]-2]= tmp[:,:im.shape[2]-2]
    plt.imshow(im[zz,:,:])
    plt.show()
    plt.imshow(ves>th)
    plt.show()

def mipView(im):
    mip= np.amax(im,axis=0)
    plt.imshow(mip)
    plt.show()

def img_seg_combine(img, seg, roi=['Full',None]):

    # normalize to 0~1
    img = img.astype(np.float32)
    img = (img-img.min())/(img.max()-img.min())
    seg = seg.astype(np.float32)
    seg[seg>0]=1

    if roi[0]=='ROI' or roi[0]=='roi':
        img = img[roi[1]]
        seg = seg[roi[1]]
    elif roi[0]=='manual' or roi[0]=='M':
        img = img[:,roi[1][1]:roi[1][3],roi[1][0]:roi[1][2]]
        seg = seg[:,roi[1][1]:roi[1][3],roi[1][0]:roi[1][2]]

    # combine
    combined = np.concatenate((seg, img), axis=2)

    ## overlay
    #ovelay = img.copy()
    #ovelay[seg>0]=1
    #combined = np.concatenate((combined, ovelay), axis=2)

    #  view
    return combined

def segmentation_quick_view(seg):
    valid_pxl = np.unique(seg[seg>0])
    if len(valid_pxl)<1:
        print('segmentation is empty')
        return

    seg = seg>0
    seg = seg.astype(np.uint8)
    seg[seg>0]=255

    return seg

def single_fluorescent_view(im):

    assert len(im.shape)==3

    im = im.astype(np.float32)
    im = (im - im.min())/(im.max()-im.min())

    return im

def seg_fluo_side_by_side(im, seg, roi=['Full',None]):

    out = img_seg_combine(im, seg, roi)

    return out
