# Informationssicherheit

Wir orientieren uns an **Art. 32 DSGVO (Technische und organisatorische Maßnahmen)** und setzen im Prototyp die wesentlichen Punkte um. Die Tabelle zeigt, was im Produktivbetrieb zusätzlich zu erwarten wäre.

| Thema | Prototyp | Produktiv-Ausblick |
| --- | --- | --- |
| Authentifizierung | Login für Admin-UI, Passwörter mit bcrypt/argon2 gehasht | MFA, Passwort-Policy, Brute-Force-Schutz |
| Transportverschlüsselung | Lokal HTTP | HTTPS-only, HSTS, aktuelle TLS-Version |
| Input-Validierung | Pydantic-Schemas im FastAPI-Backend | + Rate-Limiting, WAF, strukturelle Output-Validierung |
| Secrets-Management | `.env` + `.gitignore`, `.env.example` als Vorlage | Secrets-Manager (z. B. Vault, AWS SM), Rotation |
| Audit-Log | Preishistorie als append-only Tabelle | Zentrales, manipulationssicheres Log, Retention-Policy |
| Backup | Manueller DB-Dump (z. B. `pg_dump`) | Automatisiert, verschlüsselt, Restore regelmäßig getestet |
| Rollen/Berechtigungen | Admin + Read-only | Feingranulares RBAC, Review-Prozess |
| Privacy by Design | Umgesetzt durch Leitprinzipien 1, 2, 5 | Datenschutz-Folgenabschätzung, AVV, Löschkonzept |
| LLM-Datenminimierung | Whitelist-Felder aus Produktdaten, keine Kundendaten | AVV mit Anbieter, EU-Hosting, Opt-out für Trainingsnutzung |

## Zusätzliche Praxis im Prototyp
- Keys und Credentials werden nicht geloggt.
- Fehlermeldungen geben keine internen Details nach außen.
- Jede Preisberechnung erzeugt genau einen Historien-Eintrag (Nachvollziehbarkeit).
