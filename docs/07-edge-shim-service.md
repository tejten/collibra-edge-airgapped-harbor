# 07 - Run edge-shim as a systemd service on RHEL 8

This document shows how to run `edge_shim.py` as a **systemd** service on RHEL 8 (instead of using `nohup ... &`).

The service will:
- start on boot
- restart on failure
- write logs to **journald** and also append to `/var/log/edge-shim.log` via `tee`

---

## Prerequisites

- `python3` installed
- Script present at: `/opt/edge-shim/edge_shim.py`
- Root content directory present at: `/srv/edge-repo`
- Port: `8080` available

---

## 1) Create the service user

Create a dedicated system user for the service:

```bash
sudo useradd --system --home-dir /opt/edge-shim --shell /sbin/nologin edge-shim
```

Make sure it can read/write whatever it needs under `/srv/edge-repo`:

```bash
sudo chown -R edge-shim:edge-shim /srv/edge-repo
```

> If `/srv/edge-repo` should be read-only, adjust accordingly, but the service user must be able to read the content.

---

## 2) Create the log file (fixes tee Permission denied)

If you previously ran edge-shim as root (via `nohup`), `/var/log/edge-shim.log` may be owned by root and not writable by `edge-shim`.

Create (or overwrite) the log file with the correct ownership:

```bash
sudo install -o edge-shim -g edge-shim -m 0644 /dev/null /var/log/edge-shim.log
```

Optional (SELinux): if SELinux is enforcing and you hit access issues, restore label:

```bash
sudo restorecon -v /var/log/edge-shim.log
```

---

## 3) Create the systemd service unit

Create `/etc/systemd/system/edge-shim.service`:

```bash
sudo tee /etc/systemd/system/edge-shim.service >/dev/null <<'EOF'
[Unit]
Description=Edge Shim
Wants=network-online.target
After=network-online.target

[Service]
Type=simple

# Recommended: run as a dedicated service user (adjust as needed)
User=edge-shim
Group=edge-shim

WorkingDirectory=/opt/edge-shim

ExecStart=/bin/bash -lc '/usr/bin/python3 /opt/edge-shim/edge_shim.py --root /srv/edge-repo --port 8080 2>&1 | /usr/bin/tee -a /var/log/edge-shim.log'

# Restart if it crashes
Restart=on-failure
RestartSec=3

# Make logs show up immediately (no buffering)
Environment=PYTHONUNBUFFERED=1

# Also capture logs in the journal (journalctl)
StandardOutput=journal
StandardError=inherit
SyslogIdentifier=edge-shim

[Install]
WantedBy=multi-user.target
EOF
```

---

## 4) Enable and start the service

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now edge-shim.service
```

---

## 5) Check status and logs

Check status:

```bash
sudo systemctl status edge-shim.service
```

Follow logs (file):

```bash
tail -f /var/log/edge-shim.log
```

Follow logs (journald):

```bash
sudo journalctl -u edge-shim.service -f
```

---

## 6) Stop / Start the service

Stop:

```bash
sudo systemctl stop edge-shim.service
```

Start:

```bash
sudo systemctl start edge-shim.service
```

Restart:

```bash
sudo systemctl restart edge-shim.service
```

---

## Troubleshooting

### `tee: /var/log/edge-shim.log: Permission denied`

Recreate the log file with the correct owner:

```bash
sudo install -o edge-shim -g edge-shim -m 0644 /dev/null /var/log/edge-shim.log
sudo systemctl restart edge-shim.service
```

Optional (SELinux):

```bash
sudo restorecon -v /var/log/edge-shim.log
sudo systemctl restart edge-shim.service
```

### Port 8080 is already in use

Check what is listening:

```bash
sudo ss -lntp | grep ':8080'
```

Check if an old `nohup` process is still running:

```bash
ps -ef | grep -E 'edge_shim\.py|edge-shim' | grep -v grep
```

Stop the old process and restart the systemd service.

### Open firewall for 8080 (if needed)

```bash
sudo firewall-cmd --permanent --add-port=8080/tcp
sudo firewall-cmd --reload
```
