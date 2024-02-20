#!/bin/sh

# Login to a custom Bitwarden instance
if [ "$BITWARDEN_URL" ]; then
    echo "Connecting to Bitwarden instance at $BITWARDEN_URL"
    bw config server "$BITWARDEN_URL"
fi

BW_SESSION="$(bw login --raw)"
export BW_SESSION

# Set environment variables for the script
BW_PATH="$(which bw)"
export BW_PATH

DATABASE_PATH="/exports/$DATABASE_NAME"
export DATABASE_PATH

# Convert the Bitwarden data to a KeePass file
bw sync
python3 bitwarden-to-keepass.py
bw lock

echo "KeePass file $DATABASE_NAME generated successfully"
