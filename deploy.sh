#!/usr/bin/env bash
set -euo pipefail

PROJECT_DIR="/home/projectotibl/tibk"
IMAGE="tiblbaptista/projecto_tibl"

echo "==> A actualizar código..."
cd "$PROJECT_DIR"
git pull origin production

echo "==> A construir imagem..."
docker compose build web

echo "==> A reiniciar serviços..."
docker compose up -d

echo "==> A aplicar migrações..."
docker compose exec -T web python manage.py migrate --noinput

echo "==> A limpar imagens antigas..."
docker image prune -f

echo "✓ Deploy concluído."
