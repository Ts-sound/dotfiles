#!/bin/bash

set -e

# install 
apt update
apt install -y vim  wget curl  tree \
    openssh-server vim zip git screen

# 
apt install -y  htop  net-tools  iputils-ping  lsof  tmux

# install can 
apt install -y  can-utils

# X11-forwarding 
sudo apt install xorg