#!/usr/bin/env bash

STRNAME=RAB5
INPUTCH=3
OUTPUT_TYPE="default"
OUTPUTDIR="../../data/structures/$STRNAME/result/"
INPUTFILE_TYPE='czi'
XY=0.108 # parameter to control image resizing

# script for processing a whole folder
INPUTDIR="../../data/structures/$STRNAME/original/"

python batch_pipeline.py \
        --d \
        --struct_name $STRNAME \
        --struct_ch $INPUTCH \
        --xy $XY \
        --output_dir $OUTPUTDIR \
        --use $OUTPUT_TYPE \
        per_dir \
        --input_dir $INPUTDIR \
        --data_type $INPUTFILE_TYPE

# script for processing a single file
INPUTFILE="../../data/structures/$STRNAME/original/test_img.czi"

python batch_pipeline.py \
        --d \
        --struct_name $STRNAME \
        --struct_ch $INPUTCH \
        --xy $XY \
        --output_dir $OUTPUTDIR \
        --use $OUTPUT_TYPE \
        per_img \
        --input $INPUTFILE \