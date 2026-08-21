import pandas as pd
import io
import re
from datetime import datetime

MESES_PT = {
    1: "janeiro", 2: "fevereiro", 3: "março", 4: "abril",
    5: "maio", 6: "junho", 7: "julho", 8: "agosto",
    9: "setembro", 10: "outubro", 11: "novembro", 12: "dezembro"
}

def extrair_numero_inteiro(val):
    if pd.isna(val):
        return None
    nums = re.findall(r'\d+', str(val))
    return int(nums[0]) if nums else None

def normalizar_colunas(df):
    """Padroniza os nomes das colunas removendo espaços extras."""
    df.columns = [str(c).strip() for c in df.columns]
    return df

def encontrar_coluna(df, palavras_chave):
    """Encontra a coluna correspondente a partir de palavras-chave."""
    for col in df.columns:
        col_lower = str(col).lower()
        if any(pc in col_lower for pc in palavras_chave):
            return col
    return None

def processar_planilhas(file_digitais_bytes, file_emitidos_bytes):
    alertas = []
    
    # 1. Leitura dos arquivos
    try:
        df_digitais = pd.read_excel(file_digitais_bytes)
        df_emitidos = pd.read_excel(file_emitidos_bytes)
    except Exception as e:
        raise ValueError(f"Erro na leitura dos arquivos Excel: {str(e)}")

    df_digitais = normalizar_colunas(df_digitais)
    df_emitidos = normalizar_colunas(df_emitidos)

    # 2. Identificação das chaves para o cruzamento
    col_chave_dig = encontrar_coluna(df_digitais, ['processo', 'cpf', 'matricula', 'aluno'])
    col_chave_emi = encontrar_coluna(df_emitidos, ['processo', 'cpf', 'matricula', 'aluno'])

    # 3. Cruzamento entre as planilhas
    if col_chave_dig and col_chave_emi:
        # Garante o mesmo tipo para cruzamento
        df_digitais[col_chave_dig] = df_digitais[col_chave_dig].astype(str).str.strip()
        df_emitidos[col_chave_emi] = df_emitidos[col_chave_emi].astype(str).str.strip()

        # Realiza o Merge (Cruzamento) mantendo apenas os registros equivalentes
        df_final = pd.merge(
            df_digitais,
            df_emitidos,
            left_on=col_chave_dig,
            right_on=col_chave_emi,
            how='inner',
            suffixes=('_digital', '_emitido')
        )
    else:
        # Caso não encontre chave de cruzamento direta, utiliza a de digitais como base
        alertas.append({"mensagem": "Não foi possível identificar a chave de cruzamento comum (ex: Processo ou CPF). Exibindo dados da planilha de digitais."})
        df_final = df_digitais.copy()

    # 4. Ajuste da coluna 'Livro' para agrupamento dos relatórios
    col_livro = encontrar_coluna(df_final, ['livro'])
    if col_livro:
        df_final.rename(columns={col_livro: 'Livro'}, inplace=True)
    elif 'Livro' not in df_final.columns:
        df_final['Livro'] = 'Não Identificado'

    # Ajuste da coluna 'Registro da homologação'
    col_registro = encontrar_coluna(df_final, ['registro', 'homologação', 'homologacao'])
    if col_registro and col_registro != 'Registro da homologação':
        df_final.rename(columns={col_registro: 'Registro da homologação'}, inplace=True)

    # Verificação de divergências de contagem
    qtd_dig = len(df_digitais)
    qtd_emi = len(df_emitidos)
    qtd_final = len(df_final)

    if qtd_dig != qtd_emi:
        alertas.append({"mensagem": f"Divergência detectada: Planilha de Digitais possui {qtd_dig} registros e Emitidos possui {qtd_emi}. O resultado cruzado contém {qtd_final} registros."})

    # 5. Exportação do Excel resultante em memória
    buffer_excel = io.BytesIO()
    with pd.ExcelWriter(buffer_excel, engine='openpyxl') as writer:
        df_final.to_excel(writer, index=False, sheet_name='Cruzamento_Diplomas')
    buffer_excel.seek(0)

    return df_final, alertas, buffer_excel