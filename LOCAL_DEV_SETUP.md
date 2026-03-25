# Local Dev Setup Summary

This document summarizes the current local single-node setup committed in this workspace so readers can quickly see which ports and dependencies are in use.

## Runtime Baseline

- Backend runtime: JDK 21, Maven build under `jeecg-boot`
- Frontend runtime: Node.js 20+ and `pnpm` 10.28.1
- Default local startup mode: single-node backend + Vue 3 frontend

## Local Single-Node Ports

| Component | How it runs locally | Host / URL | Notes |
| --- | --- | --- | --- |
| Frontend dev server | `pnpm dev` in `jeecgboot-vue3` | `http://localhost:3100` | Vite dev server port comes from `jeecgboot-vue3/.env` |
| Backend single-node app | `JeecgSystemApplication` or packaged jar | `http://localhost:28080/jeecg-boot` | Spring Boot server port is `28080`, context path is `/jeecg-boot` |
| Frontend API proxy | Vite dev proxy | `/jeecgboot -> http://localhost:28080/jeecg-boot` | Configured in `jeecgboot-vue3/.env.development` |
| Frontend upload proxy | Vite dev proxy | `/upload -> http://localhost:3300/upload` | Kept as a separate local upload entry |
| Mobile/app domain placeholder | Backend config | `http://localhost:8051` | Reserved in backend `domainUrl.app` config |

## Current Dev Dependencies

- MySQL (backend `dev` profile): `10.92.82.149:30004`, database `jeecg-boot`
- Redis (backend `dev` profile): `10.92.82.149:40004`, database `0`
- AIRag pgvector default: `127.0.0.1:5432`, database `postgres`, table `embeddings`

Credentials are intentionally not repeated here. Check the corresponding `.yml` or `.env` files when you need the exact values.

## Frontend Environment Targets

- Development API target: `http://localhost:28080/jeecg-boot`
- Production frontend API target: `http://127.0.0.1:28080/jeecg-boot`
- Docker frontend API target: `http://jeecg-boot-system:28080/jeecg-boot`
- Development mock switch: `VITE_USE_MOCK = true`

## Docker Port Mapping

### Root `docker-compose.yml`

- Frontend nginx: `80 -> 80`
- Backend single-node service: `28080 -> 28080`
- MySQL: `13306 -> 3306`
- Pgvector: `5432 -> 5432`
- Redis is not published to the host in this compose file

### `jeecg-boot/docker-compose.yml`

- Backend single-node service: `28080 -> 28080`
- MySQL: `13306 -> 3306`
- Redis is not published to the host
- Pgvector host port is commented out

## Reader Notes

- If you start the frontend with `pnpm dev`, open `http://localhost:3100`.
- If you call the backend directly, use `http://localhost:28080/jeecg-boot`.
- If you package and run the backend jar from `jeecg-system-start`, the app may auto-create `config/` template files next to the jar working directory.
