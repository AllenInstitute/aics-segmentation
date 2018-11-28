import aicsimageio
import numpy as np



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

#### general hook for cutomized output ######
def output_hook(im, names, out_flag, output_path, fn):
    assert len(im) == len(names) and len(names) == len(out_flag)

    for i in range(len(out_flag)):
        if out_flag[i]:
            if names[i].startswith('bw_'):
                segmentation_type = names[i]
                bw = im[i].astype(np.uint8)
                bw[bw>0]=255
                writer = aicsimageio.omeTifWriter.OmeTifWriter(str(output_path / (fn + '_bw_' + segmentation_type[3:] + '.tiff')))
                writer.save(bw)
            else:
                writer = aicsimageio.omeTifWriter.OmeTifWriter(str(output_path / (fn + '_' + names[i] + '.tiff')))
                writer.save(im[i])

def paperFigure(out_img_list, out_name_list, output_type, output_path, fn):
    out_flag = []
    for i in range(len(out_name_list)):
        if out_name_list[i] == 'im_smooth':
            out_flag.append(True)
        else:
            out_flag.append(False)

    out_flag[-1] = True # also output the last one (always the final result)
    out_name_list[-1] = 'struct_segmentation' # use default name
    output_hook(out_img_list, out_name_list, out_flag, output_path, fn)


def FBL_output(out_img_list, out_name_list, output_type, output_path, fn):
    if output_type == 'AICS_RnD':
        out_flag = []
        for i in range(len(out_name_list)):
            if out_name_list[i] == 'bw_coarse':
                out_flag.append(True)
                bw = out_img_list[i].astype(np.uint8)
                bw[bw>0]=255
                out_img_list[i] = bw
                out_name_list[i] = 'struct_segmentation_coarse' # use default name
            elif out_name_list[i] == 'bw_fine':
                out_flag.append(True)
                bw = out_img_list[i].astype(np.uint8)
                bw[bw>0]=255
                out_img_list[i] = bw
                out_name_list[i] = 'struct_segmentation_fine' # use default name
            else:
                out_flag.append(False)

        output_hook(out_img_list, out_name_list, out_flag, output_path, fn)


def ACTN1_output(out_img_list, out_name_list, output_type, output_path, fn):

    if output_type == 'AICS_RnD':
        paperFigure(out_img_list, out_name_list, output_type, output_path, fn)

def ACTB_output(out_img_list, out_name_list, output_type, output_path, fn):

    if output_type == 'AICS_RnD':
        paperFigure(out_img_list, out_name_list, output_type, output_path, fn)

def CETN2_output(out_img_list, out_name_list, output_type, output_path, fn):

    if output_type == 'AICS_RnD':
        paperFigure(out_img_list, out_name_list, output_type, output_path, fn)

def DSP_output(out_img_list, out_name_list, output_type, output_path, fn):

    if output_type == 'AICS_RnD':
        paperFigure(out_img_list, out_name_list, output_type, output_path, fn)

def RAB5A_output(out_img_list, out_name_list, output_type, output_path, fn):

    if output_type == 'AICS_RnD':
        paperFigure(out_img_list, out_name_list, output_type, output_path, fn)

def SLC25A17_output(out_img_list, out_name_list, output_type, output_path, fn):

    if output_type == 'AICS_RnD':
        paperFigure(out_img_list, out_name_list, output_type, output_path, fn)

def ACTB_output(out_img_list, out_name_list, output_type, output_path, fn):

    if output_type == 'AICS_RnD':
        paperFigure(out_img_list, out_name_list, output_type, output_path, fn)

def GJA1_output(out_img_list, out_name_list, output_type, output_path, fn):

    if output_type == 'AICS_RnD':
        paperFigure(out_img_list, out_name_list, output_type, output_path, fn)

def LAMP1_output(out_img_list, out_name_list, output_type, output_path, fn):

    if output_type == 'AICS_RnD':
        paperFigure(out_img_list, out_name_list, output_type, output_path, fn)

def NPM1_output(out_img_list, out_name_list, output_type, output_path, fn):

    if output_type == 'AICS_RnD':
        out_flag = []
        for i in range(len(out_name_list)):
            if out_name_list[i] == 'bw_coarse':
                out_flag.append(True)
                bw = out_img_list[i].astype(np.uint8)
                bw[bw>0]=255
                out_img_list[i] = bw
                out_name_list[i] = 'struct_segmentation_coarse' # use default name
            elif out_name_list[i] == 'bw_fine':
                out_flag.append(True)
                bw = out_img_list[i].astype(np.uint8)
                bw[bw>0]=255
                out_img_list[i] = bw
                out_name_list[i] = 'struct_segmentation_fine' # use default name
            else:
                out_flag.append(False)

        output_hook(out_img_list, out_name_list, out_flag, output_path, fn)


def SEC61B_output(out_img_list, out_name_list, output_type, output_path, fn):

    if output_type == 'AICS_RnD':
        paperFigure(out_img_list, out_name_list, output_type, output_path, fn)

def ST6GAL1_output(out_img_list, out_name_list, output_type, output_path, fn):

    if output_type == 'AICS_RnD':
        paperFigure(out_img_list, out_name_list, output_type, output_path, fn)

def MYH10_output(out_img_list, out_name_list, output_type, output_path, fn):

    if output_type == 'AICS_RnD':
        paperFigure(out_img_list, out_name_list, output_type, output_path, fn)

def TOMM20_output(out_img_list, out_name_list, output_type, output_path, fn):

    if output_type == 'AICS_RnD':
        paperFigure(out_img_list, out_name_list, output_type, output_path, fn)

def TUBA1B_output(out_img_list, out_name_list, output_type, output_path, fn):

    if output_type == 'AICS_RnD':
        paperFigure(out_img_list, out_name_list, output_type, output_path, fn)

def TJP1_output(out_img_list, out_name_list, output_type, output_path, fn):

    if output_type == 'AICS_RnD':
        paperFigure(out_img_list, out_name_list, output_type, output_path, fn)

def CTNNB1_output(out_img_list, out_name_list, output_type, output_path, fn):

    if output_type == 'AICS_RnD':
        paperFigure(out_img_list, out_name_list, output_type, output_path, fn)

def MYL7_Cardio_output(out_img_list, out_name_list, output_type, output_path, fn):

    if output_type == 'AICS_RnD':
        paperFigure(out_img_list, out_name_list, output_type, output_path, fn)

def ATP2A2_Cardio_output(out_img_list, out_name_list, output_type, output_path, fn):

    if output_type == 'AICS_RnD':
        paperFigure(out_img_list, out_name_list, output_type, output_path, fn)

def TTN_Cardio_output(out_img_list, out_name_list, output_type, output_path, fn):

    if output_type == 'AICS_RnD':
        paperFigure(out_img_list, out_name_list, output_type, output_path, fn)

def TNNI1_Cardio_output(out_img_list, out_name_list, output_type, output_path, fn):

    if output_type == 'AICS_RnD':
        paperFigure(out_img_list, out_name_list, output_type, output_path, fn)

def ACTN2_Cardio_output(out_img_list, out_name_list, output_type, output_path, fn):

    if output_type == 'AICS_RnD':
        paperFigure(out_img_list, out_name_list, output_type, output_path, fn)
