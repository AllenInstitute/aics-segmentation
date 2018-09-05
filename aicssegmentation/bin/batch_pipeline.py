#!/usr/bin/env python

import numpy as np
import os
import sys
import logging
import argparse
import traceback
import importlib

from argparse import ArgumentParser
from aicsimage import processing, io
from scipy import ndimage as ndi
from skimage.morphology import remove_small_objects
from skimage.measure import label
from skimage import io as skio
from tifffile import imsave


###############################################################################
# Global Objects
PER_IMAGE = 'per_img'
PER_DIR = 'per_dir'

STRUCTURE_MAPPING = {
    'Connexin-43': {'module': 'python_image_analysis.seg_connexin', 'class': 'Connexin_HiPSC_Pipeline'},
    'Nucleophosmin': {'module': 'python_image_analysis.seg_npm', 'class': 'NPM_HiPSC_Pipeline'},
    'alpha-actinin-1': {'module': 'python_image_analysis.seg_actn1', 'class': 'ACTN1_HiPSC_Pipeline'},
    'beta-catenin': {'module': 'python_image_analysis.seg_ctnnb1', 'class': 'BetaCatenin_HiPSC_Pipeline'},
    'Tubulin': {'module': 'python_image_analysis.seg_tubulin', 'class': 'Tubulin_HiPSC_Pipeline'},
    'Sec61B': {'module': 'python_image_analysis.seg_sec61', 'class': 'Sec61B_HiPSC_Pipeline'},
    'Tom20': {'module': 'python_image_analysis.seg_tomm20', 'class': 'TOMM20_HiPSC_Pipeline'},
    'atp2a2_cardio': {'module': 'python_image_analysis.seg_atp2a2', 'class': 'ATP2A2_Cardio'},
    'tom20_cardio': {'module': 'python_image_analysis.seg_tomm20', 'class': 'TOMM20_Cardio'},
    'myosin_cardio': {'module': 'python_image_analysis.seg_myosin', 'class': 'MYH10_Cardio'},
    'Lamp1': {'module': 'python_image_analysis.seg_lamp1', 'class': 'LAMP1_HiPSC_Pipeline'}
}


log = logging.getLogger()
logging.basicConfig(level=logging.INFO,
                    format='[%(levelname)4s:%(lineno)4s %(asctime)s] %(message)s')
#
# Set the default log level for other modules used by this script
# logging.getLogger("labkey").setLevel(logging.ERROR)
# logging.getLogger("requests").setLevel(logging.WARNING)
# logging.getLogger("urllib3").setLevel(logging.WARNING)


###############################################################################

###############################################################################

class Args(object):
    """
    Use this to define command line arguments and use them later.

    For each argument do the following
    1. Create a member in __init__ before the self.__parse call.
    2. Provide a default value here.
    3. Then in p.add_argument, set the dest parameter to that variable name.

    See the debug parameter as an example.
    """

    def __init__(self, log_cmdline=True):
        self.debug = False
        self.input_dir = './'
        self.output_dir = './'
        self.data_type = '.czi'
        self.struct_ch = 0
        self.xy = 0.108

        #
        self.__parse()
        #
        if self.debug:
            log.setLevel(logging.DEBUG)
            log.debug("-" * 80)
            self.show_info()
            log.debug("-" * 80)

    @staticmethod
    def __no_args_print_help(parser):
        """
        This is used to print out the help if no arguments are provided. 
        Note:
        - You need to remove it's usage if your script truly doesn't want arguments.
        - It exits with 1 because it's an error if this is used in a script with no args. 
          That's a non-interactive use scenario - typically you don't want help there.
        """
        if len(sys.argv) == 1:
            parser.print_help()
            sys.exit(1)

    def __parse(self):
        p = argparse.ArgumentParser()
        # Add arguments
        p.add_argument('-d', '--debug', action='store_true', dest='debug',
                       help='If set debug log output is enabled')
        p.add_argument('--struct_name', required=True, dest='struct_name',
                       help='structure name')
        p.add_argument('--struct_ch', default=3, dest='struct_ch',
                       help='the index of the structure channel of the image file, default is 3')
        p.add_argument('--xy', default=0.108, type=float, dest='xy',
                       help='the xy resolution of the image, default is 0.108')
        p.add_argument('--data_type', default='.czi', dest='data_type',
                       help='the image type to be processed, e.g., .czi (default) or .tiff or .ome.tif')
        p.add_argument('--output_dir', dest='output_dir',
                       help='output directory')


        subparsers = p.add_subparsers(dest='mode')
        subparsers.required = True
        
        parser_img = subparsers.add_parser(PER_IMAGE)
        parser_img.add_argument('--input',  dest='input_fname',
                       help='input filename')

        parser_dir = subparsers.add_parser(PER_DIR)
        parser_dir.add_argument('--input_dir',  dest='input_dir',
                       help='input directory')


        self.__no_args_print_help(p)
        p.parse_args(namespace=self)

    def show_info(self):
        log.debug("Working Dir:")
        log.debug("\t{}".format(os.getcwd()))
        log.debug("Command Line:")
        log.debug("\t{}".format(" ".join(sys.argv)))
        log.debug("Args:")
        for (k, v) in self.__dict__.items():
            log.debug("\t{}: {}".format(k, v))


###############################################################################

class Executor(object):

    def __init__(self, args):

        ##########################################################################
        # Algorithm PARAMETERS:
        if args.struct_name.endswith('cardio'):
            print('using cardio default resolution')
            standard_xy = 0.135
        else:
            print('using pipeline default resolution')
            standard_xy = 0.108
        ##########################################################################

        self.data_type = args.data_type
        self.struct_ch = int(args.struct_ch)
        self.output_dir = args.output_dir

        if args.xy != standard_xy:
            self.rescale_ratio = args.xy / standard_xy
        else:
            self.rescale_ratio = -1

    def execute(self):

        if args.struct_name not in STRUCTURE_MAPPING.keys():
            print('{} structure not found'.format(args.struct_name)) 
            sys.exit(1)
        # Pull module info for this structure
        seg_module_info = STRUCTURE_MAPPING[args.struct_name]
        # Import the module specified for that structure
        seg_module = importlib.import_module(seg_module_info['module'])
        # Pull out the segmentation class from that module
        SegModule = getattr(seg_module, seg_module_info['class'])

        ##########################################################################
        if args.mode == PER_IMAGE:
            
            fname = os.path.basename(os.path.splitext(args.input_fname)[0])
            print(fname)

            if args.data_type == '.czi':
                # image = aicsimage.processing.aicsImage.AICSImage(filename)
                # image_data = image.data
                reader = io.cziReader.CziReader(args.input_fname)
                img = reader.load()
                img = np.squeeze(img, axis=0)
                img = img.astype(np.float32)
            else:
                print('error file type, support will be added in the future')

            struct_img = img[:,self.struct_ch,:,:]

            bw = SegModule(struct_img, self.rescale_ratio)
            bw = bw.astype(np.uint8)
            bw[bw>0]=255

            nm = args.output_dir + fname + '_struct_segmentation.tiff'
            imsave(nm, bw, compress=6)

        elif args.mode == PER_DIR:

            filenames = [os.path.basename(os.path.splitext(f)[0])
                for f in os.listdir(args.input_dir) if f.endswith(self.data_type)]
            filenames.sort()

            for fi, fn in enumerate(filenames):

                if args.data_type == '.czi':
                    reader = io.cziReader.CziReader(os.path.join(args.input_dir, f'{fn}{self.data_type}'))
                    img = reader.load()
                    img = np.squeeze(img, axis=0)
                    img = img.astype(float)
                else:
                    # this script is only for pipeline data, so only czi is allowed
                    print('error file type')
                #elif args.data_type == '.tif' or args.data_type == '.tiff':
                #    struct_img = skio.imread(os.path.join(args.input_dir, f'{fn}{args.data_type}')).astype(float)

                struct_img = img[:,self.struct_ch,:,:]

                bw = SegModule(struct_img, self.rescale_ratio)

                bw = bw.astype(np.uint8)
                bw[bw>0]=255

                nm = args.output_dir + fn + '_struct_segmentation.tif'
                imsave(nm, bw,  compress=6)

           
###############################################################################


if __name__ == "__main__":
    dbg = False
    try:
        args = Args()
        dbg = args.debug

        # Do your work here - preferably in a class or function,
        # passing in your args. E.g.
        exe = Executor(args)
        exe.execute()

    except Exception as e:
        log.error("=============================================")
        if dbg:
            log.error("\n\n" + traceback.format_exc())
            log.error("=============================================")
        log.error("\n\n" + str(e) + "\n")
        log.error("=============================================")
        sys.exit(1)