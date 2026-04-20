# Informationssicherheit

Orientierung an **Art. 32 DSGVO (Technische und organisatorische Maßnahmen)**.
Die Tabelle zeigt, was im Prototyp umgesetzt ist und welche Ergänzungen im
Produktivbetrieb nötig wären.

| Thema | Prototyp | Produktiv-Ausblick |
| --- | --- | --- |
| Authentifizierung | Login pro Konto, Passwörter per **argon2id** gehasht; Passwort-Änderung prüft das alte Passwort | MFA, Passwort-Policy, Brute-Force-Schutz (Lockout, Captcha) |
| Transportverschlüsselung | nginx auf Port 80; **HTTPS per Klick** in den Einstellungen (certbot-nginx, Let's Encrypt) | HSTS-Header, automatische Zertifikats-Erneuerung überwacht, TLS 1.3 erzwingen |
| Session | signiertes HttpOnly-Cookie (`SameSite=Lax`), 8 h Laufzeit; nginx invalidiert das Cookie bei 5xx automatisch | zusätzlicher `Secure`-Flag bei HTTPS, Session-Rotation nach Login, Absolute- und Idle-Timeout getrennt |
| Input-Validierung | Pydantic-Schemas pro Endpoint; AST-basierter Formel-Evaluator ohne `eval()`; Regex-Gate im Frontend-Evaluator | WAF, strukturelle Output-Validierung, Fuzzing der öffentlichen Endpoints |
| Rate Limiting | pro Benutzer pro Tag, Standard 50, Admin 200 (beides per UI einstellbar); Overschreitung → HTTP 429 | verteiltes Rate Limit (Redis/NGINX-limit-req), Burst-Limits, Anomalie-Erkennung |
| Berechtigung | `admin` vs. `viewer` (DB-Schema); kritische Bereiche (User-CRUD, HTTPS, Rate Limit) sind admin-only geschützt | feingranulares RBAC, Review-Prozess für Privilegien-Änderungen |
| Audit-Log | `price_history` als append-only Tabelle inkl. Benutzer, Strategie, KI-Flag und Begründung | zentrales, manipulationssicheres Log, Retention-Policy, Log-Shipping |
| Secrets-Management | `.env` + `.gitignore`, `.env.example` als Vorlage; zusätzlich DB-Override (`app_settings`) für den Gemini-Key (wird nie an den Client zurückgespielt) | Secrets-Manager (Vault, AWS SM o. ä.), Key-Rotation, Audit pro Zugriff |
| Backup | Manueller DB-Dump (`pg_dump`) | Automatisiert, verschlüsselt, Restore regelmäßig getestet |
| Privileged-Operations | HTTPS-Helper läuft als root **ausschließlich** über einen genau definierten sudoers-Eintrag (`/etc/sudoers.d/preisopt`, ein Binary) | zusätzlich Mandatory Access Control (AppArmor/SELinux-Profil), vollständiger Audit-Trail der sudo-Aufrufe |
| Privacy by Design | Umgesetzt über Leitprinzipien 1, 2, 5; Mock-Daten, Human-in-the-Loop, keine Kundendaten im LLM-Prompt | Datenschutz-Folgenabschätzung, AVV mit dem LLM-Anbieter, Löschkonzept |
| LLM-Datenminimierung | Whitelist-Funktion, die nur produktbezogene Felder liefert; Prompt ist vor dem Versenden in der UI sichtbar (Transparenz) | AVV mit dem Anbieter, EU-Hosting, vertraglich ausgeschlossene Trainingsnutzung |

## Zusätzliche Praxis im Prototyp
- Keys und Credentials werden nicht geloggt.
- Fehlermeldungen sind generisch; interne Details bleiben im Server-Log.
- Jede Preisberechnung erzeugt genau einen Historien-Eintrag (Audit).
- Strategie-Wechsel schreiben automatisch einen Snapshot in die Historie.
- Der bootstrap-Account `admin` ist serverseitig gegen Passwort-/Rollen-
  Änderungen und Löschen geschützt (HTTP 403).

## Transport: HTTPS optional per Klick

Die Anwendung kann wahlweise über HTTP oder HTTPS laufen:

- **Default nach Installation:** nginx auf Port 80. Die `SessionMiddleware`
  setzt das Cookie ohne `Secure`-Flag, sodass der Login auch ohne TLS
  funktioniert.
- **HTTPS aktivieren:** Einstellungen → *HTTPS (Let's Encrypt)* → Domain
  eintragen. Das Backend ruft über `sudo` ein privilegiertes Helper-Skript,
  das den `server_name` der nginx-Site setzt und `certbot --nginx` das
  Zertifikat ausstellen lässt (inklusive HTTP→HTTPS-Redirect).
- Der Helper ist der einzige Befehl, den der Backend-User als root ausführen
  darf (sudoers-Regel unter `/etc/sudoers.d/preisopt`, Pfad fest verdrahtet).
- HSTS wird bewusst **nicht** gesetzt, damit ein testweises Zurückrollen
  auf HTTP ohne Browser-Cache-Streit möglich bleibt – im Produktiv-Betrieb
  zwingend nachzuziehen.

Für einen Produktiveinsatz wären HTTPS + HSTS + automatisches Monitoring der
Zertifikats-Erneuerung verpflichtend. Siehe die rechte Spalte der Tabelle oben.
