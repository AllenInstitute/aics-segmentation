#!/usr/bin/env bash

WFNAME=lamin_interphase
INPUTCH=0
OUTPUTDIR="/home/data/structures/$WFNAME/result/"
INPUTFILE_TYPE='.czi'

# script for processing a whole folder
INPUTDIR="../../data/structures/$WFNAME/original/"

python batch_pipeline.py \
        --d \
        --workflow_name $WFNAME \
        --struct_ch $INPUTCH \
        --output_dir $OUTPUTDIR \
        per_dir \
        --input_dir $INPUTDIR \
        --data_type $INPUTFILE_TYPE
