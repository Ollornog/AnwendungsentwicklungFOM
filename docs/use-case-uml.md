mermaid
flowchart LR
  User((Shop-Betreiberin))
  Admin((Admin))
  LLM((Gemini API))

  subgraph System[Preisoptimierungs-Tool]
    direction TB

    subgraph Auth[Zugang]
      UC0([UC-0 Einloggen])
    end

    subgraph Kern[Produkt- und Preisverwaltung]
      UC1([UC-1 Produkt anlegen])
      UC2([UC-2 Strategie zuweisen])
      UC3([UC-3 Preis berechnen])
      UC4([UC-4 KI-Vorschlag einholen])
      UC5([UC-5 Wettbewerbspreise recherchieren])
      UC6([UC-6 Simulator nutzen])
      UC7([UC-7 Preisgraph oeffnen])
      UC8([UC-8 Historie einsehen])
    end

    subgraph AdminArea[Admin-Bereich]
      UC9([UC-9 Team-Accounts verwalten])
      UC10([UC-10 System konfigurieren])
    end
  end

  User --> UC0
  User --> UC1
  User --> UC2
  User --> UC5
  User --> UC6
  User --> UC7
  User --> UC8

  Admin -.->|erbt von| User
  Admin --> UC9
  Admin --> UC10

  UC2 -.->|include| UC3
  UC4 -.->|extend| UC2

  UC4 --> LLM
  UC5 --> LLM

  classDef actor fill:#e1f5ff,stroke:#01579b,stroke-width:2px
  classDef usecase fill:#fff4e6,stroke:#e65100,stroke-width:1px
  classDef external fill:#f3e5f5,stroke:#4a148c,stroke-width:2px,stroke-dasharray: 5 5

  class User,Admin actor
  class LLM external
  class UC0,UC1,UC2,UC3,UC4,UC5,UC6,UC7,UC8,UC9,UC10 usecase
