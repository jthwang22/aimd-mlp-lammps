#!/usr/bin/env python3
"""
Split a SIESTA AIMD trajectory into training and validation datasets
for DeepMD.

Requires dpdata package.

Usage
-----
python split_data.py data.out

python split_data.py data.out --val-frac 0.1

python split_data.py data.out \
    --train-dir training_data \
    --val-dir validation_data \
    --seed 123
"""

from pathlib import Path
import argparse
import numpy as np
import dpdata


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Split SIESTA AIMD output into DeepMD training and validation datasets."
    )

    parser.add_argument(
        "input_file",
        type=Path,
        help="SIESTA AIMD output file (.out)",
    )

    parser.add_argument(
        "--val-frac",
        type=float,
        default=0.10,
        help="Fraction of frames used for validation (default: 0.10)",
    )

    parser.add_argument(
        "--train-dir",
        default="training_data",
        help="Output directory for training data",
    )

    parser.add_argument(
        "--val-dir",
        default="validation_data",
        help="Output directory for validation data",
    )

    parser.add_argument(
        "--seed",
        type=int,
        default=None,
        help="Random seed for reproducible splitting",
    )

    return parser.parse_args()


def main() -> None:
    args = parse_args()

    if not args.input_file.exists():
        raise FileNotFoundError(f"Input file not found: {args.input_file}")

    if args.seed is not None:
        np.random.seed(args.seed)

    data = dpdata.LabeledSystem(
        str(args.input_file),
        fmt="siesta/aimd_output",
    )

    n_frames = len(data)
    print(f"# the data contains {n_frames} frames")

    n_val = int(n_frames * args.val_frac)

    val_indices = np.random.choice(
        n_frames,
        size=n_val,
        replace=False,
    )

    train_indices = list(
        set(range(n_frames)) - set(val_indices)
    )

    data_training = data.sub_system(train_indices)
    data_validation = data.sub_system(val_indices)

    data_training.to_deepmd_npy(args.train_dir)
    data_validation.to_deepmd_npy(args.val_dir)

    print(f"# the training data contains {len(data_training)} frames")
    print(f"# the validation data contains {len(data_validation)} frames")


if __name__ == "__main__":
    main()