FROM python:3.12-slim-bookworm

RUN apt-get update && \
    apt-get install -y --no-install-recommends wget unzip && \
    wget -O "bw.zip" "https://github.com/bitwarden/clients/releases/download/cli-v2024.6.0/bw-linux-2024.6.0.zip" && \
    unzip bw.zip && \
    chmod +x ./bw && \
    mv ./bw /usr/local/bin/bw && \
    apt-get purge -y --auto-remove wget unzip && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* && \
    rm -rf bw.zip

WORKDIR /bitwarden-to-keepass
COPY pyproject.toml poetry.lock ./

RUN pip install --no-cache-dir poetry && \
    poetry install

COPY . .
