###### import functions ####


#### do not remove ####
from aicssegmentation.core.output_utils import  save_segmentation, generate_segmentation_contour

def Workflow_template(struct_img, rescale_ratio, output_type, output_path, fn, output_func=None):
    ##########################################################################
    # PARAMETERS:


    ##########################################################################

    ###################
    # PRE_PROCESSING 
    # make sure the variable name of original image is 'struct_img'
    ###################
    # intenisty normalization 


    # smoothing 


    ###################
    # core algorithm
    ###################


    ###################
    # POST-PROCESSING 
    # make sure the variable name of final segmentation is 'seg'
    ###################
    
    

    ##########################################################################
    ### no need to change below
    ##########################################################################
    # output
    seg = seg>0
    seg = seg.astype(np.uint8)
    seg[seg>0]=255

    if output_type == 'default': 
        # the default final output
        save_segmentation(seg, False, output_path, fn)
    elif output_type == 'array':
        return seg
    elif output_type == 'array_with_contour':
        return (seg, generate_segmentation_contour(seg))
    else:
        print('your can implement your output hook here, but not yet')
        quit()



