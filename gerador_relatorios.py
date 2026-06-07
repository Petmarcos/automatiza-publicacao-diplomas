import locale
import pandas as pd
from datetime import datetime

# Configuração de localização para português
try:
    locale.setlocale(locale.LC_TIME, "pt_BR.utf8")
except:
    try:
        locale.setlocale(locale.LC_TIME, "Portuguese_Brazil.1252")
    except:
        pass


def calcular_resumo_livros(df_final):
    """
    Função que agrupa os dados por Livro e encontra o total de registros,
    o primeiro e o último número de registro de cada livro.
    """
    # Garante que a coluna de registro está em formato numérico para ordenar certo
    df_final['Registro da homologação'] = pd.to_numeric(df_final['Registro da homologação'], errors='coerce')
    
    # Agrupa por livro e extrai as estatísticas necessárias
    resumo = df_final.groupby('Livro').agg(
        Total_Registros=('Registro da homologação', 'count'),
        Primeiro_Registro=('Registro da homologação', 'min'),
        Ultimo_Registro=('Registro da homologação', 'max')
    ).reset_index()
    
    # Transforma o resultado em uma lista de objetos nomeados (namedtuples) para o Python ler fácil
    from collections import namedtuple
    LinhaResumo = namedtuple('LinhaResumo', ['Livro', 'Total_Registros', 'Primeiro_Registro', 'Ultimo_Registro'])
    
    return [LinhaResumo(**row) for row in resumo.to_dict(orient='records')]


def descobrir_mes_referencia(df_final):
    """
    Analisa as datas na planilha para descobrir o mês e o ano de referência dos diplomas.
    """
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
    
    # Fallback seguro caso não ache a coluna: pega o mês anterior baseado no dia de hoje
    hoje = datetime.now()
    mes_anterior = 12 if hoje.month == 1 else hoje.month - 1
    ano_anterior = hoje.year - 1 if hoje.month == 1 else hoje.year
    data_ficticia = datetime(ano_anterior, mes_anterior, 1)
    return data_ficticia.strftime("%B").lower(), str(ano_anterior)


def gerar_texto_rtf(df_final, resumo_livros, total_geral):
    # ... (lógica de data/livros igual) ...

    # 1. Definimos a Calibri como \f0 na tabela de fontes
    # 2. \fs18 define o tamanho 9 (18 meios-pontos)
    config_pagina = r"\sectd\paperh11906\paperw16838\margl567\margr244\margt567\margb238\pgwsxn16838\pghsxn11906\marglsxn567\margrsxn244\margtsxn567\margbsxn238\fs18"
    
    template_rtf = f"""{{\\rtf1\\ansi\\deff0 
{{\\fonttbl{{\\f0 Calibri;}}}}
{config_pagina}
{{\\b ##ATO\\b0  AVISO DE REGISTRO DE DIPLOMAS}}\\par
{{\\b ##TEX\\b0  O Instituto Capivara Learning, CNPJ no 10.738.898/0001-75, em atendimento ao disposto no art. 21 da Portaria MEC n° 1.095 de 25 de outubro de 2018 informa que, no mes de {mes_referencia} do corrente ano, registrou {total_geral} diplomas assim distribuidos: {texto_livros_corrido}.}}\\par
A relacao dos diplomas registrados podera ser consultada em ate trinta dias, no endereco eletronico https://www.icl.edu.br/pre/controle-academico/erd.\\par
\\par
{{\\b ##DAT\\b0  Joao Pessoa, {data_assinatura}}}\\par
\\par
{{\\b ##ASS\\b0  Capivara Svenson}}\\par
{{\\b ##CAR\\b0  Reitora}}\\par
}}"""
    
    return template_rtf