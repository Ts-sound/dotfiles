#!/bin/bash

set -e

# install C++ dependencies
apt update
apt install -y build-essential gdb cmake clang-format clang-tidy cppcheck valgrind lcov 