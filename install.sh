#!/usr/bin/env bash
#
# install.sh – Setup der Preisoptimierung auf Debian 12.
#
# Ausgelegt auf ein FRISCH installiertes Debian 12 (Netinstall/Cloud-Image) –
# setzt nichts voraus außer Root-Rechten und Internet. Alle Abhängigkeiten
# werden über `apt` bezogen; es werden keine Fremdquellen hinzugefügt.
#
# Idempotent: erneuter Aufruf aktualisiert Code und Abhängigkeiten, ohne
# Daten zu verlieren.
#
# Ergebnis:
#   - PostgreSQL 16 mit Datenbank 'preisopt' und User 'preisopt'
#   - Backend unter /opt/preisopt/ (Code, venv, .env)
#   - systemd-Unit 'preisopt-backend' (uvicorn auf 127.0.0.1:8000)
#   - nginx-Reverse-Proxy auf Port 80 → uvicorn
#
# Nutzung:
#   ./install.sh                    – als root aufrufen
#   sudo ./install.sh               – mit sudo
#   ./install.sh --skip-seed        – keine Mock-Produkte anlegen
#   ./install.sh --no-nginx         – ohne Reverse-Proxy (uvicorn direkt auf 8000)
#   ./install.sh --upgrade-system   – vorher `apt-get upgrade` ausführen
#   ./install.sh --admin-username x – Admin-User überschreiben (Default: admin)

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
APP_DIR="/opt/preisopt"
APP_USER="preisopt"
DB_NAME="preisopt"
DB_USER="preisopt"
PY_BIN="python3"

SKIP_SEED=false
WITH_NGINX=true
UPGRADE_SYSTEM=false
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
    --upgrade-system) UPGRADE_SYSTEM=true ;;
    --admin-username) ADMIN_USERNAME="$2"; shift ;;
    -h|--help)
      sed -n '2,25p' "$0" | sed 's/^# \{0,1\}//'
      exit 0 ;;
    *) die "Unbekannte Option: $1" ;;
  esac
  shift
done

[[ $EUID -eq 0 ]] || die "Bitte als root ausführen (sudo ./install.sh)."

# runuser ist Teil von util-linux und damit auf jedem Debian verfügbar,
# auch wenn sudo nicht installiert ist. Wir nutzen es überall, wo wir in
# einen anderen User wechseln müssen.
as_user() {
  local target_user="$1"; shift
  runuser -u "$target_user" -- "$@"
}

as_user_shell() {
  local target_user="$1"; shift
  runuser -u "$target_user" -- bash -c "$*"
}

require_debian_12() {
  [[ -r /etc/os-release ]] || { warn "/etc/os-release fehlt – fahre trotzdem fort."; return; }
  # shellcheck disable=SC1091
  . /etc/os-release
  if [[ "${ID:-}" != "debian" ]]; then
    warn "Erkannt: ${PRETTY_NAME:-unbekannt}. Skript ist auf Debian 12 ausgelegt."
  elif [[ "${VERSION_ID:-}" != "12" ]]; then
    warn "Erkannt: ${PRETTY_NAME:-unbekannt}. Ziel ist Debian 12 – fahre trotzdem fort."
  fi
}

require_internet() {
  log "Internetverbindung pruefen (deb.debian.org muss aufloesbar sein)"
  if ! getent hosts deb.debian.org >/dev/null 2>&1; then
    die "deb.debian.org ist nicht aufloesbar. DNS/Netzwerk pruefen."
  fi
  log "Internet: OK"
}

random_password() {
  # head schließt die Pipe nach 32 Bytes, tr erhält SIGPIPE. Mit
  # `set -o pipefail` würde das den gesamten Lauf stillschweigend abbrechen –
  # daher pipefail lokal im Subshell deaktivieren.
  (set +o pipefail; LC_ALL=C tr -dc 'A-Za-z0-9' < /dev/urandom | head -c 32)
}

prompt_secrets() {
  if [[ -z "$ADMIN_PASSWORD" ]]; then
    printf '\n'
    printf 'Der Admin-User wird fuer den Login in die Web-UI benutzt.\n'
    printf 'Hinweis: Die Eingabe ist unsichtbar (keine Sternchen). Bestaetigen mit Enter.\n\n'
    while true; do
      read -rsp "Passwort fuer Admin-User '${ADMIN_USERNAME}' (min. 6 Zeichen): " ADMIN_PASSWORD
      printf '\n'
      if [[ ${#ADMIN_PASSWORD} -lt 6 ]]; then
        warn "Passwort zu kurz. Bitte erneut eingeben."
        continue
      fi
      read -rsp "Passwort wiederholen: " ADMIN_PASSWORD_CONFIRM
      printf '\n'
      if [[ "$ADMIN_PASSWORD" != "$ADMIN_PASSWORD_CONFIRM" ]]; then
        warn "Passwoerter stimmen nicht ueberein. Bitte erneut eingeben."
        continue
      fi
      break
    done
    unset ADMIN_PASSWORD_CONFIRM
  fi
  if [[ -z "$DB_PASSWORD" ]]; then
    DB_PASSWORD="$(random_password)"
    log "DB-Passwort generiert (wird in $APP_DIR/.env gespeichert)."
  fi
}

install_packages() {
  log "apt: Paketlisten aktualisieren"
  export DEBIAN_FRONTEND=noninteractive
  apt-get update -qq

  if $UPGRADE_SYSTEM; then
    log "apt: System aktualisieren (--upgrade-system)"
    apt-get upgrade -y -qq
  fi

  log "apt: Pakete installieren"
  # Alles, was der Prototyp braucht – bewusst ohne Fremdquellen.
  # Jedes Paket ist begründet:
  #   ca-certificates, curl   – TLS-Roots für pip/PyPI, curl zur Diagnose
  #   gnupg, lsb-release      – Standardwerkzeuge, zukünftige Repo-Keys
  #   locales, tzdata         – UTF-8 und Zeitzonen (Cloud-Images haben das
  #                             oft nicht, ohne scheitern Logs/Datums-Formate)
  #   rsync                   – wird in deploy_code() zum Kopieren benutzt
  #   git                     – falls der User das Repo mit git pull aktualisiert
  #   build-essential         – C-Toolchain für pip-Wheels als Fallback
  #   python3, -venv, -dev    – Python-Runtime und venv-Support
  #   libpq-dev, libffi-dev,  – Header für psycopg, argon2-cffi, cryptography,
  #   libssl-dev                falls kein Binärwheel verfügbar ist
  #   postgresql, -contrib    – Datenbank + Extensions (pgcrypto)
  #   systemd-resolved        – DNS-Resolver, Config via configure_dns()
  #   nginx                   – Reverse-Proxy (optional via --no-nginx)
  local pkgs=(
    ca-certificates curl gnupg lsb-release
    locales tzdata
    rsync git build-essential
    python3 python3-venv python3-dev
    libpq-dev libffi-dev libssl-dev
    postgresql postgresql-contrib
    systemd-resolved
  )
  if $WITH_NGINX; then pkgs+=(nginx); fi
  apt-get install -y --no-install-recommends "${pkgs[@]}"

  # UTF-8-Locale sicherstellen (Cloud-Images laufen gern nur mit POSIX).
  if ! locale -a 2>/dev/null | grep -qiE '^(C\.utf-?8|en_US\.utf-?8)$'; then
    log "Locale: C.UTF-8 erzeugen"
    sed -i -E 's/^# *(C\.UTF-8)/\1/' /etc/locale.gen 2>/dev/null || true
    echo "C.UTF-8 UTF-8" >> /etc/locale.gen
    locale-gen >/dev/null
  fi
}

configure_dns() {
  log "DNS: feste Resolver 1.1.1.1 und 8.8.8.8 konfigurieren (persistent)"

  # Drop-in statt Haupt-Config, damit Paket-Updates die Einstellung nicht
  # überschreiben. Gilt systemweit, greift beim Boot über systemd-resolved.
  install -d -m 0755 /etc/systemd/resolved.conf.d
  cat > /etc/systemd/resolved.conf.d/preisopt-dns.conf <<'EOF'
# Gesetzt durch Preisopt install.sh. Nicht per Hand editieren;
# wird bei erneutem install.sh-Lauf überschrieben.
[Resolve]
DNS=1.1.1.1 8.8.8.8
FallbackDNS=
DNSStubListener=yes
EOF

  systemctl enable systemd-resolved >/dev/null 2>&1 || true
  systemctl restart systemd-resolved

  # /etc/resolv.conf auf den Stub-Resolver zeigen lassen. DHCP-Clients
  # schreiben dann nicht mehr hinein, weil es ein Symlink ist.
  local stub=/run/systemd/resolve/stub-resolv.conf
  if [[ "$(readlink -f /etc/resolv.conf 2>/dev/null)" != "$stub" ]]; then
    if [[ -e /etc/resolv.conf && ! -L /etc/resolv.conf ]]; then
      mv /etc/resolv.conf /etc/resolv.conf.preisopt-backup
    fi
    ln -sf "$stub" /etc/resolv.conf
  fi

  # Smoke-Test, damit Fehler früh sichtbar werden.
  for _ in $(seq 1 10); do
    if getent hosts deb.debian.org >/dev/null 2>&1; then
      log "DNS: aktive Resolver: $(resolvectl dns 2>/dev/null | awk 'NR==1 {print $0}')"
      return
    fi
    sleep 1
  done
  warn "DNS scheint nach Konfiguration nicht aufzulösen. Prüfen: resolvectl status"
}

wait_for_postgres() {
  log "Warte auf PostgreSQL-Cluster"
  for _ in $(seq 1 30); do
    if as_user postgres psql -tAc 'SELECT 1' >/dev/null 2>&1; then
      return
    fi
    sleep 1
  done
  die "PostgreSQL wurde nicht innerhalb 30 Sekunden erreichbar."
}

ensure_app_user() {
  if ! id -u "$APP_USER" >/dev/null 2>&1; then
    log "System-Benutzer '$APP_USER' anlegen"
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
  log "PostgreSQL: Dienst starten"
  systemctl enable --now postgresql >/dev/null 2>&1 || true
  wait_for_postgres

  log "PostgreSQL: Benutzer und Datenbank einrichten"
  local user_exists
  user_exists=$(as_user postgres psql -tAc "SELECT 1 FROM pg_roles WHERE rolname='$DB_USER'")
  if [[ "$user_exists" == "1" ]]; then
    as_user postgres psql -c "ALTER USER $DB_USER WITH ENCRYPTED PASSWORD '$DB_PASSWORD';" >/dev/null
  else
    as_user postgres psql -c "CREATE USER $DB_USER WITH ENCRYPTED PASSWORD '$DB_PASSWORD';" >/dev/null
  fi

  local db_exists
  db_exists=$(as_user postgres psql -tAc "SELECT 1 FROM pg_database WHERE datname='$DB_NAME'")
  if [[ "$db_exists" != "1" ]]; then
    as_user postgres createdb -O "$DB_USER" "$DB_NAME"
  fi

  as_user postgres psql -d "$DB_NAME" -c 'CREATE EXTENSION IF NOT EXISTS "pgcrypto";' >/dev/null
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
# client_encoding erzwingt UTF-8 auf dem Verbindungs-Kanal. Ohne das gibt
# psycopg bei Clustern mit SQL_ASCII-Encoding bytes statt str zurück, und
# SQLAlchemy scheitert beim Parsen der Server-Version mit einem TypeError.
DATABASE_URL=postgresql+psycopg://${DB_USER}:${DB_PASSWORD}@127.0.0.1:5432/${DB_NAME}?client_encoding=utf8
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
  as_user "$APP_USER" "$PY_BIN" -m venv "$APP_DIR/.venv"
  as_user "$APP_USER" "$APP_DIR/.venv/bin/pip" install --quiet --upgrade pip wheel
  as_user "$APP_USER" "$APP_DIR/.venv/bin/pip" install --quiet -r "$APP_DIR/backend/requirements.txt"
}

run_migrations() {
  log "Alembic: Migrationen anwenden"
  as_user_shell "$APP_USER" \
    "cd '$APP_DIR/backend' && set -a && source '$APP_DIR/.env' && set +a && '$APP_DIR/.venv/bin/alembic' upgrade head"
}

run_seed() {
  if $SKIP_SEED; then
    log "Seed übersprungen (--skip-seed)"
    return
  fi
  log "Seed: Admin-User und Mock-Produkte"
  as_user_shell "$APP_USER" \
    "cd '$APP_DIR/backend' && set -a && source '$APP_DIR/.env' && set +a && '$APP_DIR/.venv/bin/python' -m seed --username '$ADMIN_USERNAME' --password '$ADMIN_PASSWORD'"
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

smoke_test() {
  log "Smoke-Test: Health-Endpoint"
  local target
  if $WITH_NGINX; then
    target="http://127.0.0.1/api/v1/health"
  else
    target="http://127.0.0.1:8000/api/v1/health"
  fi
  # systemd-Start ist asynchron, kurzer Retry.
  for _ in $(seq 1 20); do
    if curl -fsS "$target" >/dev/null 2>&1; then
      log "Health-Endpoint antwortet: $target"
      return
    fi
    sleep 1
  done
  warn "Health-Endpoint $target antwortet nicht. Prüfen: journalctl -u preisopt-backend -n 50"
}

summary() {
  local port
  if $WITH_NGINX; then port=80; else port=8000; fi
  log "Fertig."
  printf '  URL:         http://<server-ip>:%s/\n' "$port"
  printf '  Admin-User:  %s\n' "$ADMIN_USERNAME"
  printf '  .env:        %s/.env\n' "$APP_DIR"
  printf '  Service:     systemctl status preisopt-backend\n'
  printf '  Logs:        journalctl -u preisopt-backend -f\n'
  if [[ -z "$GEMINI_API_KEY" ]]; then
    warn "GEMINI_API_KEY ist leer — LLM-Strategie schlägt fehl, bis er in $APP_DIR/.env gesetzt ist."
  fi
}

banner() {
  printf '\n'
  printf '\033[1;36m==============================================================\033[0m\n'
  printf '\033[1;36m  Preisoptimierung - Debian 12 Installer\033[0m\n'
  printf '\033[1;36m==============================================================\033[0m\n'
  printf '  Zielverzeichnis: %s\n' "$APP_DIR"
  printf '  Reverse-Proxy:   %s\n' "$( $WITH_NGINX && echo 'nginx (Port 80)' || echo 'aus (uvicorn :8000 direkt)' )"
  printf '  Seed-Daten:      %s\n' "$( $SKIP_SEED && echo 'uebersprungen' || echo 'Admin + Mock-Produkte' )"
  printf '\n'
}

main() {
  banner
  require_debian_12
  prompt_secrets
  require_internet
  install_packages
  configure_dns
  ensure_app_user
  deploy_code
  setup_postgres
  write_env_file
  setup_venv
  run_migrations
  run_seed
  install_systemd
  install_nginx
  smoke_test
  summary
}

main "$@"
