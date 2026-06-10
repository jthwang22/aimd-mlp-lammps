"""
Process multiple SIESTA AIMD trajectories into a single output to be read by dpdata for DeePMD-kit training data.

Procedure:
1. Crop the final MD frame from the first trajectory, then crop the first MD frame from the subsequent trajectories.
    For restarted trajectories:
        - The first restart chunk has its first MD frame removed
        - All non-final restart chunks have their final MD frame removed
        - Restart chunks are concatenated before downsampling
2. Downsample MD trajectories with given stride.
3. Concatenate all trajectories into single output file.

Usage example:

python aimd_process.py ./Raw_Folder/ ./processed_system.out --stride 10

"""


from pathlib import Path
from typing import List
from collections import defaultdict
import argparse
import logging
import re


def is_restart_file(path: Path) -> bool:
    """
    Match files such as:

    300K_1.out
    300K_2.out
    """

    return re.search(r"_\d+\.out$", path.name) is not None


def get_restart_info(path: Path) -> tuple[str, int] | None:

    match = re.match(r"(.+?)_(\d+)\.out$", path.name)

    if match is None:
        return None

    return (match.group(1), int(match.group(2)))


def has_later_restart(file_path: Path, all_files) -> bool:

    info = get_restart_info(file_path)

    if info is None:
        return False

    prefix, chunk = info

    for other in all_files:

        other_info = get_restart_info(other)

        if other_info is None:
            continue

        other_prefix, other_chunk = (other_info)

        if (other_prefix == prefix and other_chunk > chunk):
            return True

    return False


def remove_first_md_frame(lines: List[str]) -> List[str]:
    """
    Remove the first MD frame and
    start at the second MD frame.
    """

    md_count = 0

    for idx, line in enumerate(lines):

        if line.strip().startswith("Begin MD step"):

            md_count += 1

            if md_count == 2:
                return lines[idx:]

    raise ValueError(
        "File contains fewer than two MD steps."
    )


def remove_last_md_frame(lines: List[str]) -> List[str]:
    """
    Remove the final MD frame.
    """

    md_indices = []

    for idx, line in enumerate(lines):
        if line.strip().startswith("Begin MD step"):
            md_indices.append(idx)

    if len(md_indices) < 2:
        raise ValueError(
            "Need at least two MD steps to remove the last frame."
        )

    # Start of final frame
    last_frame_start = md_indices[-1]

    return lines[:last_frame_start]


def downsample_lines(lines: List[str], stride: int) -> List[str]:
    """
    Keep every nth MD frame.
    """

    output_lines = []

    current_frame = []
    frame_index = -1

    inside_frame = False
    found_first_frame = False

    for line in lines:

        if line.strip().startswith("Begin MD step"):

            if not found_first_frame:
                found_first_frame = True

                # Preserve header before first MD step
                output_lines.extend(current_frame)
                current_frame = []

            if inside_frame:

                if frame_index % stride == 0:
                    output_lines.extend(current_frame)

                current_frame = []

            frame_index += 1
            inside_frame = True

        if not found_first_frame:
            current_frame.append(line)

        elif inside_frame:
            current_frame.append(line)

    # Handle final frame

    if (
        current_frame
        and found_first_frame
        and frame_index % stride == 0
    ):
        output_lines.extend(current_frame)

    return output_lines


def process_folder(
    input_dir: Path,
    output_file: Path,
    stride: int
) -> None:
    """
    Process all .out files and write a single
    concatenated trajectory.
    """

    out_files = sorted(input_dir.glob("*.out"))

    if not out_files:
        raise FileNotFoundError(
            f"No .out files found in {input_dir}"
        )

    logging.info(
        "Found %d files.",
        len(out_files)
    )
    
    total_frames = 0

    trajectory_groups = defaultdict(list)

    with output_file.open("w", encoding="utf-8") as outfile:

        for file_path in out_files:

            info = get_restart_info(file_path)

            if info is None:

                trajectory_groups[file_path.stem].append(file_path)

            else:

                prefix, chunk = info

                trajectory_groups[prefix].append(file_path)

        for files in trajectory_groups.values():

            files.sort(
                key=lambda p:
                get_restart_info(p)[1]
                if get_restart_info(p)
                else 0
            )

        regular_file_count = 0

        for trajectory_name in sorted(trajectory_groups):

            group_files = trajectory_groups[trajectory_name]

            combined_lines = []

            for file_path in group_files:

                with file_path.open("r", encoding="utf-8") as f:

                    lines = f.readlines()

                if is_restart_file(file_path):

                    _, chunk = (get_restart_info(file_path))

                    if chunk == 1:

                        lines = (remove_first_md_frame(lines))

                    if has_later_restart(file_path,group_files):

                        lines = (remove_last_md_frame(lines))

                else:

                    if regular_file_count == 0:

                        lines = (remove_last_md_frame(lines))

                    else:

                        lines = (remove_first_md_frame(lines))

                    regular_file_count += 1

                combined_lines.extend(lines)

                logging.info(
                    "Added %s to %s",
                    file_path.name,
                    trajectory_name
                )

            processed_lines = (downsample_lines(combined_lines, stride))

            frame_count = sum(
                1
                for line in processed_lines
                if line.strip().startswith(
                    "Begin MD step"
                )
            )

            total_frames += frame_count

            outfile.writelines(processed_lines)

    logging.info(
        "Created combined trajectory: %s",
        output_file
    )

    logging.info(
        "Total MD frames in combined trajectory: %d",
        total_frames
    )


def main():

    parser = argparse.ArgumentParser(
        description=(
            "Crop, downsample, and concatenate "
            "SIESTA AIMD output files."
        )
    )

    parser.add_argument(
        "input_dir",
        type=Path,
        help="Directory containing raw .out files"
    )

    parser.add_argument(
        "output_file",
        type=Path,
        help="Combined output filename"
    )

    parser.add_argument(
        "--stride",
        type=int,
        default=10,
        help="Keep every nth MD frame (default: 10)"
    )

    args = parser.parse_args()

    logging.basicConfig(
        level=logging.INFO,
        format="%(levelname)s: %(message)s"
    )

    process_folder(
        args.input_dir,
        args.output_file,
        args.stride
    )


if __name__ == "__main__":
    main()