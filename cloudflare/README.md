# Cloudflare Tunnel (cloudflared)

This project includes an optional `cloudflared` container in `docker-compose.yml` under the `tunnel` profile.

## Quick tunnel (no domain required)

Start everything + the tunnel:

```bash
docker compose --profile tunnel up -d --build
docker compose logs -f tunnel
```

Cloudflare will print a public URL in the tunnel logs.

## Named tunnel (your own domain)

If you want a stable hostname (e.g. `api.example.com`), create a Cloudflare Tunnel and credentials, then mount a config:

1) Create `cloudflare/config.yml` (copy from `config.yml.example`)
2) Put your credentials file at `cloudflare/cert.json`
3) Change the compose `tunnel` service to use the config file, e.g.
   - `command: tunnel --no-autoupdate --config /etc/cloudflared/config.yml run`
   - `volumes: - ./cloudflare:/etc/cloudflared:ro`

`cert.json` is ignored by git on purpose.
