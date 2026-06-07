import pandas as pd
from datetime import datetime
from collections import namedtuple

def calcular_resumo_livros(df_final):
    df_final['Registro da homologação'] = pd.to_numeric(df_final['Registro da homologação'], errors='coerce')
    resumo = df_final.groupby('Livro').agg(
        Total_Registros=('Registro da homologação', 'count'),
        Primeiro_Registro=('Registro da homologação', 'min'),
        Ultimo_Registro=('Registro da homologação', 'max')
    ).reset_index()
    
    LinhaResumo = namedtuple('LinhaResumo', ['Livro', 'Total_Registros', 'Primeiro_Registro', 'Ultimo_Registro'])
    return [LinhaResumo(**row) for row in resumo.to_dict(orient='records')]

def descobrir_mes_referencia(df_final):
    try:
        datas = pd.to_datetime(df_final['Homologacao'], errors='coerce')
        datas_validas = datas.dropna()
        if not datas_validas.empty:
            data_referencia = datas_validas.iloc[0]
            mes_extenso = data_referencia.strftime("%B").lower()
            ano_corrente = data_referencia.strftime("%Y")
            return mes_extenso, ano_corrente
    except Exception:
        pass
    hoje = datetime.now()
    mes_anterior = 12 if hoje.month == 1 else hoje.month - 1
    ano_anterior = hoje.year - 1 if hoje.month == 1 else hoje.year
    data_ficticia = datetime(ano_anterior, mes_anterior, 1)
    return data_ficticia.strftime("%B").lower(), str(ano_anterior)

def gerar_texto_rtf(df_final, resumo_livros, total_geral, mes_referencia, data_assinatura):
    # Processa o texto corrido aqui dentro para evitar erros de escopo
    trechos = [f"livro {r.Livro} com {r.Total_Registros} registros numerados no intervalo de {r.Primeiro_Registro} a {r.Ultimo_Registro}" for r in resumo_livros]
    texto_livros_corrido = "; ".join(trechos)

    # Configuração de página
    config_pagina = r"\landscape\paperh5103\paperw16838\margl567\margr244\margt567\margb238"
    
    template_rtf = f"""{{\\rtf1\\ansi\\deff0 
{{\\fonttbl{{\\f0 Calibri;}}}}
{config_pagina}
\\pard\\qc\\b ##ATO AVISO DE REGISTRO DE DIPLOMAS\\b0\\par
\\pard\\qc\\fs18 \\par
\\pard\\qj\\fi567\\li0\\b ##TEX\\b0  \\tab O Instituto Capivara Learning, CNPJ no 10.738.898/0001-75, em atendimento ao disposto no art. 21 da Portaria MEC n° 1.095 de 25 de outubro de 2018 informa que, no mes de {mes_referencia} do corrente ano, registrou {total_geral} diplomas assim distribuidos: {texto_livros_corrido}.\\par
\\pard\\qj\\fi567\\li0 \\tab A relacao dos diplomas registrados podera ser consultada em ate trinta dias, no endereco eletronico https://www.icl.edu.br/pre/controle-academico/erd.\\par
\\pard\\par
\\pard\\qc\\b ##DAT Joao Pessoa, {data_assinatura}\\b0\\par
\\pard\\par
\\pard\\qc\\b ##ASS Capivara Svenson\\b0\\par
\\pard\\qc\\b ##CAR Reitora\\b0\\par
}}"""
    return template_rtf

# --- Exemplo de como você deve chamar isso no seu fluxo principal ---
# mes, ano = descobrir_mes_referencia(df)
# mes_ref = f"{mes} de {ano}"
# data_ass = datetime.now().strftime("%d de %B de %Y")
# resumo = calcular_resumo_livros(df)
# total = df.shape[0]
# rtf_final = gerar_texto_rtf(df, resumo, total, mes_ref, data_ass)