# Overview of AICS Segmentation Library

Obtaining accurate segmentation of 3D intracellular structures in an
automated, reproducible and consistent manner is a key step for quantitative analysis of image data, especially for analysis at scale. With the fast development of computer vision researches in recent years, the capability of computers in interpreting images is being significantly improved. But, there is still a noteworthy gap between the state-of-the-art computer vision algorithms and the actual tools that cell biologists can easily access for segmenting their own images. In this work, we introduce a new python-based open source toolkit, developed at the Allen Institute for Cell Science, for intracellular structure segmentation in 3D microscopy images. The toolkit has been applied on over 30 different cell Lines, from human induced pluripotent stem cell and stem cell differentiated cardiomyocyte,and enables further quantitative cell biology analysis. The toolkit consists of two complementary parts: a classic image segmentation workflow
and an iterative deep learning workflow. (1) The classic image segmentation workfow is formulated as a simple 3-step workflow with restricted numbers of selectable algorithms and tunable parameters to effective segment a wide range of different structures. To further make the application on new data as straightforward as possible, we select 21 representative structures and their results to create a “look-up table” as a reference and a starting point. (2) The iterative deep learning workflow can be used the classic segmentation workflow cannot achieve satisfactory accuracy or robustness. We design the
iterative deep learning workflow to be easily accessible to cell biologists from two aspects. Combining our classic segmentation workflow and two conceptually simple human intervention strategies, one can easily build ground truth image sets as training data without painstaking manual painting in 3D. On the other hand, the model constructing and training are specially designed and tested for 3Dmicroscopy images and implemented in a human readable wrapper. All
in all, we developed a new open-source toolkit for 3D microscopy image segmentation leveraging state-of-the-art computer vision algorithms in an accessible way and hope to facilitate cell biologists to gain more insight into fundamental biological questions.

**Note: This repository is only for the "Classic Image Segmentation Workflow". We are working on the release of the "Iteration Deep Learning Workflow", which requires more effort to simplify the complicated environment setup. Stay tuned :smiley:**


## Installation

Our package is implemented in python 3.6. We suggest to manage python packages using conda. For detailed instruction on different operating systems, check the pages below.

[Installation on Linux](./docs/installation_linux.md) (The OS we used for development is Ubuntu 16.04.5 LTS)

[Installation on MacOS](./docs/installation_mac.md)

[Installation on Windows](./docs/installation_windows.md)


## Use the package

What you have installed is actually a collection of many many image analysis and visualization algorithms implemented in Python 3, including [ITK](https://itkpythonpackage.readthedocs.io/en/latest/), [scikit-image](http://scikit-image.org/docs/stable/), and also some our own implementations. In other words, you already have a huge box of Python "weapons" for image analysis and visualization on your machine. :hammer: :wrench:

The "design philosophy" of our package is (1) to provide a simple tool for cell biologists to quickly obtain intracelluar structure segmentation with reasonable accuracy and robustness over a large set of images, (2) if by chance, experienced developers need to design a more sophisticated algorithm, we hope our package could facilitate such advanced development and implementation, as a unified development environment.

### Part 1: Quick segmentation for **Users**

This toolkit is
1. formulated as a simple 3-step workflow for solving 3D intracelluar structure segmentation problem using restricted number of selectable algorithms and tunable parameters
2. accompanied by a ["lookup table"](./docs/figure_3_lookup_table_20181029.pdf) with 20 representative structure segmentation tasks and their results for you as a reference and the correspoinding Jupyter notebook as a starting point.

[Link to documentation for users](./docs/jupyter_lookup_table.md)

### Part 2: Advanced development for experienced **Developers**  

[Link to documentation for developers](./docs/full_doc.md)

## Level of Support
Currently, we are at soft-release stage. We are simply releasing it to the community AS IS. It has been used within our organization. We are not able to provide any guarantees of support. The community is welcome to submit issues. Contact: Jianxu Chen (jianxuc@alleninstitute.org)

