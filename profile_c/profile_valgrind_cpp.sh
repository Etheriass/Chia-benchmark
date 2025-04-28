#!/bin/bash
# profile_valgrind_cpp.sh

set -e

MODULE=$1
BINARY=ProofOfSpace
ARGS="create -k 24 -n 1"

#cd ~/chia-project/$MODULE

ulimit -n 1048576


valgrind --tool=callgrind ~/chia-project/$MODULE/$BINARY $ARGS
