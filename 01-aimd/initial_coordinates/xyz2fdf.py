"""
Read an XYZ file, reorder atoms according to atom type and z-coordinate,
and print the resulting coordinates.

This script assumes a molecular junction structure with geometrically constrained electrode atoms.

Usage:
    python xyz2fdf.py AuSC10HS.xyz
"""

from pathlib import Path
import argparse
import pandas as pd


ELEMENT_MAP = {
    "Au": 1,
    "S": 2,
    "C": 3,
    "H": 4,
}


def read_xyz(filepath: Path) -> pd.DataFrame:
    """
    Read an XYZ file and return a DataFrame containing coordinates and atom types.
    """
    molecule = pd.read_table(
        filepath,
        skiprows=2,
        sep=r"\s+",
        names=["Element", "x", "y", "z"],
    )

    molecule["Element"] = molecule["Element"].replace(ELEMENT_MAP)

    molecule = molecule[["x", "y", "z", "Element"]]
    molecule = molecule.sort_values(by=["Element", "z"])

    return molecule


def reorder_atoms(molecule: pd.DataFrame) -> pd.DataFrame:
    """
    Reorder atoms:
      1. Bottom Au layer
      2. Top Au layer
      3. Remaining Au atoms
      4. Non-Au atoms
    """
    autype = molecule[molecule["Element"] == 1].copy()
    moltype = molecule[molecule["Element"] != 1].copy()

    z_min = autype["z"].min()
    z_max = autype["z"].max()

    fix_layer_1 = autype[autype["z"] < z_min + 0.5]
    fix_layer_2 = autype[autype["z"] > z_max - 0.5]

    move_au = autype[
        (autype["z"] > z_min + 0.5)
        & (autype["z"] < z_max - 0.5)
    ]

    au_ordered = pd.concat(
        [fix_layer_1, fix_layer_2, move_au],
        ignore_index=True,
    )

    return pd.concat(
        [au_ordered, moltype],
        ignore_index=True,
    )


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Reorder atoms in an XYZ file."
    )

    parser.add_argument(
        "xyz_file",
        type=Path,
        help="Path to XYZ file",
    )

    return parser.parse_args()


def main() -> None:
    """Main program."""
    args = parse_args()

    if not args.xyz_file.exists():
        raise FileNotFoundError(
            f"File not found: {args.xyz_file}"
        )

    molecule = read_xyz(args.xyz_file)
    junction = reorder_atoms(molecule)

    print(junction.to_string(index=False))
    print(f"\nNumber of atoms = {len(junction)}")


if __name__ == "__main__":
    main()