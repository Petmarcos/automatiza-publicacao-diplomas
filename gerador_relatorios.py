import pandas as pd
from datetime import datetime
from collections import namedtuple

# 1. Funções de suporte (mantidas como você gosta)
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

# 2. A FUNÇÃO UNIFICADA (Ela calcula tudo internamente para evitar erros de escopo)
def gerar_texto_rtf(df_final, resumo_livros, total_geral):
    # Cálculo interno para garantir que as variáveis existam
    mes_referencia, ano_referencia = descobrir_mes_referencia(df_final)
    data_assinatura = datetime.now().strftime("%d de %B de %Y")
    config_pagina = r"\landscape\paperh5103\paperw16838\margl567\margr244\margt567\margb238"
    
    trechos_livros = []
    for linha in resumo_livros:
        livro = linha.Livro
        total = linha.Total_Registros
        inicio = int(linha.Primeiro_Registro) if not pd.isna(linha.Primeiro_Registro) else 0
        fim = int(linha.Ultimo_Registro) if not pd.isna(linha.Ultimo_Registro) else 0
        if total == 1:
            trechos_livros.append(f"livro {livro} com 1 registro numerado com o numero {inicio}")
        elif total == 2:
            trechos_livros.append(f"livro {livro} com 2 registros numerados com os numeros {inicio} e {fim}")
        else:
            trechos_livros.append(f"livro {livro} com {total} registros numerados no intervalo de {inicio} a {fim}")
    
    texto_livros_corrido = "; ".join(trechos_livros)
    
    # Template RTF consolidado
    template_rtf = f"""{{\\rtf1\\ansi\\deff0 
{{\\fonttbl{{\\f0 Calibri;}}}}
{config_pagina}
\\pard\\qc\\b ##ATO AVISO DE REGISTRO DE DIPLOMAS\\b0\\par
\\par
\\pard\\qj\\fi567\\li0\\sa200  O Instituto Capivara Learning, CNPJ no 10.738.898/0001-75, em atendimento ao disposto no art. 21 da Portaria MEC n° 1.095 de 25 de outubro de 2018 informa que, no mes de {mes_referencia} do corrente ano, registrou {total_geral} diplomas assim distribuidos: {texto_livros_corrido}.\\par
\\pard\\qj\\fi567\\li0\\sa200  A relacao dos diplomas registrados podera ser consultada em ate trinta dias, no endereco eletronico https://www.icl.edu.br/pre/controle-academico/erd.\\par
\\par
\\pard\\qc\\b ##DAT Joao Pessoa, {data_assinatura}\\b0\\par
\\par
\\pard\\qc\\b ##ASS Capivara Svenson\\b0\\par
\\pard\\qc\\b ##CAR Reitora\\b0\\par
}}"""
    return template_rtf