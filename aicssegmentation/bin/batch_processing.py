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

'''
STRUCTURE_MAPPING = {
    'DSP': {'module': 'aicssegmentation.structure_wrapper.seg_dsp', 'class': 'DSP_HiPSC_Pipeline'},             # version 1.1.1
    'SEC61B': {'module': 'aicssegmentation.structure_wrapper.seg_sec61b', 'class': 'SEC61B_HiPSC_Pipeline'},    # version 1.1.2
    'ST6GAL1': {'module': 'aicssegmentation.structure_wrapper.seg_st6gal1', 'class': 'ST6GAL1_HiPSC_Pipeline'},  # version 1.2.0
    'TUBA1B': {'module': 'aicssegmentation.structure_wrapper.seg_tuba1b', 'class': 'TUBA1B_HiPSC_Pipeline'},    # version 1.1.2
    'TOMM20': {'module': 'aicssegmentation.structure_wrapper.seg_tomm20', 'class': 'TOMM20_HiPSC_Pipeline'},    # version 1.1.2
    'CETN2': {'module': 'aicssegmentation.structure_wrapper.seg_cetn2', 'class': 'CETN2_HiPSC_Pipeline'},   # version 1.1.0
    'FBL': {'module': 'aicssegmentation.structure_wrapper.seg_fbl', 'class': 'FBL_HiPSC_Pipeline'},         # version 1.1.3
    'ACTN1': {'module': 'aicssegmentation.structure_wrapper.seg_actn1', 'class': 'ACTN1_HiPSC_Pipeline'},   # version 1.1.3  
    'TJP1': {'module': 'aicssegmentation.structure_wrapper.seg_tjp1', 'class': 'TJP1_HiPSC_Pipeline'},   # version 1.1.1
    'ACTB': {'module': 'aicssegmentation.structure_wrapper.seg_actb', 'class': 'ACTB_HiPSC_Pipeline'},   # version 1.2.0
    'MYH10': {'module': 'aicssegmentation.structure_wrapper.seg_myh10', 'class': 'MYH10_HiPSC_Pipeline'}, # version 1.2.0
    'CTNNB1': {'module': 'aicssegmentation.structure_wrapper.seg_ctnnb1', 'class': 'CTNNB1_HiPSC_Pipeline'}, # version 1.1.0
    'GJA1': {'module': 'aicssegmentation.structure_wrapper.seg_gja1', 'class': 'GJA1_HiPSC_Pipeline'}, # version 1.1.0
    'NPM1': {'module': 'aicssegmentation.structure_wrapper.seg_npm1', 'class': 'NPM1_HiPSC_Pipeline'}, # version 1.1.0
    'LAMP1': {'module': 'aicssegmentation.structure_wrapper.seg_lamp1', 'class': 'LAMP1_HiPSC_Pipeline'}, # version 1.1.0
    'RAB5A': {'module': 'aicssegmentation.structure_wrapper.seg_rab5a', 'class': 'RAB5A_HiPSC_Pipeline'}, # version 1.0.0
    'SLC25A17': {'module': 'aicssegmentation.structure_wrapper.seg_slc25a17', 'class': 'SLC25A17_HiPSC_Pipeline'}, # version 1.2.0
    'PXN': {'module': 'aicssegmentation.structure_wrapper.seg_pxn', 'class': 'PXN_HiPSC_Pipeline'}, # version 1.0.0
    'TNNI1_Cardio': {'module': 'aicssegmentation.structure_wrapper.seg_cardio_tnni1', 'class': 'TNNI1_Cardio_Pipeline'},
    'TTN_Cardio': {'module': 'aicssegmentation.structure_wrapper.seg_cardio_ttn', 'class': 'TTN_Cardio_Pipeline'},
    'ATP2A2_Cardio': {'module': 'aicssegmentation.structure_wrapper.seg_cardio_atp2a2', 'class': 'ATP2A2_Cardio_Pipeline'},
    'MYL7_Cardio': {'module': 'aicssegmentation.structure_wrapper.seg_cardio_myl7', 'class': 'MYL7_Cardio_Pipeline'},
    'ACTN2_Cardio': {'module': 'aicssegmentation.structure_wrapper.seg_cardio_actn2', 'class': 'ACTN2_Cardio_Pipeline'}
}
'''


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
        p.add_argument('--struct_name', dest='struct_name', default='skip',
                       help='Legacy Option for backward compatibility] use workflow_name instead')
        p.add_argument('--workflow_name', dest='workflow_name', default='template',
                       help='the name of your workflow')        
        p.add_argument('--struct_ch', default=3, type=int, dest='struct_ch',
                       help='the index of the structure channel of the image file, default is 3')
        p.add_argument('--xy', default=0.108, type=float, dest='xy',
                       help='the xy resolution of the image, default is 0.108')
        p.add_argument('--rescale', default=-1, type=float, dest='rescale',
                       help='the rescale ratio for x/y dimenstions, will overwrite --xy')
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

        standard_xy = 0.108

        if args.rescale>0:
            self.rescale_ratio = args.rescale
        else:
            if args.xy != standard_xy:
                self.rescale_ratio = args.xy / standard_xy
            else:
                self.rescale_ratio = -1

    def execute(self, args):

        if not args.struct_name == 'skip':
            if not args.workflow_name == 'template':
                print('only use either workflow_name or struct_name, should use both.')
                quit()
            args.workflow_name = args.struct_name
        
        try:
            module_name = 'aicssegmentation.structure_wrapper.seg_' + args.workflow_name
            seg_module = importlib.import_module(module_name)
            class_name = 'Workflow_'+ args.workflow_name
            SegModule = getattr(seg_module, class_name)
        except:
            print('{} structure not found'.format(args.workflow_name))
            sys.exit(1)

        output_path = pathlib.Path(args.output_dir)
        
        if not os.path.exists(output_path):
            os.mkdir(output_path)
            
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

            for _, fn in enumerate(filenames):

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
