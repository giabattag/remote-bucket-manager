# Main helper for RBM transfer

import sys
from rbm import ssh_transfer

def print_usage():
    print("Usage:")
    print("  python rbm_transfer.py <mapping_file> <remote_host> <upload|download> [scp|rsync]")
    raise RuntimeError

if __name__ != "__main__": print_usage()

if len(sys.argv) < 4: print_usage()

mapping_file = sys.argv[1]
remote_host = sys.argv[2]
direction = sys.argv[3]
method = sys.argv[4] if len(sys.argv) > 4 else "scp"

ssh_transfer(mapping_file, remote_host, direction, method)

