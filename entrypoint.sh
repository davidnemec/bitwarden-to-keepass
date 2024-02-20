#!/bin/sh


bw config server http://192.168.0.186:9998

export BW_SESSION="$(bw login --raw)"

bw sync

python3 bitwarden-to-keepass.py

bw lock
