# Private utils for Remote Bucket Manager

import os
import subprocess

"""
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
    result = subprocess.run(cmd)

    if result.returncode != 0:
        raise RuntimeError(f"Command failed: {' '.join(cmd)}")


