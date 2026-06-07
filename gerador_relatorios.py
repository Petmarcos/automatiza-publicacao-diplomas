import pandas as pd
from datetime import datetime
from collections import namedtuple

# 1. Funções de suporte inalteradas
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
            data_ref = datas_validas.iloc[0]
            return data_ref.strftime("%B").lower(), data_ref.strftime("%Y")
    except: pass
    hoje = datetime.now()
    return hoje.strftime("%B").lower(), str(hoje.year)

# 2. A FUNÇÃO "À PROVA DE ERROS"
# O uso de *args e **kwargs faz com que ela aceite QUALQUER número de argumentos
def gerar_texto_rtf(*args, **kwargs):
    # Recupera os dados dos argumentos, não importa como foram passados
    df_final = args[0]
    resumo_livros = args[1]
    total_geral = args[2]
    
    # Tenta pegar os novos argumentos se existirem, senão calcula na hora
    mes_extenso, ano = descobrir_mes_referencia(df_final)
    mes_referencia = kwargs.get('mes_referencia', f"{mes_extenso} de {ano}")
    data_assinatura = kwargs.get('data_assinatura', datetime.now().strftime("%d de %B de %Y"))
    
    trechos = [f"livro {r.Livro} com {r.Total_Registros} registros numerados no intervalo de {r.Primeiro_Registro} a {r.Ultimo_Registro}" for r in resumo_livros]
    texto_livros_corrido = "; ".join(trechos)

    config_pagina = r"\landscape\paperh5103\paperw16838\margl567\margr244\margt567\margb238"
    
    return f"""{{\\rtf1\\ansi\\deff0 
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

# 3. CHAMADA (Chame da forma mais simples possível)
resumo = calcular_resumo_livros(df_final)
total = df_final.shape[0]
conteudo_rtf = gerar_texto_rtf(df_final, resumo, total)