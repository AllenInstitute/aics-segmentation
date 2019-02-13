#!/usr/bin/env python

import numpy as np
import os
import sys
import logging
import argparse
import traceback
import importlib
import pathlib

import aicsimageio


###############################################################################
# Global Objects
PER_IMAGE = 'per_img'
PER_DIR = 'per_dir'

STRUCTURE_MAPPING = {
    # only keep this file as a template. the actual file should be in a seperate repository
    'DSP': {'module': 'aicssegmentation.structure_wrapper.seg_dsp', 'class': 'DSP_HiPSC_Pipeline'},             # version 1.1.1
    'TEMPLATE': {'module': 'aicssegmentation.structure_wrapper.seg_template', 'class': 'TEMPLATE_Cardio_Pipeline'}
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
        self.output_dir = './'
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
        p.add_argument('--d', '--debug', action='store_true', dest='debug',
                       help='If set debug log output is enabled')
        p.add_argument('--struct_name', required=True, dest='struct_name',
                       help='structure name')
        p.add_argument('--struct_ch', default=3, type=int, dest='struct_ch',
                       help='the index of the structure channel of the image file, default is 3')
        p.add_argument('--xy', default=0.108, type=float, dest='xy',
                       help='the xy resolution of the image, default is 0.108')
        p.add_argument('--output_dir', dest='output_dir',
                       help='output directory')
        p.add_argument('--use', dest='output_type', default='default', 
                        help='how to output the results, options are default, AICS_pipeline, AICS_QCB, AICS_RnD')

        subparsers = p.add_subparsers(dest='mode')
        subparsers.required = True

        parser_img = subparsers.add_parser(PER_IMAGE)
        parser_img.add_argument('--input',  dest='input_fname',
                                help='input filename')

        parser_dir = subparsers.add_parser(PER_DIR)
        parser_dir.add_argument('--input_dir',  dest='input_dir',
                                help='input directory')
        parser_dir.add_argument('--data_type',  default='.czi', dest='data_type',
                                help='the image type to be processed, e.g., .czi (default) or .tiff or .ome.tif')

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
        if args.struct_name.endswith('Cardio'):
            print('using cardio default resolution')
            standard_xy = 0.135
        else:
            print('using pipeline default resolution')
            standard_xy = 0.108
        ##########################################################################

        if args.xy != standard_xy:
            self.rescale_ratio = args.xy / standard_xy
        else:
            self.rescale_ratio = -1

    def execute(self, args):

        if args.struct_name not in STRUCTURE_MAPPING.keys():
            print('{} structure not found'.format(args.struct_name))
            sys.exit(1)
        # Pull module info for this structure
        seg_module_info = STRUCTURE_MAPPING[args.struct_name]
        # Import the module specified for that structure
        seg_module = importlib.import_module(seg_module_info['module'])
        # Pull out the segmentation class from that module
        SegModule = getattr(seg_module, seg_module_info['class'])

        output_path = pathlib.Path(args.output_dir)

        ##########################################################################
        if args.mode == PER_IMAGE:

            fname = os.path.basename(os.path.splitext(args.input_fname)[0])

            image_reader = aicsimageio.AICSImage(args.input_fname)
            img = image_reader.data
            struct_img = img[0, args.struct_ch, :, :, :].astype(np.float32)

            SegModule(struct_img, self.rescale_ratio, args.output_type, output_path, fname)

        elif args.mode == PER_DIR:

            filenames = [os.path.basename(os.path.splitext(f)[0])
                         for f in os.listdir(args.input_dir)
                         if f.endswith(args.data_type)]
            filenames.sort()

            for fi, fn in enumerate(filenames):

                image_reader = aicsimageio.AICSImage(os.path.join(args.input_dir, f'{fn}{args.data_type}'))
                img = image_reader.data
                struct_img = img[0, args.struct_ch, :, :, :].astype(np.float32)

                SegModule(struct_img, self.rescale_ratio, args.output_type, output_path, fn)

###############################################################################


def main():
    dbg = False
    try:
        args = Args()
        dbg = args.debug

        # Do your work here - preferably in a class or function,
        # passing in your args. E.g.
        exe = Executor(args)
        exe.execute(args)

    except Exception as e:
        log.error("=============================================")
        if dbg:
            log.error("\n\n" + traceback.format_exc())
            log.error("=============================================")
        log.error("\n\n" + str(e) + "\n")
        log.error("=============================================")
        sys.exit(1)


if __name__ == "__main__":
    main()
