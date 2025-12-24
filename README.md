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
- [7. Run edge-shim as a systemd service](docs/07-edge-shim-service.md)

## Why this repo?

Edge provides seamless native integrations and on-site data processing solutions that prioritize security and proximity to the data, while keeping the processing of your data within your own environment. It processes the data source information on the Edge site and sends the process results to Collibra. 

Currently (Sepetember,2025), Collibra Edge only supports using the [JFrog private Helm registry](https://productresources.collibra.com/docs/collibra/latest/Content/Edge/EdgeSecurity/ta_user-pass-registry.htm#tab-Private_Helm_registry) with user/pass authentication. For customers, who prefer a open source registry option like Harbor, this repository provides a solution. 

Here are the high level steps: 

- Mirrors Edge images to Harbor while **preserving original subpaths**.
- Hosts charts behind a lightweight **AQL shim + NGINX/TLS**.
- Covers cert import, `registries.yaml`, and **air‑gapped gotchas**.

> Credits: Original material by **Tej Tenmattam** (Version 07, 2025‑09‑19).  
