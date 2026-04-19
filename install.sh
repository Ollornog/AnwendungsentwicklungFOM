#!/usr/bin/env bash
#
# install.sh – Setup der Preisoptimierung auf Debian 12.
#
# Idempotent: erneuter Aufruf aktualisiert Code und Abhängigkeiten, ohne Daten zu verlieren.
# Benötigt Root (apt, systemd, nginx, postgres).
#
# Ergebnis:
#   - PostgreSQL 16 mit Datenbank 'preisopt' und User 'preisopt'
#   - Backend unter /opt/preisopt/ (Code, venv, .env)
#   - systemd-Unit 'preisopt-backend' (uvicorn auf 127.0.0.1:8000)
#   - nginx-Reverse-Proxy auf Port 80 → uvicorn
#
# Nutzung:
#   sudo ./install.sh                 – vollständige Einrichtung (fragt nach Admin-Passwort)
#   sudo ./install.sh --skip-seed     – keine Mock-Produkte anlegen
#   sudo ./install.sh --no-nginx      – ohne Reverse-Proxy (uvicorn direkt auf 8000)

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
APP_DIR="/opt/preisopt"
APP_USER="preisopt"
DB_NAME="preisopt"
DB_USER="preisopt"
PY_BIN="python3"

SKIP_SEED=false
WITH_NGINX=true
ADMIN_USERNAME="admin"
ADMIN_PASSWORD="${PREISOPT_ADMIN_PASSWORD:-}"
DB_PASSWORD="${PREISOPT_DB_PASSWORD:-}"
GEMINI_API_KEY="${GEMINI_API_KEY:-}"

log() { printf '\033[1;34m[install]\033[0m %s\n' "$*"; }
warn() { printf '\033[1;33m[warn]\033[0m %s\n' "$*" >&2; }
die() { printf '\033[1;31m[error]\033[0m %s\n' "$*" >&2; exit 1; }

while [[ $# -gt 0 ]]; do
  case "$1" in
    --skip-seed) SKIP_SEED=true ;;
    --no-nginx) WITH_NGINX=false ;;
    --admin-username) ADMIN_USERNAME="$2"; shift ;;
    -h|--help)
      sed -n '2,18p' "$0" | sed 's/^# \{0,1\}//'
      exit 0 ;;
    *) die "Unbekannte Option: $1" ;;
  esac
  shift
done

[[ $EUID -eq 0 ]] || die "Bitte als root ausführen (sudo ./install.sh)."

require_debian_12() {
  if [[ -r /etc/os-release ]]; then
    # shellcheck disable=SC1091
    . /etc/os-release
    if [[ "${ID:-}" == "debian" && "${VERSION_ID:-}" != "12" ]]; then
      warn "Ziel ist Debian 12, erkannt wurde ${PRETTY_NAME:-unbekannt}. Fortfahren."
    fi
  fi
}

random_password() {
  tr -dc 'A-Za-z0-9' < /dev/urandom | head -c 32
}

prompt_secrets() {
  if [[ -z "$ADMIN_PASSWORD" ]]; then
    read -rsp "Passwort für Admin-User '${ADMIN_USERNAME}': " ADMIN_PASSWORD
    echo
    [[ -n "$ADMIN_PASSWORD" ]] || die "Admin-Passwort darf nicht leer sein."
  fi
  if [[ -z "$DB_PASSWORD" ]]; then
    DB_PASSWORD="$(random_password)"
    log "DB-Passwort generiert (wird in /opt/preisopt/.env gespeichert)."
  fi
}

install_packages() {
  log "apt: Pakete installieren"
  export DEBIAN_FRONTEND=noninteractive
  apt-get update -qq
  local pkgs=(
    ca-certificates curl git build-essential
    python3 python3-venv python3-dev
    postgresql postgresql-contrib libpq-dev
  )
  if $WITH_NGINX; then pkgs+=(nginx); fi
  apt-get install -y --no-install-recommends "${pkgs[@]}"
}

ensure_app_user() {
  if ! id -u "$APP_USER" >/dev/null 2>&1; then
    log "Benutzer '$APP_USER' anlegen"
    useradd --system --home "$APP_DIR" --shell /usr/sbin/nologin "$APP_USER"
  fi
}

deploy_code() {
  log "Code nach $APP_DIR kopieren"
  install -d -o "$APP_USER" -g "$APP_USER" -m 0755 "$APP_DIR"
  for dir in backend frontend deploy; do
    rsync -a --delete --chown="$APP_USER:$APP_USER" "$SCRIPT_DIR/$dir/" "$APP_DIR/$dir/"
  done
}

setup_postgres() {
  log "PostgreSQL: Benutzer und Datenbank einrichten"
  systemctl enable --now postgresql >/dev/null 2>&1 || true

  local user_exists
  user_exists=$(sudo -u postgres psql -tAc "SELECT 1 FROM pg_roles WHERE rolname='$DB_USER'")
  if [[ "$user_exists" == "1" ]]; then
    sudo -u postgres psql -c "ALTER USER $DB_USER WITH ENCRYPTED PASSWORD '$DB_PASSWORD';" >/dev/null
  else
    sudo -u postgres psql -c "CREATE USER $DB_USER WITH ENCRYPTED PASSWORD '$DB_PASSWORD';" >/dev/null
  fi

  local db_exists
  db_exists=$(sudo -u postgres psql -tAc "SELECT 1 FROM pg_database WHERE datname='$DB_NAME'")
  if [[ "$db_exists" != "1" ]]; then
    sudo -u postgres createdb -O "$DB_USER" "$DB_NAME"
  fi

  sudo -u postgres psql -d "$DB_NAME" -c 'CREATE EXTENSION IF NOT EXISTS "pgcrypto";' >/dev/null
}

write_env_file() {
  log "Schreibe $APP_DIR/.env"
  local env_file="$APP_DIR/.env"
  local session_secret
  if [[ -f "$env_file" ]] && grep -q '^SESSION_SECRET=' "$env_file"; then
    session_secret="$(grep '^SESSION_SECRET=' "$env_file" | cut -d= -f2-)"
  else
    session_secret="$(random_password)$(random_password)"
  fi
  umask 077
  cat > "$env_file" <<EOF
DATABASE_URL=postgresql+psycopg://${DB_USER}:${DB_PASSWORD}@127.0.0.1:5432/${DB_NAME}
SESSION_SECRET=${session_secret}
APP_ENV=production
GEMINI_API_KEY=${GEMINI_API_KEY}
GEMINI_MODEL=gemini-2.5-flash
FRONTEND_DIR=${APP_DIR}/frontend
SUGGESTION_TTL_MINUTES=15
EOF
  chown "$APP_USER:$APP_USER" "$env_file"
  chmod 640 "$env_file"
}

setup_venv() {
  log "Python venv und Abhängigkeiten"
  sudo -u "$APP_USER" "$PY_BIN" -m venv "$APP_DIR/.venv"
  sudo -u "$APP_USER" "$APP_DIR/.venv/bin/pip" install --upgrade pip wheel
  sudo -u "$APP_USER" "$APP_DIR/.venv/bin/pip" install -r "$APP_DIR/backend/requirements.txt"
}

run_migrations() {
  log "Alembic: Migrationen anwenden"
  sudo -u "$APP_USER" bash -c "cd $APP_DIR/backend && set -a && source $APP_DIR/.env && set +a && $APP_DIR/.venv/bin/alembic upgrade head"
}

run_seed() {
  if $SKIP_SEED; then
    log "Seed übersprungen (--skip-seed)"
    return
  fi
  log "Seed: Admin-User und Mock-Produkte"
  sudo -u "$APP_USER" bash -c "cd $APP_DIR/backend && set -a && source $APP_DIR/.env && set +a && $APP_DIR/.venv/bin/python -m seed --username '$ADMIN_USERNAME' --password '$ADMIN_PASSWORD'"
}

install_systemd() {
  log "systemd: Service einrichten"
  install -m 0644 "$APP_DIR/deploy/preisopt-backend.service" /etc/systemd/system/preisopt-backend.service
  systemctl daemon-reload
  systemctl enable preisopt-backend >/dev/null
  systemctl restart preisopt-backend
}

install_nginx() {
  $WITH_NGINX || { log "nginx übersprungen (--no-nginx). Backend lauscht auf 127.0.0.1:8000."; return; }
  log "nginx: Reverse-Proxy konfigurieren"
  install -m 0644 "$APP_DIR/deploy/nginx-preisopt.conf" /etc/nginx/sites-available/preisopt
  ln -sf /etc/nginx/sites-available/preisopt /etc/nginx/sites-enabled/preisopt
  rm -f /etc/nginx/sites-enabled/default
  nginx -t
  systemctl enable --now nginx >/dev/null 2>&1 || true
  systemctl reload nginx
}

summary() {
  local port
  if $WITH_NGINX; then port=80; else port=8000; fi
  log "Fertig."
  printf '  URL:         http://<server-ip>:%s/\n' "$port"
  printf '  Admin-User:  %s\n' "$ADMIN_USERNAME"
  printf '  .env:        %s/.env\n' "$APP_DIR"
  printf '  Service:     systemctl status preisopt-backend\n'
  if [[ -z "$GEMINI_API_KEY" ]]; then
    warn "GEMINI_API_KEY ist leer — LLM-Strategie schlägt fehl, bis er in $APP_DIR/.env gesetzt ist."
  fi
}

main() {
  require_debian_12
  prompt_secrets
  install_packages
  ensure_app_user
  deploy_code
  setup_postgres
  write_env_file
  setup_venv
  run_migrations
  run_seed
  install_systemd
  install_nginx
  summary
}

main "$@"
