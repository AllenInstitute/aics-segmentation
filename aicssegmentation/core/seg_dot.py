from scipy import ndimage as ndi
import numpy as np


def dot_3d(struct_img, log_sigma):
    assert len(struct_img.shape) == 3
    responce = -1*(log_sigma**2)*ndi.filters.gaussian_laplace(struct_img, log_sigma)
    return responce


def dot_2d(struct_img, log_sigma):
    assert len(struct_img.shape) == 2 
    responce = -1*(log_sigma**2)*ndi.filters.gaussian_laplace(struct_img, log_sigma)
    return responce


def dot_slice_by_slice(struct_img, log_sigma):
    res = np.zeros_like(struct_img)
    for zz in range(struct_img.shape[0]):
        res[zz, :, :] = -1*(log_sigma**2)*ndi.filters.gaussian_laplace(struct_img[zz, :, :], log_sigma)
    return res
