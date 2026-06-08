import pandas as pd
from datetime import datetime
from collections import namedtuple

# Dicionário global para garantir a tradução dos meses
MESES_PT = {
    1: "janeiro", 2: "fevereiro", 3: "março", 4: "abril",
    5: "maio", 6: "junho", 7: "julho", 8: "agosto",
    9: "setembro", 10: "outubro", 11: "novembro", 12: "dezembro"
}

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
            return MESES_PT[data_ref.month], data_ref.strftime("%Y")
    except: 
        pass
    
    hoje = datetime.now()
    return MESES_PT[hoje.month], str(hoje.year)


# 2. FUNÇÃO ATUALIZADA (Retorna o RTF e a Prévia HTML)
def gerar_texto_rtf(df_final, resumo_livros, total_geral):
    mes_referencia, _ = descobrir_mes_referencia(df_final)
    
    hoje = datetime.now()
    mes_assinatura_pt = MESES_PT[hoje.month]
    data_assinatura = f"{hoje.strftime('%d')} de {mes_assinatura_pt} de {hoje.strftime('%Y')}"
    
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
    
    # ----------------------------------------------------
    # 1. GERAÇÃO DO RTF BRUTO (Para o arquivo de download)
    # ----------------------------------------------------
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

    # ----------------------------------------------------
    # 2. GERAÇÃO DA PRÉVIA HTML (Para renderizar na tela)
    # ----------------------------------------------------
    template_previa_html = f"""
    <div style="font-family: 'Calibri', sans-serif; line-height: 1.6; color: #333; padding: 20px; text-align: justify;">
        <div style="text-align: center; font-weight: bold; margin-bottom: 20px;">##ATO AVISO DE REGISTRO DE DIPLOMAS</div>
        
        <p style="text-indent: 30px; margin-bottom: 15px;">
            O Instituto Capivara Learning, CNPJ no 10.738.898/0001-75, em atendimento ao disposto no art. 21 da Portaria MEC n° 1.095 de 25 de outubro de 2018 informa que, no mes de <strong>{mes_referencia}</strong> do corrente ano, registrou {total_geral} diplomas assim distribuidos: {texto_livros_corrido}.
        </p>
        
        <p style="text-indent: 30px; margin-bottom: 30px;">
            A relacao dos diplomas registrados podera ser consultada em ate trinta dias, no endereco eletronico <a href="https://www.icl.edu.br/pre/controle-academico/erd" target="_blank">https://www.icl.edu.br/pre/controle-academico/erd</a>.
        </p>
        
        <div style="text-align: center; font-weight: bold; margin-bottom: 15px;">##DAT Joao Pessoa, {data_assinatura}</div>
        <div style="text-align: center; font-weight: bold;">##ASS Capivara Svenson</div>
        <div style="text-align: center; font-weight: bold;">##CAR Reitora</div>
    </div>
    """

    # Retorna ambos em um dicionário
    return {
        "rtf": template_rtf,
        "html_previa": template_previa_html
    }