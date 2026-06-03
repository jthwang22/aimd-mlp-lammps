#!/bin/bash
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=96
#SBATCH --time=12:00:00
#SBATCH --job-name=siesta_ausc10hs
#SBATCH --output=siesta_sh.out

## Change to current working directory
cd $SLURM_SUBMIT_DIR

## Load modules
module load StdEnv/2023 intel/2023.2.1 openmpi/4.1.5
module load siesta/5.4.0

## Run
mpirun siesta < ausc10hs.fdf > ausc10hs.out
