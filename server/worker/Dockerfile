FROM prefecthq/prefect:3-latest

RUN apt update \
 && apt install -y --no-install-recommends docker.io \
 && pip install --no-cache-dir prefect-docker \
 && rm -rf /var/lib/apt/lists/*
