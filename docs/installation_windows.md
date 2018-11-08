## Step 0: Setup conda environment (Optional, but strongly recommended)

Out package is implemented in python 3.6. We suggest to manage your python packages using conda. 

### Windows

1. [Install conda on Windows](https://conda.io/docs/user-guide/install/windows.html?highlight=conda)


2. [Start conda on Windows](https://conda.io/docs/user-guide/getting-started.html#starting-conda)

All commands below are typed into Anaconda Prompt sindow

3. Create a new empty conda environment (suppose we use name "segmentation")

``` bash 
conda create -n segmentation python=3.6
```

4. Activate your new conda environment "segmentation"

``` bash
activate segmentation
```

5. Now, you are in "segmentatin" environment. You can install the package following the steps below.


## Step 1: Install the core package

### Windows

1. Install MS Visual Studio 

2. Install our package

``` bash
pip install aicssegmentation
```