#!/usr/bin/env python3

'''
OPS445 Assignment 2 - Winter 2023
Program: assignment2.py
Author: Dilpreet Kaur
The python code in this file is original work written by
Dilpreet Kaur. No code in this file is copied from any other source
except those provided by the course instructor, including any person,
textbook, or on-line resource. I have not shared this python script
with anyone or anything except for submission for grading.
I understand that the Academic Honesty Policy will be enforced and
violators will be reported and appropriate action will be taken.

Description: Displays total system memory usage and process memory usage
using text bar graphs.

Date: 17 July 2026
'''

import argparse
import os
import sys


def parse_command_args() -> object:
    """Set up argparse and return the command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Memory Visualiser -- See Memory Usage Report with bar charts",
        epilog="Copyright 2023"
    )

    parser.add_argument(
        "-H",
        "--human-readable",
        action="store_true",
        help="Display memory amounts in human-readable format."
    )

    parser.add_argument(
        "-l",
        "--length",
        type=int,
        default=20,
        help="Specify the length of the graph. Default is 20."
    )

    parser.add_argument(
        "program",
        type=str,
        nargs="?",
        help=(
            "If a program is specified, show memory use of all associated "
            "processes. Show only total use if not."
        )
    )

    return parser.parse_args()


def percent_to_graph(percent: float, length: int = 20) -> str:
    """Convert a value between 0.0 and 1.0 into a graph string."""
    hashes = round(percent * length)
    spaces = length - hashes
    return "#" * hashes + " " * spaces


def get_sys_mem() -> int:
    """Return total system memory in kB."""
    with open("/proc/meminfo", "r") as file:
        for line in file:
            if line.startswith("MemTotal:"):
                return int(line.split()[1])
    return 0


def get_avail_mem() -> int:
    """Return currently available system memory in kB."""
    mem_free = 0
    swap_free = 0

    with open("/proc/meminfo", "r") as file:
        for line in file:
            if line.startswith("MemAvailable:"):
                return int(line.split()[1])
            if line.startswith("MemFree:"):
                mem_free = int(line.split()[1])
            if line.startswith("SwapFree:"):
                swap_free = int(line.split()[1])

    return mem_free + swap_free


def pids_of_prog(app_name: str) -> list:
    """Return a list of process IDs associated with an application."""
    output = os.popen("pidof " + app_name).read()
    return output.split()


def rss_mem_of_pid(proc_id: str) -> int:
    """Return the total resident memory used by a process in kB."""
    total_rss = 0

    with open("/proc/" + proc_id + "/smaps", "r") as file:
        for line in file:
            if line.startswith("Rss:"):
                total_rss += int(line.split()[1])

    return total_rss


def bytes_to_human_r(kibibytes: int, decimal_places: int = 2) -> str:
    """Convert a KiB value into a human-readable memory value."""
    suffixes = ["KiB", "MiB", "GiB", "TiB", "PiB"]
    suffix_index = 0
    result = float(kibibytes)

    while result >= 1024 and suffix_index < len(suffixes) - 1:
        result /= 1024
        suffix_index += 1

    return f"{result:.{decimal_places}f} {suffixes[suffix_index]}"


def print_memory_line(label: str, used: int, total: int,
                      graph_length: int, human_readable: bool) -> None:
    """Print one formatted memory usage line."""
    if total == 0:
        percent = 0.0
    else:
        percent = used / total

    graph = percent_to_graph(percent, graph_length)

    if human_readable:
        used_text = bytes_to_human_r(used)
        total_text = bytes_to_human_r(total)
    else:
        used_text = str(used)
        total_text = str(total)

    print(f"{label:<15}[{graph}| {percent:.0%}] {used_text}/{total_text}")


def main() -> None:
    """Run the memory visualiser."""
    args = parse_command_args()

    if args.length <= 0:
        print("Error: graph length must be greater than zero.", file=sys.stderr)
        sys.exit(1)

    total_memory = get_sys_mem()

    if not args.program:
        used_memory = total_memory - get_avail_mem()
        print_memory_line(
            "Memory",
            used_memory,
            total_memory,
            args.length,
            args.human_readable
        )
        return

    process_ids = pids_of_prog(args.program)

    if not process_ids:
        print(f"{args.program}: no running processes found")
        return

    program_total = 0

    for process_id in process_ids:
        try:
            process_memory = rss_mem_of_pid(process_id)
        except (FileNotFoundError, PermissionError, ProcessLookupError):
            process_memory = 0

        program_total += process_memory
        print_memory_line(
            process_id,
            process_memory,
            total_memory,
            args.length,
            args.human_readable
        )

    print_memory_line(
        args.program,
        program_total,
        total_memory,
        args.length,
        args.human_readable
    )


if __name__ == "__main__":
    main()
