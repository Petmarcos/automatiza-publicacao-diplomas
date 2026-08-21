import pandas as pd
import io
import re

def extrair_numero_inteiro(val):
    if pd.isna(val):
        return None
    nums = re.findall(r'\d+', str(val))
    return int(nums[0]) if nums else None

def processar_planilhas(file_digitais_bytes, file_emitidos_bytes):
    alertas = []
    
    # 1. Leitura das planilhas em memória
    try:
        df_digitais = pd.read_excel(file_digitais_bytes)
        df_emitidos = pd.read_excel(file_emitidos_bytes)
    except Exception as e:
        raise ValueError(f"Erro ao ler os arquivos Excel: {str(e)}")

    # Padroniza nomes de colunas
    df_digitais.columns = [str(c).strip() for c in df_digitais.columns]
    df_emitidos.columns = [str(c).strip() for c in df_emitidos.columns]

    # 2. Localização flexível do campo Livro
    col_livro_dig = next((c for c in df_digitais.columns if 'livro' in c.lower()), None)
    col_livro_emi = next((c for c in df_emitidos.columns if 'livro' in c.lower()), None)

    if col_livro_dig:
        df_digitais.rename(columns={col_livro_dig: 'Livro'}, inplace=True)
    if col_livro_emi:
        df_emitidos.rename(columns={col_livro_emi: 'Livro'}, inplace=True)

    # 3. Processamento/Unificação dos dados
    # Se a planilha de emitidos tiver os dados principais, usamos ela como base
    df_final = df_emitidos.copy() if not df_emitidos.empty else df_digitais.copy()

    # Checagem básica de integridade/alertas
    if df_digitais.empty:
        alertas.append({"mensagem": "A planilha de diplomas digitais está vazia."})
    if df_emitidos.empty:
        alertas.append({"mensagem": "A planilha de diplomas emitidos está vazia."})

    # 4. Geração do Excel de saída em memória
    buffer_excel = io.BytesIO()
    with pd.ExcelWriter(buffer_excel, engine='openpyxl') as writer:
        df_final.to_excel(writer, index=False, sheet_name='Diplomas_Processados')
    buffer_excel.seek(0)

    return df_final, alertas, buffer_excel