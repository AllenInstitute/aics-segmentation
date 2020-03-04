import numpy as np
import copy
from .utils import divide_nonzero
from .hessian import absolute_3d_hessian_eigenvalues


def blobness3D(nd_array, scale_range=(1, 10), scale_step=2, tau=0.5, whiteonblack=True):

    if not nd_array.ndim == 3:
        raise(ValueError("Only 3 dimensions is currently supported"))

    # from https://github.com/scikit-image/scikit-image/blob/master/skimage/filters/_frangi.py#L74
    sigmas = np.arange(scale_range[0], scale_range[1], scale_step)
    if np.any(np.asarray(sigmas) < 0.0):
        raise ValueError("Sigma values less than zero are not valid")

    print(sigmas)

    filtered_array = np.zeros(sigmas.shape + nd_array.shape)

    for i, sigma in enumerate(sigmas):
        eigenvalues = absolute_3d_hessian_eigenvalues(nd_array, sigma=sigma, scale=True, whiteonblack=True)
        # print(eigenvalues[1])
        # print(eigenvalues[2])
        filtered_array[i] = compute_blobness3D(eigenvalues[0], eigenvalues[1], eigenvalues[2], tau=tau)

    return np.max(filtered_array, axis=0)

def filament_3d_wrapper(struct_img, f3_param):
    bw = np.zeros(struct_img.shape, dtype=bool)
    for fid in range(len(f3_param)):
        sigma = f3_param[fid][0]
        eigenvalues = absolute_3d_hessian_eigenvalues(struct_img, sigma=sigma, scale=True, whiteonblack=True)
        responce = compute_vesselness3D(eigenvalues[1], eigenvalues[2], tau=1)
        bw = np.logical_or(bw, responce>f3_param[fid][1])
    return bw

def filament_2d_wrapper(struct_img, f2_param):
    bw = np.zeros(struct_img.shape, dtype=bool)

    if len(struct_img.shape)==2:
        for fid in range(len(f2_param)):
            sigma = f2_param[fid][0]
            eigenvalues = absolute_3d_hessian_eigenvalues(struct_img, sigma=sigma, scale=True, whiteonblack=True)
            responce = compute_vesselness2D(eigenvalues[1], tau=1)
            bw = np.logical_or(bw, responce > f2_param[fid][1])
    elif len(struct_img.shape)==3:
        mip = np.amax(struct_img, axis=0)
        for fid in range(len(f2_param)):
            sigma = f2_param[fid][0]
    
            res = np.zeros_like(struct_img)
            for zz in range(struct_img.shape[0]):
                tmp = np.concatenate((struct_img[zz, :, :], mip), axis=1)
                eigenvalues = absolute_3d_hessian_eigenvalues(tmp, sigma=sigma, scale=True, whiteonblack=True)
                responce = compute_vesselness2D(eigenvalues[1], tau=1)
                res[zz, :, :struct_img.shape[2]-3] = responce[:, :struct_img.shape[2]-3]
            bw = np.logical_or(bw, res>f2_param[fid][1])
    return bw


def vesselness3D(nd_array, sigmas, tau=0.5, whiteonblack=True):

    if not nd_array.ndim == 3:
        raise(ValueError("Only 3 dimensions is currently supported"))

    # adapted from https://github.com/scikit-image/scikit-image/blob/master/skimage/filters/_frangi.py#L74
    if np.any(np.asarray(sigmas) < 0.0):
        raise ValueError("Sigma values less than zero are not valid")

    filtered_array = np.zeros(tuple([len(sigmas),]) + nd_array.shape)

    for i, sigma in enumerate(sigmas):
        eigenvalues = absolute_3d_hessian_eigenvalues(nd_array, sigma=sigma, scale=True, whiteonblack=True)
        # print(eigenvalues[1])
        # print(eigenvalues[2])
        filtered_array[i] = compute_vesselness3D(eigenvalues[1], eigenvalues[2], tau=tau)

    return np.max(filtered_array, axis=0)


def plateness3D(nd_array, scale_range=(1, 10), scale_step=2, tau=0.5, pa=0.5, pb=0.5, pc=1, whiteonblack=True):
    if not nd_array.ndim == 3:
        raise(ValueError("Only 3 dimensions is currently supported"))

    sigmas = np.arange(scale_range[0], scale_range[1], scale_step)
    if np.any(np.asarray(sigmas) < 0.0):
        raise ValueError("Sigma values less than zero are not valid")

    print(sigmas)

    filtered_array = np.zeros(sigmas.shape + nd_array.shape)
    for i, sigma in enumerate(sigmas):
        eigenvalues = absolute_3d_hessian_eigenvalues(nd_array, sigma=sigma, scale=True, whiteonblack=True)
        filtered_array[i] = compute_plateness3D(eigenvalues[0], eigenvalues[1], eigenvalues[2], pa, pb, pc, tau=tau)

    return np.max(filtered_array, axis=0)


def vesselness2D(nd_array, sigmas, tau=0.5, whiteonblack=True):

    if not nd_array.ndim == 2:
        raise(ValueError("Only 2 dimensions is currently supported"))

    # adapted from https://github.com/scikit-image/scikit-image/blob/master/skimage/filters/_frangi.py#L74
    if np.any(np.asarray(sigmas) < 0.0):
        raise ValueError("Sigma values less than zero are not valid")

    filtered_array = np.zeros(tuple([len(sigmas), ]) + nd_array.shape)

    for i, sigma in enumerate(sigmas):
        eigenvalues = absolute_3d_hessian_eigenvalues(nd_array, sigma=sigma, scale=True, whiteonblack=True)
        # print(eigenvalues[1])
        # print(eigenvalues[2])
        filtered_array[i] = compute_vesselness2D(eigenvalues[1], tau=tau)

    return np.max(filtered_array, axis=0)

def vesselness2D_range(nd_array, scale_range=(1, 10), scale_step=2, tau=0.5, whiteonblack=True):

    if not nd_array.ndim == 2:
        raise(ValueError("Only 2 dimensions is currently supported"))

    # from https://github.com/scikit-image/scikit-image/blob/master/skimage/filters/_frangi.py#L74
    sigmas = np.arange(scale_range[0], scale_range[1], scale_step)
    if np.any(np.asarray(sigmas) < 0.0):
        raise ValueError("Sigma values less than zero are not valid")

    print(sigmas)

    filtered_array = np.zeros(sigmas.shape + nd_array.shape)

    for i, sigma in enumerate(sigmas):
        eigenvalues = absolute_3d_hessian_eigenvalues(nd_array, sigma=sigma, scale=True, whiteonblack=True)
        #print(eigenvalues[1])
        #print(eigenvalues[2])
        filtered_array[i] = compute_vesselness2D(eigenvalues[1], tau = tau)

    return np.max(filtered_array, axis=0)

def vesselnessSliceBySlice(nd_array, sigmas, tau=0.5, whiteonblack=True):

    mip = np.amax(nd_array, axis=0)
    response = np.zeros(nd_array.shape)
    for zz in range(nd_array.shape[0]):
        tmp = np.concatenate((nd_array[zz, :, :], mip), axis=1)
        tmp = vesselness2D(tmp,  sigmas=sigmas, tau=1, whiteonblack=True)
        response[zz, :, :nd_array.shape[2]-3] = tmp[:, :nd_array.shape[2]-3]

    return response


def compute_blobness3D(eigen1, eigen2, eigen3, tau):

    lambda3m = copy.copy(eigen3)
    lambda3m[eigen3 > (tau*eigen3.min())] = tau*eigen3.min()

    response = np.multiply(np.square(eigen1), lambda3m)
    response = divide_nonzero(27*response, np.power(2*eigen1 + lambda3m, 3))
    
    response[np.less(np.abs(lambda3m), np.abs(eigen1))] = 1
    response[eigen1 >= 0] = 0
    response[eigen2 >= 0] = 0
    response[eigen3 >= 0] = 0
    response[np.isinf(response)] = 0

    return response


def compute_vesselness3D(eigen2, eigen3, tau):

    lambda3m = copy.copy(eigen3)
    lambda3m[np.logical_and(eigen3 < 0, eigen3 > (tau*eigen3.min()))]=tau*eigen3.min()
    response = np.multiply(np.square(eigen2),np.abs(lambda3m-eigen2))
    response = divide_nonzero(27*response, np.power(2*np.abs(eigen2)+np.abs(lambda3m-eigen2),3))

    response[np.less(eigen2, 0.5*lambda3m)]=1
    response[eigen2>=0]=0
    response[eigen3>=0]=0
    response[np.isinf(response)]=0

    return response

def compute_vesselness2D(eigen2, tau):

    Lambda3 = copy.copy(eigen2)
    Lambda3[np.logical_and(Lambda3<0 , Lambda3 >= (tau*Lambda3.min()))]=tau*Lambda3.min()

    response = np.multiply(np.square(eigen2),np.abs(Lambda3-eigen2))
    response = divide_nonzero(27*response, np.power(2*np.abs(eigen2)+np.abs(Lambda3-eigen2),3))

    response[np.less(eigen2, 0.5*Lambda3)]=1
    response[eigen2>=0]=0
    response[np.isinf(response)]=0

    return response

def compute_plateness3D(eigen1, eigen2, eigen3, pa, pb, pc, tau):

    response = eigen2-eigen3 # -1*(eigen3 - eigen2) # assume eigen3<0, abs(eigen3)>abs(eigen2)
    response[eigen3>-0.001]=0

    '''
    Ra = divide_nonzero(np.abs(eigen2),np.abs(eigen3))
    Rb = divide_nonzero(np.abs(eigen1), np.sqrt(np.abs(np.multiply(eigen2,eigen3))))
    SS = np.sqrt(np.square(eigen1)+np.square(eigen2)+np.square(eigen3))

    aa = 2*pa*pa
    bb = 2*pb*pb
    cc = 2*pc*pc

    m1 = np.exp(-1*np.square(Ra)/aa)
    m2 = np.exp(-1*np.square(Rb)/bb)
    m3 = np.exp(-1*np.square(SS)/cc)

    response = m1 * m2 * (1-m3)
    response[eigen3>0]=0
    response[np.isinf(response)]=0
    '''
    return response
