# API for Remote Bucket Manager

import sys

from ._utils import ensure_ssh_agent, parse_mapping_file, run_command, ensure_remote_dir

r"""
Mapping file example:
# local_path,remote_path
./data/file1.txt,/remote/path/file1.txt
./data/folder,/remote/path/folder
C:\Users\me\file.bin,/remote/path/file.bin
"""

def ssh_transfer(mapping_file, remote_host, direction="upload", method="scp"):
    """
    direction: 'upload' or 'download'
    method: 'scp' or 'rsync'
    """

    ensure_ssh_agent()

    mappings = parse_mapping_file(mapping_file)

    for local, remote in mappings:

        if method == "scp":
            if direction == "upload":
                ensure_remote_dir(remote_host, remote)
                src = local
                dst = f"{remote_host}:{remote}"
            else:
                src = f"{remote_host}:{remote}"
                dst = local

            cmd = ["scp", "-r", src, dst]

        elif method == "rsync":
            if direction == "upload":
                src = local
                dst = f"{remote_host}:{remote}"
            else:
                src = f"{remote_host}:{remote}"
                dst = local

            cmd = [
                "rsync",
                "-avz",
                "--progress",
                src,
                dst
            ]

        else:
            raise ValueError("method must be 'scp' or 'rsync'")

        run_command(cmd)


if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Usage:")
        print("  python ssh_transfer.py <mapping_file> <remote_host> <upload|download> [scp|rsync]")
        sys.exit(1)

    mapping_file = sys.argv[1]
    remote_host = sys.argv[2]
    direction = sys.argv[3]
    method = sys.argv[4] if len(sys.argv) > 4 else "scp"

    ssh_transfer(mapping_file, remote_host, direction, method)

