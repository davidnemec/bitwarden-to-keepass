# First stage: Download and extract the Bitwarden CLI
FROM python:3.11.0-slim-bullseye as builder

# Install dependencies for downloading and extracting Bitwarden CLI
RUN apt-get update && \
    apt-get install -y --no-install-recommends curl jq unzip

# Download and extract Bitwarden CLI
# Taken from https://github.com/tangowithfoxtrot/bw-docker/blob/main/Dockerfile#L7
RUN export VER=$(curl -H "Accept: application/vnd.github+json" https://api.github.com/repos/bitwarden/clients/releases | jq -r 'sort_by(.published_at) | reverse | .[].name | select( index("CLI") )' | sed 's:.*CLI v::' | head -n 1) && \
    curl -LO "https://github.com/bitwarden/clients/releases/download/cli-v${VER}/bw-linux-${VER}.zip" && \
    unzip *.zip && \
    chmod +x ./bw

# Second stage: Build the final image
FROM python:3.11.0-slim-bullseye

# Copy Bitwarden CLI from the builder stage
COPY --from=builder /bw /bin/bw

# Set up the working directory
WORKDIR /bitwarden-to-keepass

# Copy the application files
COPY . .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Clean up unnecessary files to reduce image size
RUN apt-get clean && \
    rm -rf /var/lib/apt/lists/*
