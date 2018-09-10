import numpy as np
import matplotlib.pyplot as plt

def sliceViewer(im, zz):
    plt.imshow(im[zz,:,:])
    plt.show()


def blob2dExplorer_single(im, sigma, th):
    from python_image_analysis.ptDetection import logSlice

    bw = logSlice(im,(sigma[0],sigma[1],1) , th)
    plt.imshow(im)
    plt.show()
    plt.imshow(bw)
    plt.show()

def blob2dExplorer_stack(im_stack, zz, sigma, th):
    from python_image_analysis.ptDetection import logSlice

    im = im_stack[zz,:,:]

    print(im.shape)

    bw = logSlice(im,(sigma[0],sigma[1],1) , th)
    plt.imshow(im)
    plt.show()
    plt.imshow(bw)
    plt.show()

def vesselness2dExplorer(im, zz, sigma, th):
    from python_image_analysis.vessel import vesselness2D

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

def img_seg_combine(img,seg):
# normalize to 0~1
    img = img.astype(np.float32)
    img = (img-img.min())/(img.max()-img.min())
    seg = seg.astype(np.float32)
    seg[seg>0]=1
    
# combine
    combined = np.concatenate((seg, img), axis=2)
    
# overlay
    ovelay = img.copy()
    ovelay[seg>0]=1
    combined = np.concatenate((combined, ovelay), axis=2)
    
#     view
    return combined