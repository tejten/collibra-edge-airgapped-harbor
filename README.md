# Collibra Edge Air‑gapped Installation — Using Harbor Registry

A step‑by‑step guide to installing **Collibra Edge** in a fully air‑gapped environment using **Harbor** to host images & Helm charts.
**Tested OS:** RHEL 8.8 • **Audience:** Platform/DevOps • **Status:** Production‑ready

> This README is a quick overview. See the full guide in [`docs/`](docs/index.md).

## Contents
- [Scope & Prereqs](docs/index.md#scope--prerequisites)
- [1. Harbor Projects & Robot](docs/01-harbor.md)
- [2. Host Helm Charts (Shim + NGINX)](docs/02-helm-repo.md)
- [3. Enable Edge for CPSH](docs/03-enable-cpsh.md)
- [4. Prepare the Edge Node](docs/04-edge-node.md)
- [5. Verify & Troubleshoot](docs/05-verify.md)
- [6. Uninstall](docs/06-uninstall.md)

## Why this repo?
- Mirrors Edge images to Harbor while **preserving original subpaths**.
- Hosts charts behind a lightweight **AQL shim + NGINX/TLS**.
- Covers cert import, `registries.yaml`, and **air‑gapped gotchas**.

> Credits: Original material by **Tej Tenmattam** (Version 06, 2025‑09‑02). PDF reference included.  
