# **Testkonzept**

Dieses Dokument beschreibt, wie die Qualität des Prototyps im Modul *Projekt Anwendungsentwicklung* sichergestellt wird. Fokus: pragmatische Kombination aus automatisierten Tests im Backend und manuellen User-Tests mit externen Personen.

## **1\. Testziele**

* **Funktionale Korrektheit:** die primären Use Cases (siehe [`use-cases.md`](https://claude.ai/chat/use-cases.md)) laufen erwartungsgemäß durch.  
* **Usability:** ein Nutzer ohne Vorerfahrung kann den Hauptflow (Produkt anlegen → Strategie setzen → Preis berechnen) selbständig durchlaufen.  
* **Robustheit gegenüber LLM-Ausfällen:** Fix- und Formel-Strategien arbeiten unabhängig vom LLM weiter.

Keine Leistungs- oder Lasttests, keine Sicherheitsaudits – der Scope ist ein akademischer Prototyp.

## **2\. Testebenen**

### **Manuelle Smoke-Tests**

Nach jedem größeren Merge und vor der Abschluss-Demo: vollständiger Durchlauf der primären Use Cases in der Live-Demo-Umgebung ([fom.ollornog.de](https://fom.ollornog.de/)). Checkliste in der Test-Matrix, Durchführung durch Person B.

### **Externe User-Tests**

Zwei bis drei Personen außerhalb des Teams bedienen die Anwendung ohne Erklärung. Beobachtung mit Screen-Recording oder Notizen. Ziel: Usability-Probleme entdecken, die uns im Team wegen Betriebsblindheit nicht auffallen. Findings landen in [`bug-log.md`](https://claude.ai/chat/bug-log.md).

## **3\. Testumgebung**

| Umgebung | Zweck | Daten |
| ----- | ----- | ----- |
| Lokal | Unabhängiger Test von Daniel | leere Test-DB, pro Test frisch |
| Live-Demo ([fom.ollornog.de](https://fom.ollornog.de/)) | Manuelle Smoke-Tests, externe User-Tests | Seed-Daten aus `backend/app/mock_data.py` |

Für die externen User-Tests wird vor jeder Session die DB über *Einstellungen → Datenbank zurücksetzen* (UC-16) auf den Seed-Stand gebracht, damit die Tester reproduzierbare Startbedingungen haben.

## 

## **4\. Was wird getestet – was nicht**

### **Getestet**

* Alle zehn primären Use Cases ([`use-cases.md`](https://claude.ai/chat/use-cases.md) UC-1 bis UC-10)  
* Der Formel-Evaluator mit besonderem Blick auf Security-Angriffsvektoren  
* Session-Auth-Flow und Ownership-Grenzen  
* Rollentrennung: Team-Benutzer darf keine Admin-Einstellungen sehen oder ändern

### **Nicht getestet (bewusst)**

* Die sekundären Admin-Use-Cases (UC-11 bis UC-16) – manuell einmal durchgespielt, aber keine Testfälle in der Matrix  
* Performance/Last – kein produktiver Einsatz  
* Browser-Kompatibilität jenseits Chrome/Firefox/Safari in aktueller Version  
* Mobile Ansicht (Pico.css bringt Basis-Responsiveness, gezielte Mobile-Optimierung ist out-of-scope)  
* `install.sh` auf anderen Distributionen als Debian 12 – ADR-dokumentiert

## **5\. Abnahmekriterien**

Der Prototyp gilt als abnahmefähig für die Abgabe am 14.07.2026, wenn:

1. **Test-Matrix:** mindestens 20 Testfälle, davon 100 % mit Status *Passed* oder *Wontfix* (mit Begründung).  
2. **Bug-Log:** kein Bug mit Priorität *kritisch* oder *hoch* im Status *Offen*.  
3. **User-Tests:** zwei externe User-Tests durchgeführt, Findings dokumentiert, kritische Usability-Probleme behoben.  
4. **Smoke-Test live:** kompletter Demo-Pfad auf [fom.ollornog.de](https://fom.ollornog.de/) wird vollständig durchlaufen, ohne manuelles Eingreifen in Datenbank oder Logs.

## **8\. Nicht genutzt**

* **GitHub-Issues als Bug-Tracker** – bewusste Entscheidung; Findings kommen direkt in [`bug-log.md`](https://claude.ai/chat/bug-log.md) mit Commit. Begründung siehe [`../team-aufgaben.md`](https://claude.ai/team-aufgaben.md).  
* **End-to-End-Tests im Browser (Playwright/Selenium)** – Aufwand für einen 6-Wochen-Prototyp nicht gerechtfertigt; wird durch manuelle Smoke-Tests ersetzt.  
* **Testabdeckungs-Report (Coverage)** – nicht Prüfungskriterium; Unit-Tests decken die sicherheitskritischen Pfade gezielt ab.
