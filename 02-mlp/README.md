# 02. DeePMD-kit training of machine learning interatomic potentials

The main output file from SIESTA AIMD simulations is the .out file, which contains frame-by-frame information on coordinates, energies, and forces. This file contains all information required for the MLP training using DeePMD-kit.

## Data preparation

Firstly, if there are multiple .out files from AIMD simulations, they are processed by a script (aimd_process.py) that prepares the ML dataset. The dpdata package is required, which prepares data from various electronic structure calculation programs for use in DeePMD-kit. See documentation for all supported programs and formats. Three tasks beyond direct reading of training data are configured for dpdata to perform:

1. Crop first frame of trajectories when multiple .out files from AIMD are read in. The main purpose of this task is to remove the repeated initial configuration.

2. Downsample the MD frames with an adjustable stride. Because information for every single timestep is written in the AIMD output, subsequent frames may be highly correlated in terms of their structures and properties. This task reduces the correlation i.e., the amount of data, and the extent of reduction can be controlled.

3. Split data into training set and validation set. The splitting occurs in every individual trajectory so validation set should contain information from all trajectories. The default is a 90/10 split.

## Machine learning training

The input.json script contains all information to begin the ML training. Example SLURM job script is included.

Default command in terminal: dp train input.json

Further training details and procedure can be found in the documentation and the tutorials. After training, the model is frozen and compressed to a .pb format for use in production MD simulations.