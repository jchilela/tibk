#!/usr/bin/env bash
set -euo pipefail

# ──────────────────────────────────────────────
# Configuração — ajustar antes de usar
# ──────────────────────────────────────────────
VPS_NAME="vps-tibk"
BACKUP_DIR="/backups"
MEGA_PATH="mega:backups/${VPS_NAME}"
KEEP=3
LOG="/var/log/backup.log"

PROJECT_DIR="/home/projectotibl/tibk"

# Credenciais MySQL — preencher com os valores do .env
DB_NAME="tibldb"
DB_USER="root"
DB_PASSWORD=$(grep '^DB_PASSWORD=' "${PROJECT_DIR}/.env" | cut -d'=' -f2)

# rclone config (root configurou como root)
RCLONE_CONFIG="/root/.config/rclone/rclone.conf"

# ──────────────────────────────────────────────
# Helpers
# ──────────────────────────────────────────────
log() { echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*" | tee -a "$LOG"; }
die() { log "[ERRO] $*"; exit 1; }

# ──────────────────────────────────────────────
# Inicialização
# ──────────────────────────────────────────────
TIMESTAMP=$(date '+%Y-%m-%d_%H-%M')
FILENAME="backup_${VPS_NAME}_${TIMESTAMP}.tar.gz"
TMPDIR=$(mktemp -d)
trap 'rm -rf "$TMPDIR"' EXIT

mkdir -p "$BACKUP_DIR"
log "Início do backup → ${FILENAME}"

# ──────────────────────────────────────────────
# 1. Base de dados MySQL
# ──────────────────────────────────────────────
log "A fazer dump MySQL (${DB_NAME})..."
mysqldump -u "$DB_USER" -p"${DB_PASSWORD}" "$DB_NAME" > "$TMPDIR/db.sql" \
    || die "Falha no mysqldump"

# ──────────────────────────────────────────────
# 2. Ficheiros .env
# ──────────────────────────────────────────────
log "A copiar ficheiro .env..."
[ -f "${PROJECT_DIR}/.env" ] \
    && cp "${PROJECT_DIR}/.env" "$TMPDIR/" \
    || log "AVISO: .env não encontrado, a saltar"

# ──────────────────────────────────────────────
# 3. Media (uploads Django)
# ──────────────────────────────────────────────
log "A copiar pasta media/..."
[ -d "${PROJECT_DIR}/media" ] \
    && cp -r "${PROJECT_DIR}/media" "$TMPDIR/media" \
    || log "AVISO: pasta media/ não encontrada, a saltar"

# ──────────────────────────────────────────────
# 4. Configurações nginx
# ──────────────────────────────────────────────
log "A copiar configs nginx..."
[ -d "/etc/nginx/sites-available" ] \
    && cp -r /etc/nginx/sites-available "$TMPDIR/nginx-sites" \
    || true
[ -f "${PROJECT_DIR}/nginx_documentacao.conf" ] \
    && cp "${PROJECT_DIR}/nginx_documentacao.conf" "$TMPDIR/" \
    || true

# ──────────────────────────────────────────────
# 5. Serviços systemd
# ──────────────────────────────────────────────
log "A copiar serviços systemd..."
if ls /etc/systemd/system/*.service 2>/dev/null | grep -q .; then
    mkdir -p "$TMPDIR/systemd"
    cp /etc/systemd/system/*.service "$TMPDIR/systemd/"
fi

# ──────────────────────────────────────────────
# 6. Comprimir
# ──────────────────────────────────────────────
log "A comprimir..."
tar -czf "${BACKUP_DIR}/${FILENAME}" -C "$TMPDIR" . \
    || die "Falha ao comprimir"
log "Arquivo criado: ${BACKUP_DIR}/${FILENAME} ($(du -sh "${BACKUP_DIR}/${FILENAME}" | cut -f1))"

# ──────────────────────────────────────────────
# 7. Rotação local — manter apenas os ${KEEP} mais recentes
# ──────────────────────────────────────────────
log "Rotação local (manter ${KEEP})..."
ls -1t "${BACKUP_DIR}"/backup_${VPS_NAME}_*.tar.gz 2>/dev/null \
    | tail -n +$((KEEP + 1)) \
    | while read -r old; do
        log "A apagar local: ${old}"
        rm -f "$old"
    done

# ──────────────────────────────────────────────
# 8. Upload para MEGA
# ──────────────────────────────────────────────
log "A fazer upload para MEGA..."
rclone --config "$RCLONE_CONFIG" mkdir "$MEGA_PATH" 2>/dev/null || true
rclone --config "$RCLONE_CONFIG" copy "${BACKUP_DIR}/${FILENAME}" "$MEGA_PATH" \
    || die "Falha no upload para MEGA"
log "Upload concluído: ${MEGA_PATH}/${FILENAME}"

# ──────────────────────────────────────────────
# 9. Rotação no MEGA — manter apenas os ${KEEP} mais recentes
# ──────────────────────────────────────────────
log "Rotação no MEGA (manter ${KEEP})..."
rclone --config "$RCLONE_CONFIG" lsf "$MEGA_PATH" --include "backup_${VPS_NAME}_*.tar.gz" 2>/dev/null \
    | sort \
    | head -n -${KEEP} \
    | while read -r old_file; do
        log "A apagar MEGA: ${old_file}"
        rclone --config "$RCLONE_CONFIG" deletefile "${MEGA_PATH}/${old_file}" \
            || log "AVISO: falha ao apagar ${old_file} do MEGA"
    done

log "Backup concluído com sucesso."
