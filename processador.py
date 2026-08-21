import pandas as pd
import re
import unicodedata
import io

def normalizar_nome_coluna(coluna):
    if not isinstance(coluna, str):
        return str(coluna)
    coluna = coluna.strip()
    coluna = "".join(c for c in unicodedata.normalize('NFD', coluna) if unicodedata.category(c) != 'Mn')
    return coluna.lower()

def limpar_e_mascarar_cpf(cpf_sujo):
    if pd.isna(cpf_sujo):
        return ""
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

def processar_planilhas(file_digitais_bytes, file_emitidos_bytes):
    alertas = []

    # 1. Leitura forçando tudo como string/texto desde a origem
    df_digitais = pd.read_excel(file_digitais_bytes, dtype=str)
    df_emitidos = pd.read_excel(file_emitidos_bytes, dtype=str)
    
    # Padroniza os cabeçalhos das colunas (letras minúsculas e sem acento)
    df_digitais.columns = [normalizar_nome_coluna(col) for col in df_digitais.columns]
    df_emitidos.columns = [normalizar_nome_coluna(col) for col in df_emitidos.columns]
    
    # Limpa as strings numéricas de matrícula
    if 'matricula' in df_digitais.columns:
        df_digitais['matricula'] = df_digitais['matricula'].apply(higienizar_matricula_digito)
        df_digitais = df_digitais[df_digitais['matricula'] != ""]
    
    if 'matricula' in df_emitidos.columns:
        df_emitidos['matricula'] = df_emitidos['matricula'].apply(higienizar_matricula_digito)
        df_emitidos = df_emitidos[df_emitidos['matricula'] != ""]
    
    # Proteção para o merge não gerar linhas duplicadas
    if 'matricula' in df_emitidos.columns:
        df_emitidos = df_emitidos.drop_duplicates(subset=['matricula'])
    
    # Localiza a Data de Homologação na Planilha de Digitais
    col_homolog_real = encontrar_coluna_por_multiplas_palavras(df_digitais.columns, ['homol', 'data da homologacao'], 'homologacao')
    
    # Localiza as informações chaves na Planilha de Emitidos
    col_emec_real = encontrar_coluna_por_multiplas_palavras(df_emitidos.columns, ['mec', 'emec'], 'e-mec')
    col_ingresso_real = encontrar_coluna_por_multiplas_palavras(df_emitidos.columns, ['ingr', 'ingresso'], 'ingresso')
    col_conclusao_real = encontrar_coluna_por_multiplas_palavras(df_emitidos.columns, ['concl', 'conclusao'], 'conclusao')
    col_folha_real = encontrar_coluna_por_multiplas_palavras(df_emitidos.columns, ['folh', 'folha'], 'folha')
    col_cpf_emitidos = encontrar_coluna_por_multiplas_palavras(df_emitidos.columns, ['cpf'], 'cpf')
    
    colunas_para_trazer = ['matricula', col_emec_real, col_ingresso_real, col_conclusao_real, col_folha_real, col_cpf_emitidos]
    colunas_para_trazer = [c for c in list(set(colunas_para_trazer)) if c in df_emitidos.columns]
    
    # Merge/PROCV unificando as informações pela matrícula
    if 'matricula' in df_digitais.columns and 'matricula' in df_emitidos.columns:
        df_mesclado = pd.merge(df_digitais, df_emitidos[colunas_para_trazer], on='matricula', how='left')
    else:
        df_mesclado = df_digitais.copy()
        alertas.append({"mensagem": "Coluna 'matricula' não foi localizada para o cruzamento direto."})
    
    # Localiza de forma dinâmica o campo do Livro
    coluna_livro_real = encontrar_coluna_por_multiplas_palavras(df_mesclado.columns, ['livro'], 'livro')
    
    # Mapeamento para os nomes formais
    mapeamento_exibicao = {
        'aluno': 'Aluno',
        col_cpf_emitidos: 'CPF',
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
    
    # Higieniza valores nulos
    for col in [
        'Aluno', 'CPF', 'e-MEC', 'Curso', 'Ingresso', 
        'Conclusao', 'Homologacao', 'Folha', 'Livro', 'Registro da homologação'
    ]:
        if col not in df_mesclado.columns:
            df_mesclado[col] = "-"
        else:
            df_mesclado[col] = df_mesclado[col].fillna("-")
            df_mesclado[col] = df_mesclado[col].replace(['nan', 'NaN', 'None', ''], '-')
            
    # Formatação visual padronizada
    df_mesclado['Aluno'] = df_mesclado['Aluno'].astype(str).str.upper().str.strip()
    df_mesclado['Curso'] = df_mesclado['Curso'].astype(str).str.upper().str.strip()
    df_mesclado['CPF'] = df_mesclado['CPF'].apply(limpar_e_mascarar_cpf)
    df_mesclado['Homologacao'] = df_mesclado['Homologacao'].astype(str).str.strip()
    df_mesclado['Folha'] = df_mesclado['Folha'].astype(str).str.strip()
    
    # Reordena as colunas
    sequencia_oficial = [
        'Aluno', 'CPF', 'e-MEC', 'Curso', 'Ingresso', 
        'Conclusao', 'Homologacao', 'Folha', 'Livro', 'Registro da homologação'
    ]
    
    cols_existentes = [c for c in sequencia_oficial if c in df_mesclado.columns]
    df_final = df_mesclado[cols_existentes].copy()
    
    if 'Aluno' in df_final.columns:
        df_final = df_final.sort_values(by='Aluno', ascending=True)

    # 4. Geração do buffer de Excel
    buffer_excel = io.BytesIO()
    with pd.ExcelWriter(buffer_excel, engine='openpyxl') as writer:
        df_final.to_excel(writer, index=False, sheet_name='Cruzamento_Diplomas')
    buffer_excel.seek(0)

    return df_final, alertas, buffer_excel