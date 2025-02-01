#!/bin/bash

function log_error() {
    echo "Error: $1" >&2
}

function get_bw_session() {
    local session
    session=$($BW_PATH login --raw || $BW_PATH unlock --raw)
    if [[ -z "$session" ]]; then
        log_error "Failed to obtain a Bitwarden session."
        exit 1
    fi
    echo "$session"
}

# Attempt to configure the server
if ! $BW_PATH config server "$BITWARDEN_URL"; then
    log_error "Ignoring error on configuring server. It might already be set."
fi

# Export Bitwarden session key
export BW_SESSION=$(get_bw_session)

# Synchronize Bitwarden vault
if ! $BW_PATH sync; then
    log_error "Failed to sync Bitwarden vault."
    exit 1
fi

# Run the main export script
if ! poetry run python run.py; then
    log_error "Failed to run main export script."
    exit 1
fi

# Lock Bitwarden vault
if ! $BW_PATH lock; then
    log_error "Failed to lock Bitwarden vault."
    exit 1
fi
