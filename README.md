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

``` mermaid
---

## 🚀 Sobre o Projeto: Automatiza-Publicação

O **Automatiza-Publicação** é uma solução de software desenvolvida para otimizar, cruzar e validar de forma automática os dados necessários para a publicação de registros de diplomas. O sistema garante conformidade estrita com o **art. 21 da Portaria MEC nº 1.095 de 25 de outubro de 2018**.

Ele elimina o trabalho manual e suscetível a erros de conferência de planilhas e formatação de textos legais, gerando os documentos finais prontos para publicação em poucos segundos com validação visual em tempo real (WYSIWYG).

---

## 🛠️ Fluxo Operacional (Passo a Passo)

### 1. Extração de Dados (Origem)
* O usuário acessa o **SUAP** (Sistema Unificado de Administração Pública).
* Realiza a extração de duas planilhas em formato `.xls`:
  * `digitais.xls`: Contém as informações base dos diplomas acadêmicos.
  * `emitidos_2026.xls`: Contém os dados de registro detalhados dos diplomas já emitidos.
* Esses arquivos são mantidos na máquina local do usuário para upload.

### 2. Processamento e Regras de Negócio (Backend)
Assim que os arquivos são submetidos na interface React, a API em FastAPI aciona o script `processador.py`, que executa as seguintes operações em memória:
* **Limpeza de Dados:** Elimina colunas desnecessárias do arquivo original (*“Codigo curso”*, *“Campus”*, *“Processo”*, *“Etapa atual”* e *“Situacao”*).
* **Relacionamento Lógico:** Cruza e mescla os dados de ambas as planilhas utilizando a coluna **Matrícula** (chave primária comum e sem repetições) como elo de ligação.
* **Enriquecimento:** Injeta na tabela final as colunas trazidas do arquivo de emitidos (*“CPF”*, *“e-MEC”*, *“Ingresso”* e *“Conclusão”*) em suas posições regulamentares.
* **Agrupamento Estatístico:** Agrupa os registros por **Livro de Homologação** e calcula automaticamente o subtotal de registros por livro e o intervalo exato (primeiro e último número de registro).

### 3. Entregáveis e Destino Legal (Saídas)
Após a validação da prévia formatada em tela, o usuário realiza o download dos ativos finais:
* **Aviso_de_Registro_de_Diplomas.rtf:** Documento oficial contendo o texto formatado dos livros e intervalos calculados. Destinado ao upload manual no sistema **INCOM da Imprensa Nacional** para publicação no Diário Oficial da União.
* **Listagem_Publicacao_Diplomas.xlsx:** Planilha consolidada com todas as células tratadas como texto puro (evitando quebras de hífens ou códigos e-MEC) e ordenada alfabeticamente por aluno. Destinada à publicação regulamentar no site da instituição.

---

## 💻 Arquitetura Tecnológica
* **Frontend:** React (Hospedado na Vercel)
* **Backend:** Python / FastAPI (Hospedado no Render)
* **Manipulação de Dados:** Pandas / Openpyxl
