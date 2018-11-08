# Installation Instruction for MacOS

(tested on XXXXX)


## Step 1: Install XCode

[Download and install XCode from Apple Developer](https://developer.apple.com/xcode/)


## Step 2: Setup conda environment 

[What is conda and anaconda, and why we need this?](conda_why.md) In short, setting up conda will make all the following setups straightforward and greatly avoid future problems (conda itself is also very easy to set up).

#### 1. [Install conda on macOS](https://conda.io/docs/user-guide/install/macos.html), choose anaconda installer.


#### 2. [Start conda on macOS](https://conda.io/docs/user-guide/getting-started.html#starting-conda)

All commands below are typed into the Terminal Window

#### 3. Create a new empty conda environment (suppose we use name "segmentation" for this environment)

``` bash 
conda create -n segmentation python=3.6
```

#### 4. Activate your new conda environment "segmentation"

``` bash
source activate segmentation
```

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


### Option 1: Install from PyPi (simple and recommend for most users)

```bash
pip install aicssegmentation
```
### Option 2: Build from source (only if you want to make changes on the source code)

```bash
cd ~/Projects/aics-segmentation
pip install -e .
```

## Step 5: Test jupyter notebook demo


``` bash 
cd ~/Projects/aics-segmentation/lookup_table_demo
jupyter notebook
```

This will take you to your default browser (e.g., Safari) and launch Jupyter Notebook App within your browser. Then, you can test if you can run the demo or not. See more details on [How to use Jupyter Notebook to running the workflow in the Look-up Table](../docs/jupyter_notebook_table.md)


