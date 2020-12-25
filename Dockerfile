FROM python:3.9-slim-buster

WORKDIR /bitwarden-to-keepass
COPY . .

RUN apt update && apt install -y npm && \
    pip install -r requirements.txt && \
    npm i -g @bitwarden/cli && \
    apt purge -y npm
