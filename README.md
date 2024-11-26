## Installation

Install loki docker plugin:
```sh
docker plugin install grafana/loki-docker-driver:2.9.2 --alias loki --grant-all-permissions
```

Enable loki:
```sh
docker plugin enable loki
```

## Running
Run all services with `production` profile:
```sh
docker compose --profile production up -d
```