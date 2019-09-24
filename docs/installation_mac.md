# Installation Instruction for MacOS

(tested on XXXXX)


## Step 1: Install XCode

[Download and install XCode from Apple Developer](https://developer.apple.com/xcode/)


## Step 2: Setup conda environment 

[What is conda and anaconda, and why we need this?](conda_why.md) Because conda can effectively manage environment and package installation, setting up conda will make the following steps straightforward and help avoid future problems (conda itself is also very easy to set up).

#### 0. If you already have anaconda installed on your machine, you can double-check your version by

```bash
conda info
```

You may see somthing like
```bash
conda version : 4.6.11
python version : 3.7.3.final.0
```
`conda version > 4.4` is preferred. To update conda, check out [how to update your conda](https://www.anaconda.com/keeping-anaconda-date/).
`python version >=3.6` is required.

#### 1. [Install conda on macOS](https://docs.conda.io/projects/conda/en/latest/user-guide/install/macos.html), choose anaconda installer.


#### 2. [Start conda](https://docs.conda.io/projects/conda/en/latest/user-guide/getting-started.html#starting-conda)

All commands below are typed into the Terminal Window

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


## Step 3: Clone the github repository 


#### 1. Check if you have git installed.

```bash 
git --version
```

If you don't have git, follow [Git for macOS](https://www.atlassian.com/git/tutorials/install-git#mac-os-x) to install.

#### 2. Clone aics-segmentation repository from Github (suppose you want to save the folder under '~/Projects')

```bash
cd ~/Projects
git clone https://github.com/AllenInstitute/aics-segmentation.git
```

## Step 4: Install the package

### Step 4.1: check `pip` version
`pip show pip` will return your version of `pip`. It is recommended to do `pip install --upgrade pip` to keep your `pip` updated. 


### Step 4.2: build the package

```bash
cd ~/Projects/aics-segmentation
pip3 install numpy
pip3 install itkwidgets==0.14.0
pip3 install -e .[all]
```

Note: We use the packge `itkwidgets` for visualizaiotn within jupyter notebook. Currently, we find version `0.14.0` has the slightly better performance in visualizing segmentation results. If you find this viwer keeps crashing in your browser, try `pip3 uninstall itkwidgets` and then `pip3 install itkwidgets==0.12.2`. For JupyterLab users, version >= `0.17.1` is needed. 

For Jupyter Lab users, the itk viewer requires additionally run:

```
jupyter labextension install @jupyter-widgets/jupyterlab-manager itk-jupyter-widgets
```


### Option 2: Build on server/cluster for production:

```bash
pip3 install numpy
pip3 install aicssegmentation
```

## Step 5: Test jupyter notebook demo


``` bash 
cd ~/Projects/aics-segmentation/lookup_table_demo
jupyter notebook
```

This will take you to your default browser (e.g., Safari) and launch Jupyter Notebook App within your browser.Open "demo_TNNI1.ipynb" and test if you can run the notebook from beginning to the end. See more details on [How to use Jupyter Notebook to running the workflow in the Look-up Table](../docs/jupyter_lookup_table.md)

