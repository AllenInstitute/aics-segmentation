from numpy import zeros, ones, asarray
from numpy.linalg import norm
from math import pi
import math
from scipy.ndimage.filters import gaussian_laplace, minimum_filter, convolve
from operator import contains
from functools import partial
from itertools import filterfalse
import numpy as np
from datetime import datetime
from skimage.feature import blob_log
from skimage.feature import peak_local_max

def localMinima(data, threshold):
    from numpy import ones, nonzero, transpose

    if threshold is not None:
        peaks = data < threshold
    else:
        peaks = ones(data.shape, dtype=data.dtype)

    peaks &= data == minimum_filter(data, size=(3,) * data.ndim)
    return transpose(nonzero(peaks))

def blobLOG(data, scales=range(1, 10, 1), threshold=-30):
    """Find blobs. Returns [[scale, x, y, ...], ...]"""
    from numpy import empty, asarray
    from itertools import repeat

    data = asarray(data)
    scales = asarray(scales)

    log = empty((len(scales),) + data.shape, dtype=data.dtype)
    for slog, scale in zip(log, scales):
        slog[...] = scale ** 2 * gaussian_laplace(data, scale)

    peaks = localMinima(log, threshold=threshold)
    peaks[:, 0] = scales[peaks[:, 0]]
    return peaks

def tophatSliceBySlice(im, sz):
    from skimage.morphology import white_tophat, disk

    startTime = datetime.now()
    se = disk(sz)
    print(datetime.now()-startTime)
    print('tophat starts')
    for zz in range(im.shape[0]):
        startTime = datetime.now()
        im[zz,:,:] = white_tophat(im[zz,:,:], se)
        print(datetime.now()-startTime)
    return im

def logSliceBySlice(im, max_sigma, min_sigma, num_sigma, threshold, indices=False):

    sigma_list = np.linspace(min_sigma, max_sigma, num_sigma)

    # initialization
    bw = np.zeros_like(im)
    #im_log = np.zeros_like(im)
    if indices:
        idices_z = []

    # operation slice by slice
    for zz in range(im.shape[0]):
        image=im[zz,:,:]
        gl_images = [-gaussian_laplace(image, s) * s ** 2 for s in sigma_list]

        # get the mask
        seg = np.zeros_like(image)
        for zi in range(num_sigma):
            seg = np.logical_or(seg, gl_images[zi]>threshold)
        bw[zz,:,:] = seg

        if indices:
            image_cube = np.dstack(gl_images)
            local_maxima = peak_local_max(image_cube, threshold_abs=threshold,footprint=np.ones((3, 3, 3)),threshold_rel=0.0,exclude_border=False)
            lm = local_maxima.astype(np.float64)
            lm[:, 2] = sigma_list[local_maxima[:, 2]]
            local_maxima = lm
            indices_z.append(local_maxima)

    if indices:
        return bw, indices
    else:
        return bw

def logSlice(image, sigma_list, threshold):

    #sigma_list = np.linspace(min_sigma, max_sigma, num_sigma)

    gl_images = [-gaussian_laplace(image, s) * s ** 2 for s in sigma_list]
    
    # get the mask
    seg = np.zeros_like(image)
    for zi in range(len(sigma_list)):
        seg = np.logical_or(seg, gl_images[zi]>threshold)

    return seg

'''
def log2D(im, max_sigma, min_sigma, num_sigma):

    sigma_list = np.linspace(min_sigma, max_sigma, num_sigma)

    # initialization
    out = np.zeros_like(im)

    # operation slice by slice
    for zz in range(im.shape[0]):
        image=im[zz,:,:]
        gl_images = [-gaussian_laplace(image, s) * s ** 2 for s in sigma_list]

        # get the mask
        seg = np.zeros_like(image)
        for zi in range(num_sigma):
            seg = np.logical_or(seg, gl_images[zi]>threshold)
        bw[zz,:,:] = seg

        if indices:
            image_cube = np.dstack(gl_images)
            local_maxima = peak_local_max(image_cube, threshold_abs=threshold,footprint=np.ones((3, 3, 3)),threshold_rel=0.0,exclude_border=False)
            lm = local_maxima.astype(np.float64)
            lm[:, 2] = sigma_list[local_maxima[:, 2]]
            local_maxima = lm
            indices_z.append(local_maxima)

    if indices:
        return bw, indices
    else:
        return bw
'''

def flatLogSliceBySlice(im, template_size, sigma=0.5):

    t = (template_size-1)/2  # regardless of even or odd number
    [x,y] = np.meshgrid(np.arange(-t,t+1,1), np.arange(-t,t+1,1))
    ### build the kernal

    Hg = np.power(math.e, -1*(x**2+y**2)/(2*sigma**2))
    H = (x**2 + y**2 - 2*sigma**2) * Hg / (Hg.sum()*sigma**4)
    H = H - H.sum()/(template_size*template_size)

    im_log = np.zeros_like(im)
    for zz in range(im.shape[0]):
        im_log[zz,:,:] = convolve(im[zz,:,:], H, mode='nearest')

    return im_log


def sphereIntersection(r1, r2, d):
    # https://en.wikipedia.org/wiki/Spherical_cap#Application

    valid = (d < (r1 + r2)) & (d > 0)
    return (pi * (r1 + r2 - d) ** 2
            * (d ** 2 + 6 * r2 * r1
               + 2 * d * (r1 + r2)
               - 3 * (r1 - r2) ** 2)
            / (12 * d)) * valid

def circleIntersection(r1, r2, d):
    # http://mathworld.wolfram.com/Circle-CircleIntersection.html
    from numpy import arccos, sqrt

    return (r1 ** 2 * arccos((d ** 2 + r1 ** 2 - r2 ** 2) / (2 * d * r1))
            + r2 ** 2 * arccos((d ** 2 + r2 ** 2 - r1 ** 2) / (2 * d * r2))
            - sqrt((-d + r1 + r2) * (d + r1 - r2)
                   * (d - r1 + r2) * (d + r1 + r2)) / 2)

def findBlobs(img, scales=range(1, 10), threshold=30, max_overlap=0.05):
    from numpy import ones, triu, seterr
    old_errs = seterr(invalid='ignore')

    peaks = blobLOG(img, scales=scales, threshold=-threshold)
    radii = peaks[:, 0]
    positions = peaks[:, 1:]

    distances = norm(positions[:, None, :] - positions[None, :, :], axis=2)

    if positions.shape[1] == 2:
        intersections = circleIntersection(radii, radii.T, distances)
        volumes = pi * radii ** 2
    elif positions.shape[1] == 3:
        intersections = sphereIntersection(radii, radii.T, distances)
        volumes = 4/3 * pi * radii ** 3
    else:
        raise ValueError("Invalid dimensions for position ({}), need 2 or 3."
                         .format(positions.shape[1]))

    delete = ((intersections > (volumes * max_overlap))
              # Remove the smaller of the blobs
              & ((radii[:, None] < radii[None, :])
                 # Tie-break
                 | ((radii[:, None] == radii[None, :])
                    & triu(ones((len(peaks), len(peaks)), dtype='bool'))))
    ).any(axis=1)

    seterr(**old_errs)
    return peaks[~delete]

def peakEnclosed(peaks, shape, size=1):
    from numpy import asarray

    shape = asarray(shape)
    return ((size <= peaks).all(axis=-1) & (size < (shape - peaks)).all(axis=-1))

def plot(args):
    from tifffile import imread
    from numpy import loadtxt, delete
    from pickle import load
    import matplotlib
    from mpl_toolkits.axes_grid.anchored_artists import AnchoredAuxTransformBox
    from matplotlib.text import Text
    from matplotlib.text import Line2D

    if args.outfile is not None:
        matplotlib.use('Agg')
    import matplotlib.pyplot as plt

    image = imread(str(args.image)).T
    scale = asarray(args.scale) if args.scale else ones(image.ndim, dtype='int')

    if args.peaks.suffix == '.txt':
        peaks = loadtxt(str(args.peaks), ndmin=2)
    elif args.peaks.suffix == ".csv":
        peaks = loadtxt(str(args.peaks), ndmin=2, delimiter=',')
    elif args.peaks.suffix == ".pickle":
        with args.peaks.open("rb") as f:
            peaks = load(f)
    else:
        raise ValueError("Unrecognized file type: '{}', need '.pickle' or '.csv'"
                         .format(args.peaks.suffix))
    peaks = peaks / scale

    proj_axes = tuple(filterfalse(partial(contains, args.axes), range(image.ndim)))
    image = image.max(proj_axes)
    peaks = delete(peaks, proj_axes, axis=1)

    fig, ax = plt.subplots(1, 1, figsize=args.size)
    ax.imshow(image.T, cmap='gray')
    ax.set_xticks([])
    ax.set_yticks([])
    ax.scatter(*peaks.T, edgecolor="C1", facecolor='none')

    if args.scalebar is not None:
        pixel, units, length = args.scalebar
        pixel = float(pixel)
        length = int(length)

        box = AnchoredAuxTransformBox(ax.transData, loc=4)
        box.patch.set_alpha(0.8)
        bar = Line2D([-length/pixel/2, length/pixel/2], [0.0, 0.0], color='black')
        box.drawing_area.add_artist(bar)
        label = Text(
            0.0, 0.0, "{} {}".format(length, units),
            horizontalalignment="center", verticalalignment="bottom"
        )
        box.drawing_area.add_artist(label)
        ax.add_artist(box)

    if args.outfile is None:
        plt.show()
    else:
        fig.tight_layout()
        fig.savefig(str(args.outfile))

def find(args):
    from sys import stdout
    from tifffile import imread

    image = imread(str(args.image)).astype('float32')

    scale = asarray(args.scale) if args.scale else ones(image.ndim, dtype='int')
    blobs = findBlobs(image, range(*args.size), args.threshold)[:, 1:] # Remove scale
    blobs = blobs[peakEnclosed(blobs, shape=image.shape, size=args.edge)]
    blobs = blobs[:, ::-1] # Reverse to xyz order
    blobs = blobs * scale

    if args.format == "pickle":
        from pickle import dump, HIGHEST_PROTOCOL
        from functools import partial
        dump = partial(dump, protocol=HIGHEST_PROTOCOL)

        dump(blobs, stdout.buffer)
    else:
        import csv

        if args.format == 'txt':
            delimiter = ' '
        elif args.format == 'csv':
            delimiter = ','
        writer = csv.writer(stdout, delimiter=delimiter)
        for blob in blobs:
            writer.writerow(blob)
