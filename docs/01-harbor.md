# 1. Harbor Setup

> **Goal:** Create Harbor projects and a robot account, log in to the Collibra delivery registry, and mirror images to Harbor while preserving original subpaths.

## 1.0 Create Harbor projects & a robot
```bash
export HARBOR_HOST="harbor.<YOUR_DOMAIN>"
export HARBOR_URL="https://${HARBOR_HOST}"
export HARBOR_CERT="/data/cert/${HARBOR_HOST}.crt"
export HARBOR_ADMIN="admin"
export HARBOR_ADMIN_INITIAL="<CHANGE_ME>"

# Create projects
for p in edge sre capabilities; do
  curl -sS --cacert "$HARBOR_CERT" -u "admin:${HARBOR_ADMIN_INITIAL}"     -H "Content-Type: application/json"     -X POST "$HARBOR_URL/api/v2.0/projects"     -d "{"project_name":"$p","metadata":{"public":"true"}}" || true
done

# Create a robot with push/pull on all projects (save the returned token securely)
cat >/tmp/robot-all.json <<'EOF'
{ "name":"edge-all","description":"Robot for edge/sre/capabilities","duration":-1,"disable":false,
  "level":"system","permissions":[{"kind":"project","namespace":"*",
  "access":[{"resource":"repository","action":"pull"},{"resource":"repository","action":"push"}]}]}
EOF

ROBOT_JSON=$(curl -sS --cacert "$HARBOR_CERT" -u "admin:${HARBOR_ADMIN_INITIAL}"   -H "Content-Type: application/json" -X POST   "$HARBOR_URL/api/v2.0/robots" --data-binary @/tmp/robot-all.json)

export ROBOT_USER=$(echo "$ROBOT_JSON" | yq -p=json -r '.name')
export ROBOT_TOKEN=$(echo "$ROBOT_JSON" | yq -p=json -r '.secret')

echo "$ROBOT_TOKEN" | docker login "${HARBOR_HOST}" --username "${ROBOT_USER}" --password-stdin
```

## 1.1 Log in to Collibra delivery registry
```bash
docker login edge-docker-delivery.repository.collibra.io   -u <edge-customer-id> -p <TOKEN>
```

## 1.2 Mirror images to Harbor (preserve original subpaths)
```bash
IMAGES=(
  edge/edgecli:2025.6.12
  edge/edge-controller:3.798.5
  edge/edge-objects-server:3.798.5
  edge/edge-proxy:0.282.8
  edge/edge-sdk:5.399.2
  edge/edge-session-manager:6.90.4
  sre/opentelemetry-collector:0.125.0
  capabilities/jdbc-ingestion:20.9.4
  capabilities/sample-writer:1.15.6
  capabilities/jdbc-profiling:7.1.50 
  capabilities/modular-classification:0.18.6
)

echo "$ROBOT_TOKEN" | docker login "${HARBOR_HOST}" --username "${ROBOT_USER}" --password-stdin

for img in "${IMAGES[@]}"; do
  docker pull edge-docker-delivery.repository.collibra.io/$img
  docker tag  edge-docker-delivery.repository.collibra.io/$img "${HARBOR_HOST}/$img"
  docker push "${HARBOR_HOST}/$img"
done

# Verify a tag exists
curl -sS --cacert "$HARBOR_CERT" -u "${ROBOT_USER}:${ROBOT_TOKEN}"   "${HARBOR_URL}/v2/edge/edgecli/tags/list" | yq -p=json
```
