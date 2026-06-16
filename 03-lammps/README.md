# 03. LAMMPS classical MD simulation

LAMMPS must be integrated with the use of MLPs trained using DeePMD-kit (pair_style dp). In this repository, the objective of the LAMMPS production MD is simulating heat transport in this gold-alkanedithiol-gold junction.

In this LAMMPS workflow, the coordinate file is separate from the input, which reads the coordinates in. The .xyz file is converted into the LAMMPS coordinate file format using xyz2lmp.py.

The input file (langevin_th.lammps) establishes a three step process starting from the frozen initial structure:

    Energy minimization --> NVT equilibration --> NVE + Langevin thermostats NEMD production run