# -*- coding: utf-8 -*-
"""
This script processes music directories by traversing an input folder,
detecting music files and cue sheets, and processing them using ffmpeg.
Depending on the file type, the script either splits a multi-track file
based on a cue sheet or processes individual music files. Output directories
are created as needed, and commands can be executed in parallel.
"""

import sys
import os
import os.path
import pathlib
import argparse
import logging
from multiprocessing import cpu_count
from concurrent.futures import ProcessPoolExecutor
from cue import parse_cue
from src.cmd import make_split_cmd, process_onefile
from utils import ensure_directory_exists, write_text_to_file

# Configure logging with UTF-8 encoding for both console and file handlers.
formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")

stream_handler = logging.StreamHandler(sys.stdout)
stream_handler.setLevel(logging.INFO)
stream_handler.setFormatter(formatter)
if hasattr(stream_handler.stream, "reconfigure"):
    stream_handler.stream.reconfigure(encoding="utf-8")

file_handler = logging.FileHandler("../music_processing.log", mode="a", encoding="utf-8")
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(formatter)

logger = logging.getLogger()
logger.setLevel(logging.INFO)
logger.handlers.clear()  # Remove any existing handlers.
logger.addHandler(stream_handler)
logger.addHandler(file_handler)


# Get default values from environment variables; if not provided, use fallback defaults.
ffmpeg_path_default = os.environ.get("FFMPEG_PATH", "ffmpeg")
dir_in_default = os.environ.get("DIR_IN", "/music/in")
dir_out_default = os.environ.get("DIR_OUT", "/music/out")
dry_run_default = os.environ.get("DRY_RUN", "false").lower() in ("true", "1", "yes")
hide_ffmpeg_logs_default = os.environ.get("HIDE_FFMPEG_LOGS", "false").lower() in ("true", "1", "yes")


def process_cue_files(root, cues, ffmpeg_path, dir_out_current, dry_run, hide_ffmpeg_logs=False):
    """
    Process cue files in a given directory to split a multi-track music file.

    Iterates through each cue file, parsing it and, if valid, constructs and
    executes ffmpeg commands to split the source file.

    Args:
        root (str): The current directory path.
        cues (list): List of cue filenames in the directory.
        ffmpeg_path (str): Path to the ffmpeg executable.
        dir_out_current (str): Output directory for the processed files.
        dry_run (bool): If True, commands are not executed.
        hide_ffmpeg_logs (bool): If True, ffmpeg logs are hidden.

    Returns:
        tuple: A tuple (formats, bad_cues) where:
            - formats (set): Set of file extensions processed.
            - bad_cues (list): List of cue filenames that failed parsing.
    """
    processed_files = set()
    formats = set()
    bad_cues = []

    for cue in cues:
        cue_path = os.path.join(root, cue)
        status, general, tracks = parse_cue(cue_path)
        if status == 0:
            cue_music_file = os.path.join(root, general["file"])

            if not os.path.isfile(cue_music_file):
                bad_cues.append(cue)
                logging.error(f"Music file '{cue_music_file}' referenced in cue '{cue}' does not exist.")
                continue

            if cue_music_file not in processed_files:
                formats.add(pathlib.Path(general["file"]).suffix)
                cmds = make_split_cmd(tracks, ffmpeg_path, cue_music_file, dir_out_current, verbose=False)
                if not dry_run:
                    execute_commands(cmds, paral=True, hide_ffmpeg_logs=hide_ffmpeg_logs)
                    write_text_to_file(root, os.path.join(dir_out_current, 'source_ref.txt'))
                processed_files.add(cue_music_file)
                logging.info(f"Processed cue file '{cue}' in directory '{root}'.")
        elif status == 1:
            bad_cues.append(cue)
            logging.error(f"Failed to parse cue file '{cue}' in directory '{root}'.")
    return formats, bad_cues


def process_individual_music_files(root, music_files, ffmpeg_path, dir_out_current, dry_run, hide_ffmpeg_logs=False):
    """
    Process individual music files within a directory.

    For each music file, a command is generated to process the file via ffmpeg.
    If not in dry run mode, the commands are executed in parallel.

    Args:
        root (str): The current directory path.
        music_files (list): List of music file names in the directory.
        ffmpeg_path (str): Path to the ffmpeg executable.
        dir_out_current (str): Output directory for the processed files.
        dry_run (bool): If True, commands are not executed.
        hide_ffmpeg_logs (bool): If True, ffmpeg logs are hidden.
    """
    cmds = []
    for filename in music_files:
        file_path = os.path.join(root, filename)
        cmd = process_onefile(file_path, ffmpeg_path, dir_out_current)
        cmds.append(cmd)
    if not dry_run:
        execute_commands(cmds, paral=True, hide_ffmpeg_logs=hide_ffmpeg_logs)
        write_text_to_file(root, os.path.join(dir_out_current, 'source_ref.txt'))
    logging.info(f"Processed individual music files in directory '{root}': {music_files}")


def process_music_directory(dir_in, dir_out, ffmpeg_path, dry_run=False, hide_ffmpeg_logs=False):
    """
    Traverse the input directory to process music files and cue sheets.

    For each subdirectory in 'dir_in', the function:
      - Filters out music files (e.g., .flac, .ape, .wav, .alac, .tta) and cue files (.cue).
      - Creates a corresponding output directory in 'dir_out' if needed.
      - If cue files are present and the number of music files is less than or equal
        to the number of cues, it assumes a multi-track file that requires splitting.
      - Otherwise, processes individual music files.
      - Aggregates processed file formats, cue errors, and directories that contain only cues.

    Args:
        dir_in (str): Input directory containing music files.
        dir_out (str): Output directory for processed files.
        ffmpeg_path (str): Path to the ffmpeg executable.
        dry_run (bool, optional): If True, commands are not executed. Defaults to False.
        hide_ffmpeg_logs (bool): If True, ffmpeg logs are hidden.
    """
    ensure_directory_exists(dir_out)
    total_formats = set()
    all_bad_cues = []
    only_cue_dirs = []
    music_types = [".flac", ".ape", ".wav", ".alac", ".tta"]

    total_subdirs = sum(1 for _ in os.walk(dir_in))
    counter = 0

    for root, dirs, files in os.walk(dir_in):
        counter += 1
        logging.info(f"Processing directory {counter}/{total_subdirs}: {root}")
        logging.debug(f"Subdirectories: {dirs} | Files: {files}")

        # Create corresponding output directory based on the current root folder.
        dir_out_current = os.path.join(dir_out, os.path.basename(root))

        # Filter music and cue files.
        music_files = [f for f in files if pathlib.Path(f).suffix.lower() in music_types]
        cues = [f for f in files if pathlib.Path(f).suffix.lower() == ".cue"]

        if cues or music_files:
            ensure_directory_exists(dir_out_current)

        # Mark directories that contain only cue files.
        if cues and not music_files:
            only_cue_dirs.append(root)
            logging.warning(f"Directory '{root}' contains only cue files.")

        # Process cue files if the number of music files is less than or equal to the number of cues.
        if cues and (len(music_files) <= len(cues)):
            formats, bad_cues = process_cue_files(root, cues, ffmpeg_path, dir_out_current, dry_run, hide_ffmpeg_logs)
            total_formats.update(formats)
            all_bad_cues.extend(bad_cues)
        # Process individual music files.
        elif music_files:
            process_individual_music_files(root, music_files, ffmpeg_path, dir_out_current, dry_run, hide_ffmpeg_logs)

    logging.info("Processed file formats: " + ", ".join(total_formats))
    if all_bad_cues:
        logging.error("Bad cue files: " + ", ".join(all_bad_cues))
    if only_cue_dirs:
        logging.warning("Directories with only cue files: " + ", ".join(only_cue_dirs))


def execute_commands(cmds, paral=True, hide_ffmpeg_logs=False):
    """
    Execute a list of system commands.

    Depending on the 'paral' flag, the commands are executed in parallel
    using a process pool or sequentially using os.system. If hide_ffmpeg_logs is True,
    ffmpeg commands are modified to suppress their output.

    Args:
        cmds (list): A list of command strings to execute.
        paral (bool, optional): If True, execute commands in parallel. Defaults to True.
        hide_ffmpeg_logs (bool): If True, append output redirection to hide ffmpeg logs.
    """
    if hide_ffmpeg_logs:
        # Use appropriate redirection for Windows or Unix-based systems.
        if os.name == 'nt':
            cmds = [cmd + " >nul 2>&1" for cmd in cmds]
        else:
            cmds = [cmd + " >/dev/null 2>&1" for cmd in cmds]

    if paral:
        with ProcessPoolExecutor(max_workers=cpu_count()) as executor:
            for cmd in cmds:
                executor.submit(os.system, cmd)
                logging.debug(f"Submitted command for parallel execution: {cmd}")
    else:
        for cmd in cmds:
            os.system(cmd)
            logging.debug(f"Executed command: {cmd}")


def main(
    ffmpeg_path_default=ffmpeg_path_default,
    dir_in_default=dir_in_default,
    dir_out_default=dir_out_default,
    dry_run_default=dry_run_default,
    hide_ffmpeg_logs_default=hide_ffmpeg_logs_default
):
    parser = argparse.ArgumentParser(
        description="Process a music directory using cue sheets and music files."
    )
    parser.add_argument(
        '--ffmpeg_path',
        type=str,
        default=ffmpeg_path_default,
        help="Path to the ffmpeg executable. Default is taken from the environment variable FFMPEG_PATH."
    )
    parser.add_argument(
        '--dir_in',
        type=str,
        default=dir_in_default,
        help="Input directory containing music files. Default is taken from the environment variable DIR_IN."
    )
    parser.add_argument(
        '--dir_out',
        type=str,
        default=dir_out_default,
        help="Output directory where processed files will be saved. Default is taken from the environment variable DIR_OUT."
    )
    parser.add_argument(
        '--dry_run',
        action='store_true',
        default=dry_run_default,
        help="If set, commands will not be executed. Default is taken from the environment variable DRY_RUN."
    )
    parser.add_argument(
        '--hide_ffmpeg_logs',
        action='store_true',
        default=hide_ffmpeg_logs_default,
        help="If set, ffmpeg's output will be suppressed. Default is taken from the environment variable HIDE_FFMPEG_LOGS."
    )
    args = parser.parse_args()

    logging.info("Starting music directory processing.")
    process_music_directory(args.dir_in, args.dir_out, args.ffmpeg_path, args.dry_run, args.hide_ffmpeg_logs)
    logging.info("Finished processing.")


if __name__ == "__main__":
    main()
