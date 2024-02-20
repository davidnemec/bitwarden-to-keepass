FROM tangowithfoxtrot/bw-cli as builder

FROM python:3.11.0-slim-bullseye

COPY --from=builder /usr/local/bin/bw /bin/bw

WORKDIR /bitwarden-to-keepass

COPY . .

RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt
