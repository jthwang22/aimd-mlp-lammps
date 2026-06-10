#!/bin/bash
#SBATCH --job-name=lammps_th
#SBATCH --output=lammps.out
#SBATCH --time=8765:43:21
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=4

module purge
module load deepmd-kit/3.1.2

## Change to current working directory
cd $SLURM_SUBMIT_DIR

export OMP_NUM_THREADS=4

mpirun -np 4 lmp -in input_nve.dat

exit
