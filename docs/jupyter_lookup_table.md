# Documentation for Users

We recommend that users start by

Identifying a structure in the lookup table that looks most similar to the segmentation task that you are faced with. Once you have identified this structure, open the correspoinding Jupyter Notebook and follow the instructions in the notebook to tune the workflow for your particular task. Finally, after finalizing the algorithms and parameters in the workflow, modify batch_pipeline.py to batch process all data (file by file or folder by folder).


## Step 1: Find the entry in the lookup table with most similar morphology to your data


List of "playgrounds" accomoanying the lookup table:

1. playground_st6gal.ipynb: workflow for Sialyltransferase 1
2. playground_spotty.ipynb: workflow for Fibrillarin, Beta catenin
3. playground_npm1.ipynb: workflow for Nucleophosmin
4. playground_curvi.ipynb: workflows for Sec61 beta, Tom 20, Lamin B1 (mitosis-specific)
5. playground_lamp1.ipynb: workflow for LAMP-1
6. playground_dots.ipynb: workflows for Centrin-2, Desmoplakin, and PMP34
7. playground_gja1.ipynb: workflow for Connexin-43
8. playground_filament3d.ipynb: workflows for Tight junction protein ZO1, Beta actin, Non-muscle myosin IIB, Alpha-actinin-1, Alpha tubulin, Troponin I, and Titin
9. playground_shell.ipynb: workflow for Lamin B1 (Interphase-specific)

For example, if your structure is localized to endosomes (such as Ras-related protein Rab-5A)

![rab5a raw](./rab5a_raw.jpg)

Visually, it has similar morphology to peroxisomes (peroxisomal membrane protein PMP34). Thusm the most applicable Jupyter Notebook is playground_dots.ipynb

## Step 2: Go to the Jupyter Notebook and tune the workflow

First, start your Jupyter Notebook App.

```bash
source activate segmentation
cd PATH/TO/aics-segmentation/lookup_table_demo
jupyter notebook
```

(Note: change the conda environment name and github repository path accordingly)

Now, your Jupyter should have started in your default brower and you can open "playground_dots.ipynb

(A quick start guide on how executing a notebook can be found [here](https://jupyter-notebook-beginner-guide.readthedocs.io/en/latest/execute.html#executing-a-notebook))

Follow the instruct embedded in the notebook to tune the workflow for segmenting your images

## Step 3: build a batch processing scripts using the segmentation workflow you just tuned

If you need to consistently segment more than a few images similar to the one you just experimented with, you can easily build a batch processing program following the steps below.

For example, you have finalize your segmentation workflow for Rab-5A.

1. duplicate the template file in `/aics-segmentation/aicssegmentation/structure_wrapper/seg_template.py` as `/aics-segmentation/aicssegmentation/structure_wrapper/seg_RAB5A.py`

2. Open seg_RAB5A.py

3. Change the function name from `TEMPLATE_HiPSC_Pipeline()` to `RAB5A_HiPSC_Pipeline()` on line 12

4. insert you parameters and functions at the placeholders (searching `#ADD-HERE` in the code). You can also check the other files under structure_wrapper to see examples.

5. Save the file.

6. go to `aics-segmentation/aicssegmentation/bin/batch_pipeline.py`

7. On line 43, change `'TEMPLATE': {'module': 'aicssegmentation.structure_wrapper.seg_template', 'class': 'TEMPLATE_Cardio_Pipeline'}` into `'RAB5A': {'module': 'aicssegmentation.structure_wrapper.seg_RAB5A', 'class': 'RAB5A_Cardio_Pipeline'}`

8. Process your data with run_toolkit.sh. (Make sure you change the file path to your data inside this script.)

```bash
cd /aics-segmentation/aicssegmentation/bin/
./run_toolkit.sh
```