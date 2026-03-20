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

def ensure_local_dir(local_path):
    # Extract directory part
    local_dir = os.path.dirname(local_path)

    cmd = [
        "mkdir", "-p", local_dir
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
    Ensure ssh-agent is running and key is loaded.
    Cross-platform (Windows + Unix).
    """

    key_path = os.path.expanduser("~/.ssh/id_rsa")

    # =========================
    # WINDOWS
    # =========================
    if os.name == "nt":
        print("[INFO] Checking ssh-agent (Windows)...")

        # Check if ssh-agent process is running
        result = subprocess.run(
            ["tasklist", "/FI", "IMAGENAME eq ssh-agent.exe"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        if "ssh-agent.exe" not in result.stdout:
            print("[INFO] ssh-agent not running, starting it...")

            # Start the service (more reliable than Start-Process)
            subprocess.run(
                ["powershell", "-Command", "Start-Service ssh-agent"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
        else:
            print("[INFO] ssh-agent already running.")

        # Check if key already added
        result = subprocess.run(
            ["ssh-add", "-L"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        if key_path not in result.stdout:
            print("[INFO] Adding SSH key...")
            subprocess.run(["ssh-add", key_path])
        else:
            print("[INFO] SSH key already added.")

    # =========================
    # LINUX / MAC / GIT BASH
    # =========================
    else:
        print("[INFO] Checking ssh-agent (Unix)...")

        # If agent already exists → reuse
        if os.environ.get("SSH_AUTH_SOCK"):
            print("[INFO] ssh-agent already available.")
        else:
            print("[INFO] Starting ssh-agent...")

            proc = subprocess.run(
                ["ssh-agent", "-s"],
                stdout=subprocess.PIPE,
                text=True
            )

            # Parse env variables
            for line in proc.stdout.splitlines():
                if "=" in line:
                    key, val = line.split(";", 1)[0].split("=", 1)
                    os.environ[key] = val

        # Check if key loaded
        result = subprocess.run(
            ["ssh-add", "-L"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        if "The agent has no identities" in result.stdout or result.returncode != 0:
            print("[INFO] Adding SSH key...")
            subprocess.run(["ssh-add", key_path])
        else:
            print("[INFO] SSH key already loaded.")

