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
    mes_referencia_orig, _ = descobrir_mes_referencia(df_final)
    
    # Dicionário de tradução para garantir Português
    traducao_meses = {
        'january': 'janeiro', 'february': 'fevereiro', 'march': 'marco', 'april': 'abril',
        'may': 'maio', 'june': 'junho', 'july': 'julho', 'august': 'agosto',
        'september': 'setembro', 'october': 'outubro', 'november': 'novembro', 'december': 'dezembro'
    }
    mes_referencia = traducao_meses.get(mes_referencia_orig.lower(), mes_referencia_orig)
    
    hoje = datetime.now()
    data_assinatura = f"{hoje.day} de {traducao_meses.get(hoje.strftime('%B').lower())} de {hoje.year}"
    
    # 1. Declaração da variável ANTES do loop
    texto_livros_corrido = ""
    
    if resumo_livros:
        trechos_livros = []
        for linha in resumo_livros:
            inicio = int(linha.Primeiro_Registro) if not pd.isna(linha.Primeiro_Registro) else 0
            fim = int(linha.Ultimo_Registro) if not pd.isna(linha.Ultimo_Registro) else 0
            total = linha.Total_Registros
            if total == 1:
                trechos_livros.append(f"livro {linha.Livro} com 1 registro numerado com o numero {inicio}")
            elif total == 2:
                trechos_livros.append(f"livro {linha.Livro} com 2 registros numerados com os numeros {inicio} e {fim}")
            else:
                trechos_livros.append(f"livro {linha.Livro} com {total} registros numerados no intervalo de {inicio} a {fim}")
        
        texto_livros_corrido = "; ".join(trechos_livros)

    # O formato de página do LibreOffice exige tanto o comando geral quanto o da seção (sxn)
    # 9cm = 5103 twips | 29.7cm = 16838 twips
    # Margens: 1cm = 567 | 0.43cm = 244
    config_pagina = r"\landscape\paperh5103\paperw16838\margl567\margr244\margt567\margb238\sectd\pgwsxn16838\pghsxn5103\marglsxn567\margrsxn244\margtsxn567\margbsxn238\fs18"
    
   template_rtf = f"""{{\\rtf1\\ansi\\deff0 
{{\\fonttbl{{\\f0 Calibri;}}}}
{config_pagina}
{{\\qc\\b ##ATO\\b0  AVISO DE REGISTRO DE DIPLOMAS}}\\par
\\par
{{\\qj\\fi567 \\b ##TEX\\b0  O Instituto Capivara Learning, CNPJ no 10.738.898/0001-75, em atendimento ao disposto no art. 21 da Portaria MEC n° 1.095 de 25 de outubro de 2018 informa que, no mes de {mes_referencia} do corrente ano, registrou {total_geral} diplomas assim distribuidos: {texto_livros_corrido}.}}\\par
{{\\qj\\fi567 A relacao dos diplomas registrados podera ser consultada em ate trinta dias, no endereco eletronico https://www.icl.edu.br/pre/controle-academico/erd.}}\\par
\\par
{{\\qc\\b ##DAT\\b0  Joao Pessoa, {data_assinatura}}}\\par
\\par
{{\\qc\\b ##ASS\\b0  Capivara Svenson}}\\par
{{\\qc\\b ##CAR\\b0  Reitora}}\\par
}}"""
    
    return template_rtf
    
