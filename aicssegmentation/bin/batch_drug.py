#!/usr/bin/env python

import numpy as np
import os
import sys
import logging
import argparse
import traceback
import unicodedata

from argparse import ArgumentParser
from aicsimage import processing, io
from scipy import ndimage as ndi
from skimage.morphology import remove_small_objects
from skimage.measure import label
from skimage import io as skio
from tifffile import imsave

import numba as nb 

def normalize_caseless(text):
    return unicodedata.normalize("NFKD", text.casefold())

def caseless_equal(left, right):
    return normalize_caseless(left) == normalize_caseless(right)

###############################################################################
# Global Objects

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
        p.add_argument('--output_dir', dest='output_dir',
                       help='output directory')


        subparsers = p.add_subparsers(dest='mode')
        subparsers.required = True
        
        parser_img = subparsers.add_parser('per_img')
        parser_img.add_argument('--input',  dest='input_fname',
                       help='input filename')
        parser_img.add_argument('--structure_type',  type=int, dest='structure_type',
                       help='structure name as 1-digit code, 1-8')
        parser_img.add_argument('--drug_type',  type=int, dest='drug_type',
                       help='drug name as 1-digit code, 0-5')
        parser_img.add_argument('--str_ch',  type=int, dest='structure_ch',
                       help='index of the structure channel')

        parser_dir = subparsers.add_parser('per_csv')
        parser_dir.add_argument('--input_dir',  dest='input_dir',
                       help='filepath to the meta-spreadsheet')
        
        
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
        print('good')

    def execute(self):

        ##########################################################################
        if args.mode=='per_img':
            
            fname = os.path.basename(os.path.splitext(args.input_fname)[0])
            print(fname)

            reader = io.cziReader.CziReader(args.input_fname)
            img = reader.load()
            img = np.squeeze(img, axis=0)
            img = img.astype(np.float32)

            struct_img = img[:,args.structure_ch,:,:]

            if args.structure_type == 1: # ACTB
                from python_image_analysis.seg_actb import ACTB as SegModule
            elif args.structure_type == 2: # DSP
                from python_image_analysis.seg_dsp import DSP as SegModule
            elif args.structure_type == 3: # golgi
                from python_image_analysis.seg_golgi import ST6GAL1 as SegModule
            elif args.structure_type == 4: # lamp1
                from python_image_analysis.seg_lamp1 import LAMP1 as SegModule
            elif args.structure_type == 5: # myosin
                from python_image_analysis.seg_myosin import MYH10 as SegModule
            elif args.structure_type == 6: # sec61b
                from python_image_analysis.seg_sec61 import SEC61B as SegModule
            elif args.structure_type == 7:  #tubulin
                from python_image_analysis.seg_tubulin import TUBA1B as SegModule
            elif args.structure_type == 8: # ZO1
                from python_image_analysis.seg_zo1 import ZO1 as SegModule
            else: 
                print('unsupported structure type')
                quit()

            bw = SegModule(struct_img, args.drug_type)
            bw = bw.astype(np.uint8)
            bw[bw>0]=255
            nm = args.output_dir + 'seg_'+ str(args.structure_type) + '_' + str(args.drug_type) + '_' + fname + '.tiff'
            imsave(nm, bw)

        elif args.mode=='per_csv':
            from python_image_analysis.seg_actb import ACTB
            from python_image_analysis.seg_dsp import DSP
            from python_image_analysis.seg_golgi import ST6GAL1
            from python_image_analysis.seg_lamp1 import LAMP1 
            from python_image_analysis.seg_myosin import MYH10 
            from python_image_analysis.seg_sec61 import SEC61B 
            from python_image_analysis.seg_tubulin import TUBA1B 
            from python_image_analysis.seg_zo1 import ZO1 
            import pandas as pd 

            df = pd.read_csv(args.input_dir)
            
            for idx in range(len(df)):
                filename = df['link'].iloc[idx]

                fname = os.path.basename(os.path.splitext(filename)[0])

                reader = io.cziReader.CziReader(filename)
                img = reader.load()
                img = np.squeeze(img, axis=0)
                img = img.astype(np.float32)

                #TODO: another column in csv for strucutre channel index
                struct_img = img[:,3,:,:]

                structure_name = df['structure'].iloc[idx]
                if caseless_equal(df['well'].iloc[idx], 'Vehicle'):
                    drug_type = 0 
                elif caseless_equal(df['drug'].iloc[idx], 'Brefeldin'):
                    drug_type = 1
                elif caseless_equal(df['drug'].iloc[idx], 'Paclitaxol'):
                    drug_type = 2
                elif caseless_equal(df['drug'].iloc[idx], 'Staurosporine'):
                    drug_type = 3
                elif caseless_equal(df['drug'].iloc[idx], 's-Nitro-Blebbistatin'):
                    drug_type = 4
                elif caseless_equal(df['drug'].iloc[idx], 'Rapamycin'):
                    drug_type = 5
                else: 
                    print('error in understanding drug type')
                    print(df['drug'].iloc[idx])
                    quit()

                if structure_name == 'beta-actin': # ACTB
                    bw = ACTB(struct_img, drug_type)
                elif structure_name == 'desmoplakin': # DSP
                    bw = DSP(struct_img, drug_type)
                elif structure_name == 'golgi': # golgi
                    bw = ST6GAL1(struct_img, drug_type)
                elif structure_name == 'lamp1': # lamp1
                    bw = LAMP1(struct_img, drug_type)
                elif structure_name == 'myosin': # myosin
                    bw = MYH10(struct_img, drug_type)
                elif structure_name == 'sec61b': # sec61b
                    bw = SEC61B(struct_img, drug_type)
                elif structure_name == 'tubulin':  #tubulin
                    bw = TUBA1B(struct_img, drug_type)
                elif structure_name == 'zo1': # ZO1
                    bw = ZO1(struct_img, drug_type)
                else: 
                    print('error in understanding structure name')
                    print(df['structure'].iloc[idx])
                    quit()
            
                bw = bw.astype(np.uint8)
                bw[bw>0]=255
                if drug_type == 0:
                    nm = args.output_dir + 'seg_'+ structure_name + '_Vehicle_' + fname + '.tiff'
                else:
                    nm = args.output_dir + 'seg_'+ structure_name + '_'+ df['drug'].iloc[idx] +'_' + fname + '.tiff'
                imsave(nm, bw)
       
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