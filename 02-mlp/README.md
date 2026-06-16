# 02. DeePMD-kit training of machine learning interatomic potentials

The main output file from SIESTA AIMD simulations is the .out file, which contains frame-by-frame information on coordinates, energies, and forces. This file contains all information required for the MLP training using DeePMD-kit.

## Data preparation

Firstly, if there are multiple .out files from AIMD simulations, they are processed by a script (aimd_process.py) that prepares the ML dataset. Three main tasks are performed:

1. Crop certain parts of the output file when multiple .out files from AIMD are read in. The main purpose of this task is to remove repeated information. For example, the initialization information in each individual run, and all information about the first MD step if the same initial coordinates were used for many runs.

2. Downsample the MD frames with an adjustable stride. Because information for every single timestep is written in the AIMD output, subsequent frames may be highly correlated in terms of their structures and properties. This task reduces the correlation i.e., the amount of data, and the extent of reduction can be controlled.

3. Concatenate all trajectories into one dataset file. This task combines data from multiple AIMD simulations into one for ease of splitting of data in the next step.

The next step is to split the dataset into training data and validation data. The splitting is done using split_data.py which requires the dpdata Python package. dpdata manipulates data from various electronic structure calculation programs for use in DeePMD-kit. See documentation for all supported programs and formats.

## Machine learning training

The input.json script contains all information to begin the ML training. Example SLURM job script is included.

Default command in terminal: dp train input.json

Further training details and procedure can be found in the documentation and the tutorials. After training, the model is frozen and compressed to a .pb format for use in production MD simulations.