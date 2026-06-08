```mermaid
graph TD
    %% Definição dos Nós de Origem
    subgraph SUAP ["Sistema de Gestão Institucional"]
        A["SUAP"] --> B1["digitais.xls"]
        A --> B2["emitidos_2026.xls"]
    end

    %% Definição do Cliente/Frontend
    subgraph Frontend ["Camada Cliente (Vercel)"]
        C["Interface React"]
        B1 --> C
        B2 --> C
    end

    %% Definição do Servidor/Backend
    subgraph Backend ["Camada Servidor (Render)"]
        D["API FastAPI"]
        E["processador.py"]
        F["gerador_relatorios.py"]
        
        C -->|POST /api/processar-diplomas| D
        D --> E
        E --> F
        F --> D
        D -->|Resposta JSON| C
    end

    %% Definição das Saídas e Destinos
    subgraph Destinos ["Destinos de Publicação"]
        G["Aviso_de_Registro_de_Diplomas.rtf"]
        H["Listagem_Publicacao_Diplomas.xlsx"]
        
        C -.->|Download local| G
        C -.->|Download local| H
        
        G --> I["Imprensa Nacional (INCOM)"]
        H --> J["Site Institucional (Portaria 1.095 MEC)"]
    end

    %% Estilização Básica
    style A fill:#f9f,stroke:#333,stroke-width:2px
    style C fill:#bbf,stroke:#333,stroke-width:2px
    style D fill:#bfb,stroke:#333,stroke-width:2px
    style I fill:#fbb,stroke:#333,stroke-width:2px
    style J fill:#fbb,stroke:#333,stroke-width:2px

    %% Estilização Básica
    style A fill:#f9f,stroke:#333,stroke-width:2px
    style C fill:#bbf,stroke:#333,stroke-width:2px
    style D fill:#bfb,stroke:#333,stroke-width:2px
    style I fill:#fbb,stroke:#333,stroke-width:2px
    style J fill:#fbb,stroke:#333,stroke-width:2px
