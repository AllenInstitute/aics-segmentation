# Installation Instruction for Windows 

(tested on Windows 10 with anaconda)


## Step 1: Install Microscoft Build Tools

[Download and install the Build Tools from Microsoft](https://visualstudio.microsoft.com/visual-cpp-build-tools/)

Note: Depending on the time you access this page, you may be directed to the download page of "Build Tools for Visual Studio 2017" or "Build Tools for Visual Studio 2018", etc. In general, the latest version should be good, as long as the version is at least 2015. 

When you install the Build Tool, you may be asked to choose what to install. You may only select the tool for Visual Studio C++. Also, after intalling the Build Tool, make sure to reboot your machine. 

## Step 2: Setup conda environment 

[What is conda and anaconda, and why we need this?](conda_why.md) In short, setting up conda will make all the following setups straightforward and greatly avoid future problems (conda itself is also very easy to set up).

#### 1. [Install conda on Windows](https://conda.io/docs/user-guide/install/windows.html?highlight=conda), choose anaconda installer.


#### 2. [Start conda on Windows](https://conda.io/docs/user-guide/getting-started.html#starting-conda)

All commands below are typed into Anaconda Prompt window

#### 3. Create a new empty conda environment (suppose we use name "segmentation" for this environment)

``` bash 
conda create -n segmentation python=3.6
```

#### 4. Activate your new conda environment "segmentation"

``` bash
activate segmentation
```

#### 5. Now, you are in "segmentation" environment. You can install the package following the steps below.


## Step 3: Clone the github repository 


#### 1. Check if you have git installed.

```bash 
git --version
```

If you don't have git, follow [Git for Windows](https://www.atlassian.com/git/tutorials/install-git#windows) to install. It is okay to just use default installation settings. Also, you need to restart Anaconda after installing Git.

#### 2. Clone aics-segmentation repository from Github (suppose you want to save the folder under 'C:\Projects')

```bash
cd C:\Projects
git clone https://github.com/AllenInstitute/aics-segmentation.git
```

## Step 4: Install the package


### Option 1: Install from PyPi (simple and recommend for most users)

```bash
pip install numpy
pip install aicssegmentation
```
### Option 2: Build from source (only if you want to make changes on the source code)

```bash
cd C:\Projects\aics-segmentation\
pip install -e .
```

## Step 5: Test jupyter notebook demo


``` bash 
cd C:\Projects\aics-segmentation\lookup_table_demo
jupyter notebook, choose anaconda installer.
```

This will take you to your default browser (e.g., Chrome) and launch Jupyter Notebook App within your browser. Then, you can test if you can run the demo or not. See more details on [How to use Jupyter Notebook to running the workflow in the Look-up Table](../docs/jupyter_notebook_table.md)


