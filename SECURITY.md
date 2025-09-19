# Security & Secrets

This repository contains **examples only**. Do **not** commit real secrets or private keys.

- Replace tokens/passwords with placeholders: `<TOKEN>`, `<PASSWORD>`, `<ROBOT_TOKEN>`.
- Do **not** commit `registries.yaml`. Use `registries.example.yaml` as a template.
- Keep certificates and keys (`*.crt`, `*.key`, `*.pem`, keystores) out of version control.
- Enable **GitHub Secret Scanning** in repo settings.
- Consider local pre‑commit checks with `detect-secrets` or `git-secrets`.

If you accidentally pushed a secret:
1. **Revoke/rotate** it immediately.
2. Force‑push a fix only after the key is invalidated.
