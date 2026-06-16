# 01. SIESTA Ab initio molecular dynamics simulation

The first procedure is to obtain accurate quantum data to train machine learning interatomic potentials. One method of doing so is by gathering trajectories from ab initio molecular dynamics (AIMD), where energies and forces of the system are calculated with their electronic structure. AIMD is carried out here by the SIESTA software program.

## Initial coordinates

For initial atomic coordinates, the XYZ file of the example gold-decanedithiol-gold junction (AuSC10HS.xyz) is included. These specific coordinates were created and edited, as well as having the geometry optimized with the Universal Force Field (UFF) in Avogadro. More accurate geometry optimization may also be done with SIESTA prior to AIMD simulation.

Coordinates in the XYZ format must be converted if placed into SIESTA input script. Conversion script (xyz2fdf.py) is included here.

## SIESTA

The SIESTA input script (ausc10hs.fdf) contains all information to control AIMD simulation. Information includes atomic species and coordinates, geometry constraints, simulation cell size, basis set, SCF convergence parameters, MD controls, and more.

[Pseudopotentials](https://siesta-project.org/siesta/Documentation/Pseudopotentials/) are required for each element present in the simulated system. Included here are pseudopotentials designed for the PBE functional method.

To begin the AIMD simulation, place the SIESTA input script (.fdf) together with all pseudopotentials for each element in the system. An example SLURM job script (siesta_job.sh) is included, which starts the simulation once submitted.