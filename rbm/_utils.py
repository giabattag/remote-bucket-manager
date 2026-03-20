# Private utils for Remote Bucket Manager

import os
import subprocess

r"""
Mapping file example:
# local_path,remote_path
./data/file1.txt,/remote/path/file1.txt
./data/folder,/remote/path/folder
C:\Users\me\file.bin,/remote/path/file.bin
"""
def parse_mapping_file(mapping_file):
    mappings = []

    with open(mapping_file, "r") as f:
        for line in f:
            line = line.strip()

            if not line or line.startswith("#"):
                continue

            parts = [p.strip() for p in line.split(",", 1)]
            if len(parts) != 2:
                raise ValueError(f"Invalid line: {line}")

            local, remote = parts
            mappings.append((local, remote))

    return mappings


def run_command(cmd):
    print(">>", " ".join(cmd))

    result = subprocess.run(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )

    if result.returncode != 0:
        error_msg = (
            f"\nCommand failed!\n"
            f"Exit code: {result.returncode}\n"
            f"Command: {' '.join(cmd)}\n"
            f"\n--- STDOUT ---\n{result.stdout}\n"
            f"--- STDERR ---\n{result.stderr}\n"
        )
        raise RuntimeError(error_msg)

    if result.stdout:
        print(result.stdout)

    return result

