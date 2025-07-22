#!/bin/sh
docker pull minio/mc:latest
docker pull minio/minio:RELEASE.2025-04-22T22-12-26Z
docker pull postgres:17-alpine3.22
docker pull prefecthq/prefect:3-latest
docker pull python:3
docker compose --env-file ./.env -p prefect up -d --build
