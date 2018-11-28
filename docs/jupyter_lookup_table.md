# Documentation for Users

A suggested way for using our toolkit is 

(1) check out the lookup table and find an entry in the lookup table where the segmentation tasks is the most similar to yours; for example, you pick Tom20
(2) go to Tom20_demo.ipynb and follow the detailed instruction in the notebook to tune the workflow;
(3) After finalizing the algorithms and parameters in the workflow, modify batch_pipeline.py to batch process all data (file by file or folder by folder).


## step 1: find the entry in the lookup table with most similar morphology to your data

For example, you have Endosomes (Ras-related protein Rab-5A) 

![rab5a raw](./rab5a_raw.jpg)

# Apply Classic Image Segmentation Workflow on Your Own Data (using Jupyter Notebook)

Our goal is you may checkout the lookup table first and find the structure with most similar morphology as the objects in your data. For example, you are also working on the segmentation of some "point-source" structure (i.e., spots-like shapes). You may go to DSP.ipynb to (1) test your data with the algorithm and parameters optimized on our data, (2) follow the instruction coded inside the notebook to tweak the parameters so that it works can also work well on your data.

=============


More contents are coming. 

Right now, you may use ./lookup_table_demo/DSP.ipynb to get some sense of what is inside each notebook. 






