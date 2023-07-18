FROM python:3.11-slim-bookworm

RUN apt update && apt install -y npm && \
    npm i -g @bitwarden/cli && \
    apt purge -y npm

WORKDIR /bitwarden-to-keepass

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY . .