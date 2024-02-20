#!/bin/sh

# Check that the database password is set
if [ -z "$DATABASE_PASSWORD" ]; then
    echo "DATABASE_PASSWORD is not set"
    exit 1
fi

# If BITWARDEN_URL is not empty, set a custom Bitwarden instance
if [ "$BITWARDEN_URL" ]; then
    echo "Connecting to Bitwarden instance at $BITWARDEN_URL"
    bw config server "$BITWARDEN_URL"
fi

BW_SESSION="$(bw login --raw)"
export BW_SESSION

if [ -z "$BW_SESSION" ]; then
    echo "Failed to log in to Bitwarden"
    exit 1
fi

# Set environment variables for the script
BW_PATH="$(which bw)"
export BW_PATH

if [ -z "$DATABASE_NAME" ]; then
    DATABASE_NAME="bitwarden.kdbx"
fi

DATABASE_PATH="/exports/$DATABASE_NAME"
export DATABASE_PATH


# Convert the Bitwarden data to a KeePass file
bw sync || { echo "Failed to sync Bitwarden data"; exit 1; }
echo "Generating KeePass file $DATABASE_PATH"
python3 bitwarden-to-keepass.py || { echo "Failed to convert to KeePass"; exit 1; }
bw lock

# Log out of Bitwarden
bw logout

echo "KeePass file $DATABASE_PATH generated successfully"
