# Installation Instruction for Windows 

(tested on Windows 10 with anaconda)


## Step 0: Install Microscoft Build Tools

*Go to Step 1 if you already have these installed (it is very likely that you already have it, if you have done any python or C++ programming on your machine).*


[Download and install the Build Tools from Microsoft](https://visualstudio.microsoft.com/visual-cpp-build-tools/)

Note 1: Depending on the time you access this page, you may be directed to the download page of "Build Tools for Visual Studio 2017" or "Build Tools for Visual Studio 2018", etc. In general, as long as the version is at least 2015, any subsequent version should work. 

Note 2: When you install the Build Tool, you may be asked to choose what to install. Only the tool for Visual Studio C++ (e.g, pack name: "MSVC v142 - VC 2019 C++") is required for the Allen Cell Segmenter. After installing the Build Tool, make sure to reboot your machine. 

## Step 1: Install conda

*Go to Step 2 if you have anaconda or miniconda installed*

Go to [Install conda on Windows](https://docs.conda.io/projects/conda/en/latest/user-guide/install/windows.html), choose Anaconda Installer (for Python 3) and then follow the installation instructions.

Note: [What is conda and anaconda, and why we need this?](conda_why.md) Because conda can effectively manage environment and package installation, setting up conda will make the following steps straightforward and help avoid future problems (conda itself is also very easy to set up).

## Step 3: Verify requirement and prepare for installing segmenter


#### Step 3.1: [Start conda](https://docs.conda.io/projects/conda/en/latest/user-guide/getting-started.html#starting-conda)

All commands below are typed into Anaconda Prompt window

#### Step 2.2: Test conda version

```bash
conda info
```

You may see somthing like
```bash
conda version : 4.6.11
python version : 3.7.3.final.0
```

`conda version > 4.4` is preferred. To update conda, check out [how to update your conda](https://www.anaconda.com/keeping-anaconda-date/). `python version >=3.6` is required.

#### Step 2.3: Test git

```bash 
git --version
```

If you don't have git, follow [Git for Windows](https://www.atlassian.com/git/tutorials/install-git#windows) to install. It is okay to just use default installation settings. You will need to restart Anaconda Prompt after installing Git.

#### Step 2.4: Test pip

```bash
pip show pip
```

A message will be printed out on your screen. If you see a warning, like a newer version is available, you can follow the instruction to upgrade you pip.

#### Step 2.5: Create a new empty conda environment, which we will name "segmentation" (You can certainly choose a different name.)

``` bash 
conda create -n segmentation python=3.6
```

### Step 2.6: Activate your conda environment "segmentation"

``` bash
conda activate segmentation
```

### Step 2.7: Install nb_conda (for easy conda environment management in jupyter notebook)

```bash
conda install nb_conda
```

## Step 3: Install segmenter

#### Step 3.1: Clone aics-segmentation repository from Github (suppose you want to save the folder under 'C:\Projects')

```bash
cd C:\Projects
git clone https://github.com/AllenInstitute/aics-segmentation.git
```


#### Step 3.2: install the packages

```bash
cd ~/Projects/aics-segmentation
pip install numpy
pip install itkwidgets==0.14.0
pip install -e .[all]
```

Note 1: Please note that for the users with both python 2 and python 3 installed, use `pip3` instead of `pip` in the commands

Note 2: We use the packge `itkwidgets` for visualizaiotn within jupyter notebook. Currently, we find version `0.14.0` has slightly better performance in visualizing segmentation results. If you find this viwer keeps crashing in your browser, try `pip uninstall itkwidgets` and then `pip install itkwidgets==0.12.2`. For JupyterLab users, version >= `0.17.1` is needed.

Note 3: For Jupyter Lab users, the itk viewer requires additionally run:

```
jupyter labextension install @jupyter-widgets/jupyterlab-manager itk-jupyter-widgets
```

Note 4: For advanced user to deploy segmenter on cluster, our package is also [available on PyPi](https://pypi.org/project/aicssegmentation/)

#### Step 3.3: Test segmenter

``` bash 
cd C:\Projects\aics-segmentation\lookup_table_demo
jupyter notebook, choose anaconda installer.
```

This will take you to your default browser (e.g., Chrome) and launch Jupyter Notebook App within your browser. Open "test_viewer.ipynb" and test if you can run the notebook from beginning to the end. See more details on [How to use Jupyter Notebook to running the workflow in the Look-up Table](../docs/jupyter_lookup_table.md)


