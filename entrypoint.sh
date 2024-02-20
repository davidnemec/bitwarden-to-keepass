#!/bin/sh

# Login to a VaultWarden instance
echo "Connecting to Vaultwarden instance at $VAULTWARDEN_URL"
bw config server "$VAULTWARDEN_URL"
BW_SESSION="$(bw login --raw)"
export BW_SESSION

# Set environment variables for the script
BW_PATH="$(which bw)"
export BW_PATH

# Convert the VaultWarden data to a KeePass file
bw sync
python3 bitwarden-to-keepass.py
bw lock

echo "KeePass file created successfully!"
