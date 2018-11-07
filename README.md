# Overview of AICS Segmentation Library

Obtaining accurate segmentation of 3D intracellular structures in an
automated, reproducible and consistent manner is a key step for quantitative
analysis of image data, especially for analysis at scale. With the fast
development of computer vision researches in recent years, the capability
of computers in interpreting images is being significantly improved. But,
there is still a noteworthy gap between the state-of-the-art computer
vision algorithms and the actual tools
that cell biologists can easily access for segmenting their own images. 
In this work, we introduce a new python-based open source toolkit, 
developed at the Allen Institute for Cell Science, for intracellular structure 
segmentation in 3D microscopy images. The toolkit has been applied on over 30 
different cell Lines, from human induced pluripotent stem cell and stem cell 
differentiated cardiomyocyte,and enables further quantitative cell biology analysis. 
The toolkit consists of two complementary parts: a classic image segmentation workflow 
and an iterative deep learning workflow. (1) The classic image segmentation workfow is 
formulated as a simple 3-step workflow with restricted numbers of selectable algorithms 
and tunable parameters to effective segment a wide range of different structures. To 
further make the application on new data as straightforward as possible, we select 21 
representative structures and their results to create a “look-up table” as a reference 
and a starting point. (2) The iterative deep learning workflow can be used the classic 
segmentation workflow cannot achieve satisfactory accuracy or robustness. We design the 
iterative deep learning workflow to be easily accessible to cell biologists from two aspects. 
Combining our classic segmentation workflow and two conceptually simple human intervention 
strategies, one can easily build ground truth image sets as training data without painstaking 
manual painting in 3D. On the other hand, the model constructing and training are specially 
designed and tested for 3Dmicroscopy images and implemented in a human readable wrapper. All 
in all, we developed a new open-source toolkit for 3D microscopy image segmentation 
leveraging state-of-the-art computer vision algorithms in an accessible way and hope 
to facilitate cell biologists to gain more insight into fundamental biological questions.

## Level of Support
We are not currently supporting this code for external use, but simply releasing it 
to the community AS IS. It is used for within our organization. We are not able to 
provide any guarantees of support. The community is welcome to submit issues, but 
you should not expect an active response.

## Development
See [BUILD.md](BUILD.md) for information operations related to developing the code.
