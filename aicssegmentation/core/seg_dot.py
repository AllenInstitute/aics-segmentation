from scipy import ndimage as ndi
import numpy as np


def dot_3d(struct_img, log_sigma):
    assert len(struct_img.shape) == 3
    responce = -1*(log_sigma**2)*ndi.filters.gaussian_laplace(struct_img, log_sigma)
    return responce

def dot_3d_wrapper(struct_img, s3_param):
    bw = np.zeros(struct_img.shape, dtype=bool)
    for fid in range(len(s3_param)):
        log_sigma = s3_param[fid][0]
        responce = -1*(log_sigma**2)*ndi.filters.gaussian_laplace(struct_img, log_sigma)
        bw = np.logical_or(bw, responce>s3_param[fid][1])
    return bw

def dot_2d(struct_img, log_sigma):
    assert len(struct_img.shape) == 2
    responce = -1*(log_sigma**2)*ndi.filters.gaussian_laplace(struct_img, log_sigma)
    return responce


def dot_slice_by_slice(struct_img, log_sigma):
    res = np.zeros_like(struct_img)
    for zz in range(struct_img.shape[0]):
        res[zz, :, :] = -1*(log_sigma**2)*ndi.filters.gaussian_laplace(struct_img[zz, :, :], log_sigma)
    return res

def dot_2d_slice_by_slice_wrapper(struct_img, s2_param):
    bw = np.zeros(struct_img.shape, dtype=bool)
    for fid in range(len(s2_param)):
        log_sigma = s2_param[fid][0]
        responce = np.zeros_like(struct_img)
        for zz in range(struct_img.shape[0]):
            responce[zz, :, :] = -1*(log_sigma**2)*ndi.filters.gaussian_laplace(struct_img[zz, :, :], log_sigma)
        bw = np.logical_or(bw, responce>s2_param[fid][1])
    return bw