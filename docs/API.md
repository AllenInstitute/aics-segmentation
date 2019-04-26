# API Reference

List of functions:
* Preprocessing:
    * [`intensity_normalization`](#intensity_norm)
    * `suggest_normalization_param`
    * `image_smoothing_gaussian_3d`
    * `image_smoothing_gaussian_slice_by_slice`
    * `edge_preserving_smoothing_3d`
* Core segmentation algorithms:



## Preprocessing 

### Intensity normalization

--- 

<a name='intensity_norm'>`intensity_norm`</a>

Normalize the intensity of input image so that the value range is from 0 to 1.

```python
from aicssegmentation.core.pre_processing_utils import intensity_normalization
normalized_img = intensity_normalization(img, scaling_param):
```

**Parameters** 
1. img: a 3d numpy array
2. scaling_param: a list of values
    * a list with only one value 0, i.e. `[0]`: Min-Max normlaizaiton, the max intensity of img will be mapped to 1 and min will be mapped to 0
    * a list with a single positive integer v, e.g. `[5000]`: Min-Max normalization, but first any original intensity value > v will be considered as outlier and reset of min intensity of `img`. After the max will be mapped to 1 and min will be mapped to 0
    * a list with two float values [a, b], e.g. `[1.5, 10.5]`: Auto-contrast normalizaiton. First, mean and standard deviaion (std) of the original intensity in `img` are calculated. Next, the intensity is truncated into range [mean - a * std, mean + b * std], and then recaled to [0, 1]
    * a list with four float values [a, b, c, d], e.g. `[0.5, 15.5, 200, 4000]`: Auto-contrast normalization. Similat to above case, but only intensity value between c and d will be used to calculated mean and std. 

**Return**: a 3d numpy array of the same shape as `img` with real value between 0 and 1

---


### Smoothing

----

<a name='gaussian_3d'>`image_smoothing_gaussian_3d`</a>

perform 3D Gaussian smoothing

```python
from aicssegmentation.core.pre_processing_utils import image_smoothing_gaussian_3d
smooth_img = image_smoothing_gaussian_3d(normalized_img, sigma=gaussian_smoothing_sigma)
``` 

**Parameters**
1. normalized_img: a 3d numpy array, usually the image after intensity normalization
2. gaussian_smoothing_sigma: a positive real value, we usually use 1. The larger the value is the smoother the result will be. 

**Return**: a 3d numpy array of the same size as `normalized_img`.

---

<a name='gaussian_2d'>`image_smoothing_gaussian_slice_by_slice`</a>

perform 2D Gaussian smoothing slice-by-slice

```python
from aicssegmentation.core.pre_processing_utils import image_smoothing_gaussian_slice_by_slice
smooth_img = image_smoothing_gaussian_slice_by_slice(normalized_img, sigma=gaussian_smoothing_sigma)
```

**Input**
1. normalized_img: a 3d numpy array, usually the image after intensity normalization
2. gaussian_smoothing_sigma: a positive real value, we usually use 1. The larger the value is the smoother the result will be. 

**Return**: a 3d numpy array of the same size as `normalized_img`.

---

<a name='es'>`edge_preserving_smoothing_3d`</a>

perform edge-preserving smoothing

```python
from aicssegmentation.core.pre_processing_utils import edge_preserving_smoothing_3d
smooth_img = edge_preserving_smoothing_3d(normalized_img) 
```

**Parameters**
1. normalized_img: a 3d numpy array, usually the image after intensity normalization

**Return**: a 3d numpy array of the same size as `normalized_img`.

---
---


## Core segmentation algorithms

---
<a name='f2'>`filament_3d_wrapper`</a>

apply 2D filament filter slice by slice

```python
from aicssegmentation.core.vessel import filament_2d_wrapper
bw = filament_2d_wrapper(smooth_img, f2_param)
```

**Parameters**:
1. smooth_img: a 3d numpy array, usually the image after smoothing
2. f2_param = [[scale_1, cutoff_1], [scale_2, cutoff_2], ....], e.g., `[[1, 0.01]]` or `[[1,0.05], [0.5, 0.1]]`: `scale_x` is set based on the estimated thickness of your target filaments. For example, if visually the thickness of the filaments is usually 3~4 pixels, then you may want to set `scale_x` as `1` or something near `1` (like `1.25`). Multiple scales can be used, if you have filaments of very different thickness.`cutoff_x` is a threshold applied on the actual filter reponse to get the binary result. Smaller `cutoff_x` may yielf more filaments, especially detecting more dim ones and thicker segmentation, while larger `cutoff_x` could be less permisive and yield less filaments and slimmer segmentation.

**Return**: a 3d numpy array of 0 and 1

---

<a name='f3'>`filament_3d_wrapper`</a>

apply 3D filament filter 

```python
from aicssegmentation.core.vessel import filament_3d_wrapper
bw = filament_3d_wrapper(smooth_img, f3_param)
```

**Parameters**:
1. smooth_img: a 3d numpy array, usually the image after smoothing
2. f3_param = [[scale_1, cutoff_1], [scale_2, cutoff_2], ....], e.g., `[[1, 0.01]]` or `[[1,0.05], [0.5, 0.1]]`: `scale_x` is set based on the estimated thickness of your target filaments. For example, if visually the thickness of the filaments is usually 3~4 pixels, then you may want to set `scale_x` as `1` or something near `1` (like `1.25`). Multiple scales can be used, if you have filaments of very different thickness.`cutoff_x` is a threshold applied on the actual filter reponse to get the binary result. Smaller `cutoff_x` may yielf more filaments, especially detecting more dim ones and thicker segmentation, while larger `cutoff_x` could be less permisive and yield less filaments and slimmer segmentation.

**Return** a 3d numpy array of 0 and 1

---

<a name='s2'>`dot_2d_slice_by_slice_wrapper`</a>

apply 2D spot filter slice by slice

```python
from aicssegmentation.core.seg_dot import dot_2d_slice_by_slice_wrapper
bw = dot_2d_slice_by_slice_wrapper(structure_img_smooth, s2_param)
```
**Parameters**:
1. smooth_img: a 3d numpy array, usually the image after smoothing
2. s2_param= [[scale_1, cutoff_1], [scale_2, cutoff_2], ....], e.g. `[[1, 0.1]]` or `[[1,0.12], [3,0.1]]`:
    `scale_x` is set based on the estimated radius of your target dots. For example, if visually the diameter of the dots is usually 3~4 pixels, then you may want to set `scale_x` as `1` or something near `1` (like `1.25`). Multiple scales can be used, if you have dots of very different sizes. `cutoff_x` is a threshold applied on the actual filter reponse to get the binary result. Smaller `cutoff_x` may yielf more dots and fatter segmentation, while larger `cutoff_x` could be less permisive and yield less dots and slimmer segmentation. 

**Return**: a 3d numpy array of 0 and 1

----
<a name='s3'>`dot_3d_wrapper`</a>

apply 3D spot filter

```python
from aicssegmentation.core.seg_dot import dot_3d_wrapper
bw = dot_3d_wrapper(smooth_img, s3_param)
```
**Parameters**:
1. smooth_img: a 3d numpy array, usually the image after smoothing
2. s3_param= [[scale_1, cutoff_1], [scale_2, cutoff_2], ....], e.g. `[[1, 0.1]]` or `[[1,0.12], [3,0.1]]`:
    `scale_x` is set based on the estimated radius of your target dots. For example, if visually the diameter of the dots is usually 3~4 pixels, then you may want to set `scale_x` as `1` or something near `1` (like `1.25`). Multiple scales can be used, if you have dots of very different sizes. `cutoff_x` is a threshold applied on the actual filter reponse to get the binary result. Smaller `cutoff_x` may yielf more dots and fatter segmentation, while larger `cutoff_x` could be less permisive and yield less dots and slimmer segmentation. 

**Return**: a 3d numpy array of 0 and 1

----
<a name='MO'>`MO`</a>

Masked-object (MO) thresholding: The basic idea is to apply a relatively low global threshold to roughly mask out each individual object, and then apply a relatively high threshold within each object. This is meant to handle intensity variation from cell to cell. In general, triangle method and median method are two thresholding algorithms usually yield relatively low threshold. Otsu is used within each object for the relatively high threshold.

```python
from aicssegmentation.core.MO_threshold import MO
bw, object_for_debug = MO(structure_img_smooth, global_thresh_method, object_minArea, return_object)
```

**Parameters**

1. `global_thresh_method`: Support `'tri'`, `'med'`,`'ave'` in current version. `'tri'` is triangle method, `'med'` is median method, `'ave'` is the average of the values returned by triangle method and median method.
2. `object_minArea`: The minimal area of connected components after global thresholding to be considered as valid objects. Due to some background noise there could be some small connected components in the global thresholding result. Doing Otsu thresholding within such regions will certainly result in errors. So, we want remove them before doing thresholding within each object

----

<a name='watershed'>`Watershed`</a>

```python
from skimage.morphology import watershed
seg = watershed(watershed_image, markers, mask, watershed_line)
```

Perform watershed transformation, see [doc on skimage](http://scikit-image.org/docs/0.15.x/api/skimage.morphology.html#skimage.morphology.watershed) for details. 

#### Option 1: use watershed to cut merged objects

```python
from skimage.morphology import watershed, dilation, ball
from skimage.feature import peak_local_max
from skimage.measure import label
from scipy.ndimage import distance_transform_edt

seed = dilation(peak_local_max(normalized_img, labels=label(preliminary_segmentation), min_distance=2, indices=False), selem=ball(1))
watershed_map = -1*distance_transform_edt(preliminary_segmentation)
seg = watershed(watershed_map, markers=label(seed), mask=preliminary_segmentation, watershed_line=True)
```

In this example, `preliminary_segmentation` is a binary image where some objects are falsely merged. `normalized_img` is the image after intensity normalization. The watershed is applied on the distance transform of `preliminary_segmentation` with the local maximum on `normalized_img` as the seeds for cutting the objects. `seed` may also be obtained in different ways.

#### Option 2: use watershed to segment shell-like structures

```python
from skimage.morphology import watershed, dilation, ball
from skimage.measure import label
seg_filled = watershed(normalized_img, markers=label(seed), watershed_line=True)
seg_shell = np.logical_xor(seg_filled, dilation(seg_filled, selem=ball(1)))
```

In this example, `normalized_img` is the image after intensity normalization. `seed` is an image with one connected component as one seed for a particular object. Suppose the structure to be segmented has shell-like shape, i.e., brighter rings and dimmer inside. The `watershed` transformation will return the segmentation of each object but with filled inside. A `logical_xor` can be used to get a one-voxel thick shell.

---
---

## Post-processing

---

<a name='remove_small_objects'>`remove_small_objects`</a>

perform size filtering

```python
from skimage.morphology import remove_small_objects
final_seg = remove_small_objects(seg>0, min_size=minArea, connectivity=1, in_place=False)
```

see [doc on skimage](http://scikit-image.org/docs/dev/api/skimage.morphology.html#skimage.morphology.remove_small_objects)

---

<a name='hole_filling'>`hole_filling`</a>

Fill holes in 2D/3D segmentation

```python
from aicssegmentation.utils import hole_filling
bw_filled = hole_filling(bw, hole_min, hole_max, fill_2d=True)
```

**Parameters**:
1. bw: a binary 2D/3D image.
2. hole_min: the minimum size of the holes to be filled
3. hole_max: the maximum size of the holes to be filled
4. fill_2d: if `fill_2d=True`, a 3D image will be filled slice by slice. If you think of a hollow tube alone z direction, the inside is not a hole under 3D topology, but the inside on each slice is indeed a hole under 2D topology. 

--- 
<a name=tpt'>`topology_preserving_thinning`</a>

perform thinning on segmentation without breaking topology

```python
from aicssegmentation.utils import topology_preserving_thinning
bw_thin = topology_preserving_thinning(bw>0, thin_dist_preserve, thin_dist)
```

**Parameters**:
1. `thin_dist_preserve`: Half of the minimum width you want to keep from being thinned. For example, when the object width is smaller than 4, you don't want to make this part even thinner (may break the thin object and alter the topology), you can set `thin_dist_preserve` as `2`.
2. `thin_dist`: the amount to thin (has to be an positive integer). The number of pixels to be removed from outter boundary towards center.

----
----

## Auxillary functions

<a name='suggest_normalization_param'>`suggest_normalization_param`</a>

suggest scaling parameter assuming `img` is a representative example image of this cell structure 

```python
from aicssegmentation.core.pre_processing_utils import suggest_normalization_param
suggest_normalization_param(img)
```

**Parameter**:
1. img: a 3d numpy array

**Return**: suggested parameters for `intensity_normalization` and other useful information will be printed out on console.

---

<a name='get_middle_frame'>`get_middle_frame`</a>

estimate the index of the center slice of the colony (e.g, an image with 70 z-slices and cells mostly in slice 30-60 should have 45 as the center slice of the colony instead of 70/2=35)

```python
from aicssegmentation.utils import get_middle_frame
mid_z = get_middle_frame(structure_img_smooth, method='intensity')
```

We support two methods to get middle frame: `method='intensity'` and `method='z'`. `'intensity'` method assumes the number of foreground pixels (estimated by intensity) along z dimension has a unimodal distribution (such as Gaussian). Then, the middle frame is defined as the frame with peak of the distribution along z. `'z'` method simply return the middle z frame.

---
<a name='seed'>`get_3dseed_from_mid_frame`</a>

build a 3D seed image from the binary segmentation of a single slice

```python 
from aicssegmentation import get_3dseed_from_mid_frame
seed = get_3dseed_from_mid_frame(bw2d, shape_3d, frame_index, area_min, bg_seed)
```

**Parameters**
1. bw2d: the 2d segmentation of a single frame
2. shape_3d: the shape of original 3d image, e.g. `shape_3d = img.shape`
3. frame_index: the index of where `bw2d` is from the whole z-stack
4. area_min: any connected component in `bw2d` with size smaller than `area_min` will be excluded from seed image generation
5. bg_seed: `bg_seed=True` will add a background seed at the first frame (z=0).