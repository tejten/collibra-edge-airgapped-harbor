# 5. Verify & Troubleshoot

## 5.1 Common checks
```bash
kubectl -n collibra-edge get pods -o wide
POD=$(kubectl -n collibra-edge get pods -o name | head -n1 | cut -d/ -f2)
kubectl -n collibra-edge describe pod "$POD" | less

# What k3s actually uses:
cat /etc/rancher/k3s/registries.yaml

# Images in all running pods (path sanity check)
kubectl get pods -A -o jsonpath='{range .items[*]}{.metadata.namespace}{"\t"}{.spec.containers[*].image}{"\n"}{end}' | sort -u

# Node cache
crictl images | awk '{print $3,$1}' | sort -u
```

## 5.2 CPSH localhost redirect workaround (IPv4)
If you see errors indicating that `localhost:5443` requires TLS, add an nftables redirect:
```bash
nft add table ip nat 2>/dev/null || true
nft 'add chain ip nat output { type nat hook output priority 0; }' 2>/dev/null || true
nft add rule ip nat output ip daddr 127.0.0.1 tcp dport 5443 redirect to 4400

# Verify
nft -a list chain ip nat output
curl -4 -sI http://127.0.0.1:5443/edge/api/rest/v2/sites | head -n1

# Remove later if needed
nft -a list chain ip nat output
nft delete rule ip nat output handle <HANDLE>
```
