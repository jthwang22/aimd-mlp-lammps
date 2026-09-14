#!/usr/bin/env python3
"""
Process SIESTA AIMD trajectories into DeePMD training and validation datasets.

This script discovers trajectory output files via glob, drops the initial 
shared configuration frame, applies downsampling via a stride, splits the 
data into a 90/10 train/validation ratio per trajectory, and exports them 
into DeepMD-kit compatible formats using a unified global type map.
"""

import argparse
import logging
from glob import glob
import os
import numpy as np
import dpdata

# Configure logging format
logging.basicConfig(
    level=logging.INFO,
    format="[%(levelname)s] %(asctime)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger(__name__)

# Define a single, unified type map across all systems
GLOBAL_TYPE_MAP = ["C", "H", "F", "Cl", "Br", "I"]


def parse_arguments() -> argparse.Namespace:
    """Parse command-line arguments for flexibility."""
    parser = argparse.ArgumentParser(
        description="Process SIESTA AIMD outputs for DeePMD training."
    )
    parser.add_argument(
        "--pattern",
        type=str,
        default="./output/*.out",
        help="Glob pattern to find trajectory output files (default: './output/*.out')."
    )
    parser.add_argument(
        "--stride",
        type=int,
        default=5,
        help="Stride for frame-level downsampling (default: 5)."
    )
    parser.add_argument(
        "--val-split",
        type=float,
        default=0.1,
        help="Fraction of frames to allocate for validation (default: 0.1)."
    )
    parser.add_argument(
        "--train-dir",
        type=str,
        default="training_data",
        help="Output directory for training data."
    )
    parser.add_argument(
        "--val-dir",
        type=str,
        default="validation_data",
        help="Output directory for validation data."
    )
    return parser.parse_args()


def process_trajectories(
    file_pattern: str, 
    stride: int, 
    val_split: float
) -> tuple[dpdata.MultiSystems, dpdata.MultiSystems]:
    """
    Load trajectories, drop first frame, downsample, and split into train/val.
    """
    train_ms = dpdata.MultiSystems()
    val_ms = dpdata.MultiSystems()

    files = glob(file_pattern)
    logger.info(f"Found {len(files)} matching trajectory files using pattern: {file_pattern}")

    if not files:
        logger.warning("No files found. Please check your path or glob pattern.")
        return train_ms, val_ms

    for fpath in files:
        try:
            # Load trajectory with the global type map
            ls = dpdata.LabeledSystem(fpath, fmt="siesta/aimd_output", type_map=GLOBAL_TYPE_MAP)
            n_frames_orig = len(ls)
            
            if n_frames_orig <= 1:
                logger.warning(f"Skipping {fpath}: Insufficient frames ({n_frames_orig}).")
                continue
                
            # 1. Drop the first frame (index 0) to remove shared starting geometry
            ls = ls.sub_system(np.arange(1, n_frames_orig))
            n_frames_sliced = len(ls)
            
            # 2. Downsample using stride
            ds_indices = np.arange(0, n_frames_sliced, stride)
            ls_ds = ls.sub_system(ds_indices)
            n_frames_ds = len(ls_ds)
            
            # 3. Random split based on validation fraction
            n_val = max(1, int(val_split * n_frames_ds))
            val_indices = np.random.choice(n_frames_ds, size=n_val, replace=False)
            train_indices = np.setdiff1d(np.arange(n_frames_ds), val_indices)
            
            ls_train = ls_ds.sub_system(train_indices)
            ls_val = ls_ds.sub_system(val_indices)
            
            # Append to MultiSystems containers
            train_ms.append(ls_train)
            val_ms.append(ls_val)
            
            logger.info(
                f"Successfully processed {fpath} | "
                f"Orig: {n_frames_orig} -> Sliced -> Downsampled: {n_frames_ds} "
                f"(Train: {len(train_indices)}, Val: {len(val_indices)})"
            )
            
        except Exception as e:
            logger.error(f"Failed to process {fpath}: {e}")

    return train_ms, val_ms


def main() -> None:
    args = parse_arguments()
    
    logger.info("Starting DeePMD dataset preparation pipeline...")
    logger.info(f"Using Global Type Map: {GLOBAL_TYPE_MAP}")
    
    # Process the data
    train_ms, val_ms = process_trajectories(
        file_pattern=args.pattern,
        stride=args.stride,
        val_split=args.val_split
    )
    
    # Export datasets if populated
    if len(train_ms.systems) > 0:
        logger.info(f"Exporting training data to '{args.train_dir}'...")
        train_ms.to("deepmd/npy", args.train_dir)
        
        logger.info(f"Exporting validation data to '{args.val_dir}'...")
        val_ms.to("deepmd/npy", args.val_dir)
        
        logger.info("Pipeline completed successfully!")
    else:
        logger.error("No valid systems found. Skipping export.")


if __name__ == "__main__":
    main()