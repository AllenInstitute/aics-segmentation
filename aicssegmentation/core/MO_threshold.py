import numpy as np
from skimage.morphology import remove_small_objects, binary_closing, ball , dilation
from skimage.filters import threshold_triangle, threshold_otsu
from skimage.measure import label

def MO(structure_img_smooth, global_thresh_method, object_minArea, extra_criteria=False, local_adjust=0.98, return_object=False):

    if global_thresh_method=='tri' or global_thresh_method=='triangle':
        th_low_level = threshold_triangle(structure_img_smooth)
    elif global_thresh_method=='med' or global_thresh_method=='median':
        th_low_level = np.percentile(structure_img_smooth,50)
    elif global_thresh_method=='ave' or global_thresh_method=='ave_tri_med':
        global_tri = threshold_triangle(structure_img_smooth)
        global_median = np.percentile(structure_img_smooth,50)
        th_low_level = (global_tri + global_median)/2

    bw_low_level = structure_img_smooth > th_low_level
    bw_low_level = remove_small_objects(bw_low_level, min_size=object_minArea, connectivity=1, in_place=True)
    bw_low_level = dilation(bw_low_level, selem=ball(2))

    bw_high_level = np.zeros_like(bw_low_level)
    lab_low, num_obj = label(bw_low_level, return_num=True, connectivity=1)
    if extra_criteria:
        local_cutoff = 0.333 * threshold_otsu(structure_img_smooth)
        for idx in range(num_obj):
            single_obj = lab_low==(idx+1)
            local_otsu = threshold_otsu(structure_img_smooth[single_obj>0])
            if local_otsu > local_cutoff:
                bw_high_level[np.logical_and(structure_img_smooth>local_otsu*local_adjust, single_obj)]=1
    else:
        for idx in range(num_obj):
            single_obj = lab_low==(idx+1)
            local_otsu = threshold_otsu(structure_img_smooth[single_obj>0])
            bw_high_level[np.logical_and(structure_img_smooth>local_otsu*local_adjust, single_obj)]=1

    if return_object:
        return bw_high_level>0, bw_low_level
    else:
        return bw_high_level>0
