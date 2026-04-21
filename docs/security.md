# Informationssicherheit

Orientierung an Art. 32 DSGVO. Die Tabelle listet die umgesetzten
Maßnahmen im Prototyp und den produktiven Ausblick – Legende:
**✅** umgesetzt, **🔶** vorhanden, aber für Produktivbetrieb
auszubauen, **📝** bewusst nicht Teil des Prototyps.

| Bereich | Maßnahme Prototyp | Maßnahme Produktiv | Status |
| --- | --- | --- | --- |
| Authentifizierung | Login, argon2id-Hash, Passwort-Änderung prüft altes Passwort | MFA, Passwort-Policy, Brute-Force-Lockout | 🔶 |
| Session-Management | Starlette-`SessionMiddleware`, signiertes Cookie, `HttpOnly`, `SameSite=Lax`, 8 h TTL | zusätzlich `Secure`, Session-Rotation bei Login | 🔶 |
| HTTPS/TLS | nginx Port 80; HTTPS per UI-Klick via `certbot --nginx` (Let's Encrypt) | HSTS, TLS-1.3-only, Monitoring der Zertifikats-Erneuerung | 🔶 |
| Rate Limiting | pro User pro Tag: 50 Standard / 200 Admin, einstellbar in UI (Tabelle `api_rate_usage`) | verteiltes Limit (Redis/nginx-limit-req), Burst, Anomalie-Alerting | ✅ |
| Input-Validierung | Pydantic-Schemas, AST-basierter Formel-Evaluator ohne `eval`, Regex-Gate im Frontend | WAF, Fuzzing, strukturelle Output-Validierung | ✅ |
| SQL-Injection | ausschließlich parametrisierte Queries über SQLAlchemy ORM | dto. + statisches SAST | ✅ |
| XSS | Alpine.js `x-text` / `x-html` nur mit kontrollierten Werten; Prompt-/Reasoning-Textareas `readonly`; kein `innerHTML` auf User-Eingaben | strenge CSP-Header | ✅ |
| CSRF | `SameSite=Lax` + Single-Origin-Deployment (Frontend über Backend ausgeliefert) | zusätzlich CSRF-Token für mutierende Endpoints | ✅ |
| Passwort-Hashing | argon2id (`argon2-cffi`) | dto. + Passwort-Rotation + Pwned-Checks | ✅ |
| Secrets-Management | `.env` (mode 640, Owner `preisopt`) + DB-Override `app_settings` | Secrets-Manager (Vault/SM), Rotation, Audit-Log der Zugriffe | 🔶 |
| Logging | uvicorn- + systemd-Logs, Preis-Historie als fachliches Audit | zentrales SIEM, manipulationssicher, Retention-Policy | 🔶 |
| Backups | manueller `pg_dump` | automatisiert, verschlüsselt, regelmäßig Restore-Drill | 📝 |
| Reverse-Proxy | nginx, `proxy_intercept_errors`, Cookie-Invalidierung bei 5xx, strikte Domain-Validierung im HTTPS-Helper | zusätzlich mTLS zu Upstream, Rate Limiting auf Edge | ✅ |
| Privilegienerhöhung | genau **ein** sudoers-Eintrag (`/etc/sudoers.d/preisopt`) für das HTTPS-Helper-Skript, Pfad fest verdrahtet | AppArmor-/SELinux-Profil, Audit der sudo-Aufrufe | ✅ |
| DB-Zugriff | ausschließlich durch Backend-Prozess (`preisopt`-User, Unix-Socket/Local-TCP) | Netzwerksegmentierung, Least-Privilege-Rollen pro Service | ✅ |
| Admin-Guards | `get_current_admin` schützt `/users`, `/settings/https*`, `/settings/rate-limit*` | feingranulares RBAC, Review-Prozess | ✅ |
| LLM-Datenminimierung | Whitelist-Funktion, Prompt vor Versand in UI sichtbar | AVV mit LLM-Anbieter, EU-Hosting, vertragl. Ausschluss Trainingsnutzung | ✅ |

Detail siehe [`decisions/0003-auth-session-cookie.md`](./decisions/0003-auth-session-cookie.md)
und [`decisions/0005-deployment-debian.md`](./decisions/0005-deployment-debian.md).
