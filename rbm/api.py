# API for Remote Bucket Manager

import os
import sys
import subprocess

from ._utils import expand_remote_path, ensure_local_dir, ensure_ssh_agent, parse_mapping_file, run_command, list_remote_files, ensure_remote_dir, is_remote_dir

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
        if "~" in remote:
            remote = expand_remote_path(remote_host, remote)

        if "*" in local or "*" in remote:
            raise ValueError("Wildcard '*' not supported")

        # =========================
        # SCP MODE (FILE-BY-FILE)
        # =========================
        if method == "scp":

            # -------- UPLOAD --------
            if direction == "upload":
                if os.path.isdir(local):
                    for root, _, files in os.walk(local):
                        for f in files:
                            local_file = os.path.join(root, f)

                            rel = os.path.relpath(local_file, local)
                            remote_file = os.path.join(remote, rel).replace("\\", "/")

                            ensure_remote_dir(remote_host, remote_file)

                            cmd = [
                                "scp",
                                local_file,
                                f"{remote_host}:{remote_file}"
                            ]
                            run_command(cmd)

                else:
                    ensure_remote_dir(remote_host, remote)

                    cmd = [
                        "scp",
                        local,
                        f"{remote_host}:{remote}"
                    ]
                    run_command(cmd)

            # -------- DOWNLOAD --------
            else:
                # Check if remote is directory
                is_dir = is_remote_dir(remote_host, remote)
                if is_dir:
                    files = list_remote_files(remote_host, remote)

                    for remote_file in files:
                        rel = os.path.relpath(remote_file, remote)
                        local_file = os.path.join(local, rel)

                        ensure_local_dir(local_file)

                        cmd = [
                            "scp",
                            f"{remote_host}:{remote_file}",
                            local_file
                        ]
                        run_command(cmd)

                else:
                    ensure_local_dir(local)

                    cmd = [
                        "scp",
                        f"{remote_host}:{remote}",
                        local
                    ]
                    run_command(cmd)

        # =========================
        # RSYNC MODE (UNCHANGED)
        # =========================
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

            run_command(cmd)
        else:
            raise ValueError("method must be 'scp' or 'rsync'")


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

