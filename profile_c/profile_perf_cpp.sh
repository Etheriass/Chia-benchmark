#!/bin/bash
# profile_perf_cpp.sh

set -e

MODULE=$1  # e.g., chiapos
BINARY=./ProofOfSpace  # or relevant binary in build/
ARGS="create -k 28 -n 1"  # adjust as needed

cd ~/chia-project/$MODULE
perf record -F 99 -g -- ./build/$BINARY $ARGS
perf script > perf.stacks
