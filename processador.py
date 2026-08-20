import pandas as pd
import re
import unicodedata

def normalizar_nome_coluna(coluna):
    if not isinstance(coluna, str):
        return str(coluna)
    coluna = coluna.strip()
    coluna = "".join(c for c in unicodedata.normalize('NFD', coluna) if unicodedata.category(c) != 'Mn')
    return coluna.lower()

def limpar_e_mascarar_cpf(cpf_sujo):
    if pd.isna(cpf_sujo) or str(cpf_sujo).strip() in ['', '-', 'nan', 'NaN', 'None']:
        return "-"
    numeros = re.sub(r'\D', '', str(cpf_sujo))
    if len(numeros) == 11:
        return f"***.{numeros[3:6]}.{numeros[6:9]}-**"
    return str(cpf_sujo)

def higienizar_matricula_digito(valor):
    if pd.isna(valor):
        return ""
    texto = str(valor).strip()
    texto = re.sub(r'\.0$', '', texto)
    texto = re.sub(r'\s+', '', texto)
    return texto

def encontrar_coluna_por_multiplas_palavras(lista_colunas, palavras_chave, coluna_padrao):
    for palavra in palavras_chave:
        encontradas = [c for c in lista_colunas if palavra in c]
        if encontradas:
            return encontradas[0]
    return coluna_padrao

def processar_diplomas(caminho_digitais, caminho_emitidos):
    # 1. Leitura forçando tudo como string/texto desde a origem
    df_digitais = pd.read_excel(caminho_digitais, dtype=str)
    df_emitidos = pd.read_excel(caminho_emitidos, dtype=str)
    
    # Padroniza os cabeçalhos das colunas
    df_digitais.columns = [normalizar_nome_coluna(col) for col in df_digitais.columns]
    df_emitidos.columns = [normalizar_nome_coluna(col) for col in df_emitidos.columns]
    
    # Limpa as strings numéricas de matrícula
    df_digitais['matricula'] = df_digitais['matricula'].apply(higienizar_matricula_digito)
    df_emitidos['matricula'] = df_emitidos['matricula'].apply(higienizar_matricula_digito)
    
    df_digitais = df_digitais[df_digitais['matricula'] != ""]
    df_emitidos = df_emitidos[df_emitidos['matricula'] != ""]
    
    # Proteção para o merge
    df_emitidos = df_emitidos.drop_duplicates(subset=['matricula'])
    
    # Mapeamento e busca dinâmica de colunas
    col_homolog_real = encontrar_coluna_por_multiplas_palavras(df_digitais.columns, ['homol', 'data da homologacao'], 'homologacao')
    col_aluno_digitais = encontrar_coluna_por_multiplas_palavras(df_digitais.columns, ['aluno', 'nome'], 'aluno')
    col_cpf_digitais = encontrar_coluna_por_multiplas_palavras(df_digitais.columns, ['cpf'], 'cpf')
    
    col_emec_real = encontrar_coluna_por_multiplas_palavras(df_emitidos.columns, ['mec', 'emec'], 'e-mec')
    col_ingresso_real = encontrar_coluna_por_multiplas_palavras(df_emitidos.columns, ['ingr', 'ingresso'], 'ingresso')
    col_conclusao_real = encontrar_coluna_por_multiplas_palavras(df_emitidos.columns, ['concl', 'conclusao'], 'conclusao')
    col_folha_real = encontrar_coluna_por_multiplas_palavras(df_emitidos.columns, ['folh', 'folha'], 'folha')
    col_cpf_emitidos = encontrar_coluna_por_multiplas_palavras(df_emitidos.columns, ['cpf'], 'cpf')
    
    colunas_para_trazer = ['matricula', col_emec_real, col_ingresso_real, col_conclusao_real, col_folha_real, col_cpf_emitidos]
    colunas_para_trazer = list(set(colunas_para_trazer))
    
    df_mesclado = pd.merge(df_digitais, df_emitidos[colunas_para_trazer], on='matricula', how='left', suffixes=('', '_emitidos'))
    
    # Alertas para registros de exercício anterior
    alertas = []
    linhas_sem_emitidos = df_mesclado[df_mesclado[col_emec_real].isna()]
    
    for _, linha in linhas_sem_emitidos.iterrows():
        nome_aluno = str(linha.get(col_aluno_digitais, 'ALUNO DESCONHECIDO')).upper().strip()
        raw_cpf = linha.get(col_cpf_emitidos) if pd.notna(linha.get(col_cpf_emitidos)) else linha.get(col_cpf_digitais)
        cpf_formatado = limpar_e_mascarar_cpf(raw_cpf)
        
        alertas.append({
            "aluno": nome_aluno,
            "cpf": cpf_formatado,
            "mensagem": f"{nome_aluno} - CPF: {cpf_formatado}: Diploma emitido em exercício anterior - Favor verificar"
        })

    # Consolida CPF
    if col_cpf_emitidos in df_mesclado.columns:
        df_mesclado['CPF_FINAL'] = df_mesclado[col_cpf_emitidos].fillna(df_mesclado.get(col_cpf_digitais, '-'))
    else:
        df_mesclado['CPF_FINAL'] = df_mesclado.get(col_cpf_digitais, '-')

    coluna_livro_real = encontrar_coluna_por_multiplas_palavras(df_mesclado.columns, ['livro'], 'livro')
    
    mapeamento_exibicao = {
        col_aluno_digitais: 'Aluno',
        'CPF_FINAL': 'CPF',
        col_emec_real: 'e-MEC',
        'curso': 'Curso',
        col_ingresso_real: 'Ingresso',
        col_conclusao_real: 'Conclusao',
        col_homolog_real: 'Homologacao',
        col_folha_real: 'Folha',
        coluna_livro_real: 'Livro',
        'registro da homologacao': 'Registro da homologação'
    }
    
    df_mesclado = df_mesclado.rename(columns=mapeamento_exibicao)
    
    # Higienização
    for col in [
        'Aluno', 'CPF', 'e-MEC', 'Curso', 'Ingresso', 
        'Conclusao', 'Homologacao', 'Folha', 'Livro', 'Registro da homologação'
    ]:
        if col not in df_mesclado.columns:
            df_mesclado[col] = "-"
        else:
            df_mesclado[col] = df_mesclado[col].fillna("-")
            df_mesclado[col] = df_mesclado[col].replace(['nan', 'NaN', 'None', ''], '-')
            
    df_mesclado['Aluno'] = df_mesclado['Aluno'].astype(str).str.upper().str.strip()
    df_mesclado['Curso'] = df_mesclado['Curso'].astype(str).str.upper().str.strip()
    df_mesclado['CPF'] = df_mesclado['CPF'].apply(limpar_e_mascarar_cpf)
    df_mesclado['Homologacao'] = df_mesclado['Homologacao'].astype(str).str.strip()
    df_mesclado['Folha'] = df_mesclado['Folha'].astype(str).str.strip()
    
    # ORDENAÇÃO SEM CONSIDERAR ACENTUAÇÃO (ÁLADSON entra junto do A)
    df_mesclado['aluno_chave_sort'] = df_mesclado['Aluno'].apply(remover_acentos)
    df_mesclado = df_mesclado.sort_values(by='aluno_chave_sort', ascending=True)
    df_mesclado = df_mesclado.drop(columns=['aluno_chave_sort'])
    
    sequencia_oficial = [
        'Aluno', 'CPF', 'e-MEC', 'Curso', 'Ingresso', 
        'Conclusao', 'Homologacao', 'Folha', 'Livro', 'Registro da homologação'
    ]
    df_final = df_mesclado[sequencia_oficial].copy()
    
    return df_final, alertas