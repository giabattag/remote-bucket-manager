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

def ensure_remote_dir(remote_host, remote_path):
    # Extract directory part
    remote_dir = os.path.dirname(remote_path)

    cmd = [
        "ssh",
        remote_host,
        f"mkdir -p {remote_dir}"
    ]

    run_command(cmd)

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

def ensure_ssh_agent():
    """
    Ensure ssh-agent is running and a key is loaded.
    Works on Linux/macOS/Windows (PowerShell + Git Bash).
    """

    # If agent already available → nothing to do
    if os.environ.get("SSH_AUTH_SOCK"):
        return

    print("[INFO] No ssh-agent detected, starting one...")

    if os.name == "nt":
        # Windows (PowerShell OpenSSH)
        try:
            subprocess.run(
                ["powershell", "-Command",
                 "Start-Service ssh-agent"],
                check=False
            )
        except Exception:
            pass

        # Try to add key (will prompt once)
        key_path = os.path.expanduser("~/.ssh/id_rsa")
        subprocess.run(["ssh-add", key_path])

    else:
        # Linux / macOS / Git Bash
        proc = subprocess.run(
            ["ssh-agent", "-s"],
            stdout=subprocess.PIPE,
            text=True
        )

        # Extract env variables
        for line in proc.stdout.splitlines():
            if "SSH_AUTH_SOCK" in line or "SSH_AGENT_PID" in line:
                key, _, value = line.partition("=")
                value = value.split(";")[0]
                os.environ[key] = value

        # Add key (will prompt once)
        key_path = os.path.expanduser("~/.ssh/id_rsa")
        subprocess.run(["ssh-add", key_path])

