set WFNAME=lmnb1_interphase
set INPUTCH=0
set OUTPUTDIR="C:\\Users\\Foo Yoo\\Desktop\\LMNB1_images\\out\\"
set INPUTFILE_TYPE=.tiff
: script for processing a whole folder (ENV_name is the name of your conda environment)
set INPUTDIR="C:\\Users\\Calysta Yan\\Desktop\\Allen Institute\\FISH_CAAX_images\\BMPER\\"
activate ENV_name && python batch_processing.py --d --workflow_name %WFNAME% --struct_ch %INPUTCH% --output_dir %OUTPUTDIR%  per_dir --input_dir %INPUTDIR% --data_type %INPUTFILE_TYPE% && pause || pause
