FROM python:3.10-slim-bullseye

RUN apt update && apt install -y npm && \
    npm i -g @bitwarden/cli && \
    apt purge -y npm

WORKDIR /bitwarden-to-keepass

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY . .