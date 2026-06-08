```mermaid
graph TD
    %% Definição dos Nós de Origem
    subgraph SUAP [Sistema de Gestão Institucional]
        A[SUAP] -->|Exportar| B1[digitais.xls]
        A -->|Exportar| B2[emitidos_2026.xls]
    end

    %% Definição do Cliente/Frontend
    subgraph Frontend [Camada Cliente - Hospedado na Vercel]
        C[Interface React]
        B1 -->|Upload via Browser| C
        B2 -->|Upload via Browser| C
    end

    %% Definição do Servidor/Backend
    subgraph Backend [Camada Servidor - Hospedado no Render]
        D[API FastAPI]
        E[processador.py]
        F[gerador_relatorios.py]
        
        C -->|HTTP POST /api/processar-diplomas| D
        D -->|Envia binários| E
        E -->|Cruza dados via Matrícula| F
        F -->|Gera RTF e HTML Previa| D
        D -->|Retorna Resposta JSON| C
    end

    %% Definição das Saídas e Destinos
    subgraph Destinos [Destinos de Publicação]
        G[Aviso_de_Registro_de_Diplomas.rtf]
        H[Listagem_Publicacao_Diplomas.xlsx]
        
        C -.->|Download local| G
        C -.->|Download local| H
        
        G -->|Upload Manual| I[Imprensa Nacional - INCOM]
        H -->|Publicação Manual| J[Site Institucional - Portaria 1.095 MEC]
    end

    %% Estilização Básica
    style A fill:#f9f,stroke:#333,stroke-width:2px
    style C fill:#bbf,stroke:#333,stroke-width:2px
    style D fill:#bfb,stroke:#333,stroke-width:2px
    style I fill:#fbb,stroke:#333,stroke-width:2px
    style J fill:#fbb,stroke:#333,stroke-width:2px
