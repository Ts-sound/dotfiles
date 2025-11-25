#!/bin/bash

set -e

# install common dependencies
apt update
apt install -y vim  wget curl openjdk-11-jdk zip unzip tree  python3-dev python3-pip \
    libssl-dev git subversion \
    graphviz doxygen pandoc 