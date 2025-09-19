#!/usr/bin/env bash
set -euo pipefail

HARBOR_HOST="${HARBOR_HOST:-harbor.<YOUR_DOMAIN>}"
HARBOR_CERT="${HARBOR_CERT:-/data/cert/${HARBOR_HOST}.crt}"
ROBOT_USER="${ROBOT_USER:-robot$edge-all}"
ROBOT_TOKEN="${ROBOT_TOKEN:-<ROBOT_TOKEN>}"

# Example image list — update to match your chart versions
IMAGES=(
  edge/edgecli:2025.6.12
  edge/edge-controller:3.798.5
  sre/opentelemetry-collector:0.125.0
  capabilities/jdbc-ingestion:20.9.4
)

echo "$ROBOT_TOKEN" | docker login "${HARBOR_HOST}" --username "${ROBOT_USER}" --password-stdin

for img in "${IMAGES[@]}"; do
  docker pull edge-docker-delivery.repository.collibra.io/$img
  docker tag  edge-docker-delivery.repository.collibra.io/$img "${HARBOR_HOST}/$img"
  docker push "${HARBOR_HOST}/$img"
done

echo "Completed mirroring ${#IMAGES[@]} images to ${HARBOR_HOST}."
