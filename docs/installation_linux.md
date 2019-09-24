# Installation Instruction for Linux

(tested on Ubuntu 16.04.5)


## Step 1: Setup conda environment 

[What is conda and anaconda, and why we need this?](conda_why.md) Because conda can effectively manage environment and package installation, setting up conda will make the following steps straightforward and help avoid future problems (conda itself is also very easy to set up).

#### 1. [Install conda on Linux](https://docs.conda.io/projects/conda/en/latest/user-guide/install/linux.html), choose anaconda installer.


#### 2. [Start conda](https://docs.conda.io/projects/conda/en/latest/user-guide/getting-started.html#starting-conda)

All commands below are typed in the Terminal window

#### 3. Create a new empty conda environment, which we will name "segmentation" (You can certainly choose a different name.)

``` bash 
conda create -n segmentation python=3.6
```

#### 4. Activate your new conda environment "segmentation"

``` bash
conda activate segmentation
```

(For older version conda, the command is `source activate segmentation`.)

#### 5. Now, you are in "segmentation" environment. You can install the package following the steps below.


## Step 2: Clone the github repository 


#### 1. Check if you have git installed.

```bash 
git --version
```

If you don't have git, follow [Git for Linux](https://www.atlassian.com/git/tutorials/install-git#linux) to install.

#### 2. Clone aics-segmentation repository from Github (suppose you want to save the folder under '~/Projects')

```bash
cd ~/Projects
git clone https://github.com/AllenInstitute/aics-segmentation.git
```

## Step 3: Install the package

### Option 1: Build from source (recommended)

```bash
cd ~/Projects/aics-segmentation
pip install numpy
pip install -e .
pip install itkwidgets==0.14.0
```

For Jupyter Lab users, the itk viewer requires additionally run:

```
jupyter labextension install @jupyter-widgets/jupyterlab-manager itk-jupyter-widgets
```

### Option 2: Install from PyPi (useful when running on a server/cluster)

```bash
pip install aicssegmentation
```


## Step 4: Test jupyter notebook demo


``` bash 
cd ~/Projects/aics-segmentation/lookup_table_demo
jupyter notebook
```

This will take you to your default browser (e.g., Firefox) and launch Jupyter Notebook App within your browser. Open "demo_TNNI1.ipynb" and test if you can run the notebook from beginning to the end. See more details on [How to use Jupyter Notebook to running the workflow in the Look-up Table](../docs/jupyter_lookup_table.md)