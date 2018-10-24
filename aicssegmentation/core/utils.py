import numpy as np
from skimage.morphology import medial_axis
from scipy.ndimage import distance_transform_edt
from skimage.morphology import erosion, ball
import aicsimageio


def morphology_preserving_thinning(bw, min_thickness=1, thin=1):

    safe_zone = np.zeros_like(bw)
    for zz in range(bw.shape[0]):
        if np.any(bw[zz, :, :]):
            ctl = medial_axis(bw[zz, :, :] > 0)
            dist = distance_transform_edt(ctl == 0)
            safe_zone[zz, :, :] = dist > min_thickness + 1e-5

    rm_candidate = np.logical_xor(bw > 0, erosion(bw > 0, ball(thin)))

    bw[np.logical_and(safe_zone, rm_candidate)] = 0

    return bw


def save_segmentation(bw, contour_flag, output_path, fn):

    writer = aicsimageio.omeTifWriter.OmeTifWriter(str(output_path / (fn + '_struct_segmentation.tiff')))
    writer.save(bw)

    if contour_flag:
        bd = generate_segmentation_contour(bw)

        writer = aicsimageio.omeTifWriter.OmeTifWriter(str(output_path / (fn + '_struct_contour.tiff')))
        writer.save(bd)


def generate_segmentation_contour(im):

    bd = np.logical_xor(erosion(im > 0, selem=ball(1)), im > 0)

    bd = bd.astype(np.uint8)
    bd[bd > 0] = 255

    return bd


def divide_nonzero(array1, array2):
    """
    Divides two arrays. Returns zero when dividing by zero.
    """
    denominator = np.copy(array2)
    denominator[denominator == 0] = 1e-10
    return np.divide(array1, denominator)


def create_image_like(data, image):
    return image.__class__(data, affine=image.affine, header=image.header)


def histogram_otsu(hist):

    # modify the elements in hist to avoid completely zero value in cumsum
    hist = hist+1e-5

    bin_size = 1/(len(hist)-1)
    bin_centers = np.arange(0, 1+0.5*bin_size, bin_size)
    hist = hist.astype(float)

    # class probabilities for all possible thresholds
    weight1 = np.cumsum(hist)
    weight2 = np.cumsum(hist[::-1])[::-1]
    # class means for all possible thresholds

    mean1 = np.cumsum(hist * bin_centers) / weight1
    mean2 = (np.cumsum((hist * bin_centers)[::-1]) / weight2[::-1])[::-1]

    # Clip ends to align class 1 and class 2 variables:
    # The last value of `weight1`/`mean1` should pair with zero values in
    # `weight2`/`mean2`, which do not exist.
    variance12 = weight1[:-1] * weight2[1:] * (mean1[:-1] - mean2[1:]) ** 2

    idx = np.argmax(variance12)
    threshold = bin_centers[:-1][idx]
    return threshold


def absolute_eigenvaluesh(nd_array):
    """
    Computes the eigenvalues sorted by absolute value from the symmetrical matrix.
    :param nd_array: array from which the eigenvalues will be calculated.
    :return: A list with the eigenvalues sorted in absolute ascending order (e.g. [eigenvalue1, eigenvalue2, ...])
    """
    # print(nd_array)
    # print('up:array, below:eigen')
    eigenvalues = np.linalg.eigvalsh(nd_array)
    # print(eigenvalues)
    sorted_eigenvalues = sortbyabs(eigenvalues, axis=-1)
    return [np.squeeze(eigenvalue, axis=-1)
            for eigenvalue in np.split(sorted_eigenvalues, sorted_eigenvalues.shape[-1], axis=-1)]


def sortbyabs(a, axis=0):
    """Sort array along a given axis by the absolute value
    modified from: http://stackoverflow.com/a/11253931/4067734
    """
    index = list(np.ix_(*[np.arange(i) for i in a.shape]))
    index[axis] = np.abs(a).argsort(axis)
    return a[index]
