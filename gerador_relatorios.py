import pandas as pd
import re
from datetime import datetime

MESES_PT = {
    1: "janeiro", 2: "fevereiro", 3: "março", 4: "abril",
    5: "maio", 6: "junho", 7: "julho", 8: "agosto",
    9: "setembro", 10: "outubro", 11: "novembro", 12: "dezembro"
}

def extrair_mes_dominante(df):
    """Extrai o mês predominante a partir da coluna de Homologação."""
    if 'Homologacao' in df.columns:
        datas = pd.to_datetime(df['Homologacao'], errors='coerce', dayfirst=True)
        datas_validas = datas.dropna()
        if not datas_validas.empty:
            mes_num = int(datas_validas.dt.month.mode()[0])
            return MESES_PT.get(mes_num, "julho")
    
    # Fallback para o mês corrente
    mes_atual = datetime.now().month
    return MESES_PT.get(mes_atual, "julho")

def extrair_ano_dominante(df):
    """Extrai o ano predominante a partir da coluna de Homologação."""
    if 'Homologacao' in df.columns:
        datas = pd.to_datetime(df['Homologacao'], errors='coerce', dayfirst=True)
        datas_validas = datas.dropna()
        if not datas_validas.empty:
            return int(datas_validas.dt.year.mode()[0])
    return datetime.now().year

def extrair_numero_inteiro(val):
    if pd.isna(val):
        return None
    nums = re.findall(r'\d+', str(val))
    return int(nums[0]) if nums else None

def gerar_texto_resumo_livros(df):
    """Gera o trecho textual formatado de distribuição por livros."""
    if df.empty or 'Livro' not in df.columns:
        return ""

    resumo_partes = []
    
    for livro, grupo in df.groupby('Livro', sort=False):
        qtd = len(grupo)
        registros = []
        
        if 'Registro da homologação' in grupo.columns:
            for reg in grupo['Registro da homologação']:
                num = extrair_numero_inteiro(reg)
                if num is not None:
                    registros.append(num)
        
        if registros:
            reg_min = min(registros)
            reg_max = max(registros)
            if reg_min == reg_max:
                texto_intervalo = f"numerado com o numero {reg_min}"
            elif qtd == 2 and len(registros) == 2:
                texto_intervalo = f"numerados com os numeros {reg_min} e {reg_max}"
            else:
                texto_intervalo = f"numerados no intervalo de {reg_min} a {reg_max}"
        else:
            texto_intervalo = "com registros processados"

        pl_registro = "registro" if qtd == 1 else "registros"
        resumo_partes.append(f"livro {livro} com {qtd} {pl_registro} {texto_intervalo}")

    if len(resumo_partes) == 1:
        return resumo_partes[0]
    elif len(resumo_partes) == 2:
        return f"{resumo_partes[0]} e {resumo_partes[1]}"
    else:
        return ", ".join(resumo_partes[:-1]) + f"; e {resumo_partes[-1]}"

def gerar_dados_relatorio(df, nome_reitor="Mary Roberta Meira Marinho", cargo_reitor="Reitora"):
    total_diplomas = len(df)
    mes_nome = extrair_mes_dominante(df)
    ano_num = extrair_ano_dominante(df)
    resumo_livros_texto = gerar_texto_resumo_livros(df)

    # 1. Tabela Resumo para a Interface
    resumo_livros_lista = []
    if 'Livro' in df.columns:
        for livro, grupo in df.groupby('Livro', sort=False):
            registros = [extrair_numero_inteiro(r) for r in grupo.get('Registro da homologação', []) if extrair_numero_inteiro(r) is not None]
            if registros:
                reg_min = min(registros)
                reg_max = max(registros)
                intervalo_str = f"{reg_min}" if reg_min == reg_max else f"{reg_min} a {reg_max}"
            else:
                intervalo_str = "-"
                
            resumo_livros_lista.append({
                "livro": str(livro),
                "quantidade": len(grupo),
                "intervalo": intervalo_str
            })

    # 2. Prévia HTML (Corrigido o '##' do título)
    previa_html = f"""
    <div style="font-family: Arial, sans-serif; line-height: 1.6; text-align: justify; color: #1f2937;">
        <h3 style="text-align: center; margin-bottom: 20px; font-weight: bold; font-size: 16px;">ATO AVISO DE REGISTRO DE DIPLOMAS</h3>
        <p>O Instituto Federal de Educacao, Ciencia e Tecnologia da Paraiba - IFPB, CNPJ no 10.738.898/0001-75, em atendimento ao disposto no art. 21 da Portaria MEC numero 1.095 de 25 de outubro de 2018 informa que, no mes de <strong>{mes_nome}</strong> do corrente ano, registrou {total_diplomas} diplomas assim distribuidos: {resumo_livros_texto}.</p>
        <p style="margin-top: 20px;">A relacao dos diplomas registrados encontra-se no site <a href="https://www.ifpb.edu.br" target="_blank">www.ifpb.edu.br</a>.</p>
        <br/>
        <div style="text-align: center; margin-top: 30px;">
            <p style="margin: 0; font-weight: bold;">{nome_reitor}</p>
            <p style="margin: 0; color: #4b5563;">{cargo_reitor}</p>
        </div>
    </div>
    """

    # 3. Prévia RTF
    previa_rtf = f"""{{\\rtf1\\ansi\\deff0
{{\\fonttbl{{\\f0\\fnil\\fcharset0 Arial;}}}}
\\viewkind4\\uc1\\pard\\qc\\b\\f0\\fs24 ATO AVISO DE REGISTRO DE DIPLOMAS\\b0\\par
\\par
\\pard\\qj\\fs20 O Instituto Federal de Educacao, Ciencia e Tecnologia da Paraiba - IFPB, CNPJ no 10.738.898/0001-75, em atendimento ao disposto no art. 21 da Portaria MEC numero 1.095 de 25 de outubro de 2018 informa que, no mes de {mes_nome} do corrente ano, registrou {total_diplomas} diplomas assim distribuidos: {resumo_livros_texto}.\\par
\\par
A relacao dos diplomas registrados encontra-se no site www.ifpb.edu.br.\\par
\\par
\\par
\\pard\\qc\\b {nome_reitor}\\b0\\par
{cargo_reitor}\\par
}}"""

    return {
        "total_geral": total_diplomas,
        "resumo_livros": resumo_livros_lista,
        "previa_html": previa_html,
        "previa_texto_rtf": previa_rtf
    }