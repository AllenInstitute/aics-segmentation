# Overview

The Allen Cell Structure Segmenter is a Python-based open source toolkit developed for 3D segmentation of intracellular structures in fluorescence microscope images, developed at the Allen Institute for Cell Science. This toolkit brings together classic image segmentation and iterative deep learning workflows first to generate initial high quality 3D intracellular structure segmentations and then to easily curate these results to generate the ground truths for building robust and accurate deep learning models. The toolkit takes advantage of the high replicate 3D live cell image data collected at the Allen Institute for Cell Science of over 30 endogenous fluorescently tagged human induced pluripotent stem cell (hiPSC) lines. Each cell line represents a different intracellular structure with one or more distinct localization patterns within undifferentiated hiPS cells and hiPSC-derived cardiomyocytes.

The Allen Cell Structure Segmenter consists of two complementary elements, a classic image segmentation workflow with a restricted set of algorithms and parameters and an iterative deep learning segmentation workflow. We created a collection of 20 classic image segmentation workflows based on 20 distinct and representative intracellular structure localization patterns as a “lookup table” [Add in-page Hyperlink] reference and starting point for users. The iterative deep learning workflow can take over when the classic segmentation workflow is insufficient. Two straightforward “human-in-the-loop” curation strategies convert a set of classic image segmentation workflow results into a set of 3D ground truth images for iterative model training without the need for manual painting in 3D. The Allen Cell Structure Segmenter thus leverages state of the art computer vision algorithms in an accessible way to facilitate their application by the experimental biology researcher.

**Note: This repository is only for the "Classic Image Segmentation Workflow". We are working on the release of the "Iteration Deep Learning Workflow", which requires more effort to simplify the complicated environment setup. Stay tuned :smiley:**


## Installation

Our package is implemented in python 3.6. We suggest to manage python packages using conda. For detailed instruction on different operating systems, check the pages below.

[Installation on Linux](./docs/installation_linux.md) (The OS we used for development is Ubuntu 16.04.5 LTS)

[Installation on MacOS](./docs/installation_mac.md)

[Installation on Windows](./docs/installation_windows.md)


## Use the package

What you have installed is actually a collection of many many image analysis and visualization algorithms implemented in Python 3, including [ITK](https://itkpythonpackage.readthedocs.io/en/latest/), [scikit-image](http://scikit-image.org/docs/stable/), and also some our own implementations. In other words, you already have a huge box of Python "weapons" for image analysis and visualization on your machine. :hammer: :wrench:

The "design philosophy" of our package is (1) to provide a simple tool for cell biologists to quickly obtain intracelluar structure segmentation with reasonable accuracy and robustness over a large set of images, (2) if by chance, experienced developers need to design a more sophisticated algorithm, we hope our package could facilitate such advanced development and implementation, as a unified development environment.

Visualization is a key component in algorithm development and results validation (qualitatively). Right now, our toolkit is utilizing [itk-jupyter-widgets](https://github.com/InsightSoftwareConsortium/itk-jupyter-widgets), which is a very powerful in-jupyter visualization tool primarily designed for medical data. Some cool demo videos can be found [here](https://www.youtube.com/playlist?list=PL2lHcsoU0YJsh6f8j2vbhg2eEpUnKEWcl).

### Part 1: Quick segmentation for **Users**

This toolkit is
1. formulated as a simple 3-step workflow for solving 3D intracelluar structure segmentation problem using restricted number of selectable algorithms and tunable parameters
2. accompanied by a ["lookup table"](./docs/figure_3_lookup_table_20181029.pdf) with 20 representative structure segmentation tasks and their results for you as a reference and the correspoinding Jupyter notebook as a starting point.

[Link to documentation for users](./docs/jupyter_lookup_table.md)

### Part 2: Advanced development for experienced **Developers**  

[Link to documentation for developers](./docs/full_doc.md)

## Level of Support
Currently, we are at soft-release stage. We are simply releasing it to the community AS IS. It has been used within our organization. We are not able to provide any guarantees of support. The community is welcome to submit issues. Contact: Jianxu Chen (jianxuc@alleninstitute.org)
