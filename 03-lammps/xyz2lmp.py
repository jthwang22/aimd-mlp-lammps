#!/usr/bin/env python3
"""
Read an XYZ file, reorder atoms according to atom type and z-coordinate,
and writes the separated coordinate file to be read by LAMMPS input script.

This script assumes a molecular junction structure with geometrically constrained electrode atoms.
In the LAMMPS input script, multiple atom types for the electrode atoms are used to differentiate regions for thermostatting.

Usage:
    python xyz2lmp.py AuSC10HS.xyz --box 50 50 50 -o junction.dat

"""


from pathlib import Path
import argparse
import pandas as pd


MASSES = {
    1: ("196.97", "Au"),
    2: ("196.97", "Au"),
    3: ("196.97", "Au"),
    4: ("32.07", "S"),
    5: ("12.01", "C"),
    6: ("1.01", "H"),
}


def parse_args():
    parser = argparse.ArgumentParser(
        description="Convert XYZ file to LAMMPS coordinate file."
    )

    parser.add_argument(
        "xyz_file",
        type=Path,
        help="Input XYZ file",
    )

    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        default=None,
        help="Output coordinate file",
    )

    parser.add_argument(
        "--box",
        nargs=3,
        type=float,
        metavar=("LX", "LY", "LZ"),
        default=[50.0, 50.0, 50.0],
        help="Box dimensions (default: 50 50 50)",
    )

    return parser.parse_args()


def read_xyz(xyz_file: Path) -> pd.DataFrame:
    molecule = pd.read_table(
        xyz_file,
        skiprows=2,
        sep=r"\s+",
        names=["Type", "x", "y", "z"],
    )

    molecule["Type"] = molecule["Type"].replace(
        {
            "Au": 2,
            "S": 4,
            "C": 5,
            "H": 6,
        }
    )

    z_min = molecule["z"].min()
    z_max = molecule["z"].max()

    molecule.loc[molecule["z"] < z_min + 0.5, "Type"] = 1
    molecule.loc[molecule["z"] > z_max - 0.5, "Type"] = 1

    s_zmax = molecule.loc[molecule["Type"] == 4, "z"].max()

    molecule.loc[
        (molecule["z"] < z_max - 1.0)
        & (molecule["z"] > s_zmax),
        "Type",
    ] = 3

    molecule = molecule[["Type", "x", "y", "z"]]

    molecule.index = range(1, len(molecule) + 1)

    return molecule


def write_lammps(
    molecule: pd.DataFrame,
    outfile: Path,
    lx: float,
    ly: float,
    lz: float,
):
    with open(outfile, "w") as f:

        f.write("# coordinate file\n\n")

        f.write(f"{len(molecule)} atoms\n")
        f.write("6 atom types\n\n")

        f.write(f"0.000000 {lx:.6f} xlo xhi\n")
        f.write(f"0.000000 {ly:.6f} ylo yhi\n")
        f.write(f"0.000000 {lz:.6f} zlo zhi\n\n")

        f.write("Masses\n\n")

        for atom_type, (mass, label) in MASSES.items():
            f.write(f"{atom_type} {mass:<12} # {label}\n")

        f.write("\nAtoms\n\n")

        for idx, row in molecule.iterrows():
            f.write(
                f"{idx:4d} "
                f"{int(row['Type'])} "
                f"{row['x']:12.6f} "
                f"{row['y']:12.6f} "
                f"{row['z']:12.6f}\n"
            )


def main():
    args = parse_args()

    outfile = (
        args.output
        if args.output is not None
        else args.xyz_file.with_name(
            args.xyz_file.stem + "_coord.dat"
        )
    )

    molecule = read_xyz(args.xyz_file)

    lx, ly, lz = args.box

    write_lammps(
        molecule,
        outfile,
        lx,
        ly,
        lz,
    )

    print(f"Wrote {outfile}")
    print(f"Number of atoms: {len(molecule)}")


if __name__ == "__main__":
    main()