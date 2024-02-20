FROM python:3.11.0-slim-bullseye

WORKDIR /bitwarden-to-keepass
COPY . .

RUN apt-get update && \
    apt-get install -y unzip curl jq && \
    # Taken from https://github.com/tangowithfoxtrot/bw-docker/blob/main/Dockerfile#L7
    export VER=$(curl -H "Accept: application/vnd.github+json" https://api.github.com/repos/bitwarden/clients/releases | jq  -r 'sort_by(.published_at) | reverse | .[].name | select( index("CLI") )' | sed 's:.*CLI v::' | head -n 1) && \
    curl -LO "https://github.com/bitwarden/clients/releases/download/cli-v{$VER}/bw-linux-{$VER}.zip" && \
    unzip *.zip && chmod +x ./bw && \
    mv bw /bin/ && \
    pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt && \
    apt-get purge -y --auto-remove unzip curl jq && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*
