import pandas as pd
import re
from datetime import datetime

MESES_PT = {
    1: "janeiro", 2: "fevereiro", 3: "março", 4: "abril",
    5: "maio", 6: "junho", 7: "julho", 8: "agosto",
    9: "setembro", 10: "outubro", 11: "novembro", 12: "dezembro"
}

MESES_MAP = {
    'jan': 'janeiro', 'janeiro': 'janeiro',
    'fev': 'fevereiro', 'fevereiro': 'fevereiro',
    'mar': 'março', 'marco': 'março', 'março': 'março',
    'abr': 'abril', 'abril': 'abril',
    'mai': 'maio', 'maio': 'maio',
    'jun': 'junho', 'junho': 'junho',
    'jul': 'julho', 'julho': 'julho',
    'ago': 'agosto', 'agosto': 'agosto',
    'set': 'setembro', 'setembro': 'setembro',
    'out': 'outubro', 'outubro': 'outubro',
    'nov': 'novembro', 'novembro': 'novembro',
    'dez': 'dezembro', 'dezembro': 'dezembro'
}

def extrair_numero_inteiro(val):
    if pd.isna(val):
        return None
    nums = re.findall(r'\d+', str(val))
    return int(nums[0]) if nums else None

def extrair_mes_dominante(df):
    col_homolog = None
    for c in df.columns:
        if 'homolog' in str(c).lower():
            col_homolog = c
            break

    if not col_homolog:
        return MESES_PT.get(datetime.now().month, "agosto")

    meses_encontrados = []
    for val in df[col_homolog].dropna():
        val_str = str(val).strip().lower()
        for chave, mes_extenso in MESES_MAP.items():
            if chave in val_str:
                meses_encontrados.append(mes_extenso)
                break
        else:
            dt = pd.to_datetime(val_str, errors='coerce', dayfirst=True)
            if not pd.isna(dt):
                meses_encontrados.append(MESES_PT.get(dt.month))

    if meses_encontrados:
        return max(set(meses_encontrados), key=meses_encontrados.count)
    return MESES_PT.get(datetime.now().month, "agosto")

def extrair_ano_dominante(df):
    col_homolog = None
    for c in df.columns:
        if 'homolog' in str(c).lower():
            col_homolog = c
            break

    if col_homolog:
        anos = []
        for val in df[col_homolog].dropna():
            nums = re.findall(r'20\d{2}', str(val))
            if nums:
                anos.append(nums[0])
        if anos:
            return max(set(anos), key=anos.count)
            
    return str(datetime.now().year)

def gerar_texto_resumo_livros(df):
    if 'Livro' not in df.columns:
        return f"{len(df)} diplomas"

    col_reg = None
    for c in df.columns:
        if 'registro' in str(c).lower():
            col_reg = c
            break

    partes = []
    for livro, grupo in df.groupby('Livro', sort=False):
        qtd = len(grupo)
        registros = []
        if col_reg:
            registros = [extrair_numero_inteiro(r) for r in grupo[col_reg] if extrair_numero_inteiro(r) is not None]

        if registros:
            reg_min = min(registros)
            reg_max = max(registros)
            if reg_min == reg_max:
                partes.append(f"livro {livro} com {qtd} registro numerado com o numero {reg_min}")
            else:
                partes.append(f"livro {livro} com {qtd} registros numerados no intervalo de {reg_min} a {reg_max}")
        else:
            partes.append(f"livro {livro} com {qtd} registros")

    if len(partes) > 1:
        return "; ".join(partes[:-1]) + "; e " + partes[-1]
    elif partes:
        return partes[0]
    return f"{len(df)} diplomas"

def gerar_dados_relatorio(df, nome_reitor="Mary Roberta Meira Marinho", cargo_reitor="Reitora"):
    total_diplomas = len(df)
    mes_nome = extrair_mes_dominante(df)
    ano_num = extrair_ano_dominante(df)
    
    dia_atual = datetime.now().day
    mes_atual_nome = MESES_PT.get(datetime.now().month, "agosto")
    data_emissao_texto = f"{dia_atual} de {mes_atual_nome} de {ano_num}"

    resumo_livros_texto = gerar_texto_resumo_livros(df)

    resumo_livros_lista = []
    if 'Livro' in df.columns:
        col_reg = None
        for c in df.columns:
            if 'registro' in str(c).lower():
                col_reg = c
                break

        for livro, grupo in df.groupby('Livro', sort=False):
            registros = []
            if col_reg:
                registros = [extrair_numero_inteiro(r) for r in grupo[col_reg] if extrair_numero_inteiro(r) is not None]
                
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

    # Prévia HTML padronizada em Calibri 9pt
    previa_html = f"""
    <div style="font-family: Calibri, sans-serif; font-size: 12px; line-height: 1.5; text-align: justify; color: #000000;">
        <p style="text-align: center; font-weight: bold; font-size: 12px; margin-bottom: 20px;">##ATO AVISO DE REGISTRO DE DIPLOMAS</p>
        <p>O Instituto Federal de Educacao, Ciencia e Tecnologia da Paraiba - IFPB, CNPJ no 10.738.898/0001-75, em atendimento ao disposto no art. 21 da Portaria MEC numero 1.095 de 25 de outubro de 2018 informa que, no mes de {mes_nome} do corrente ano, registrou {total_diplomas} diplomas assim distribuidos: {resumo_livros_texto}.</p>
        <p style="margin-top: 15px;">A relacao dos diplomas registrados podera ser consultada em ate trinta dias, no endereco eletronico <a href="https://www.ifpb.edu.br/pre/controle-academico/erd" target="_blank" style="color: #000; text-decoration: underline;">https://www.ifpb.edu.br/pre/controle-academico/erd</a>.</p>
        <br/>
        <div style="text-align: center; margin-top: 25px;">
            <p style="margin: 0; font-weight: bold;">##DAT Joao Pessoa, {data_emissao_texto}</p>
            <br/>
            <p style="margin: 0; font-weight: bold;">##ASS {nome_reitor}</p>
            <p style="margin: 0; font-weight: bold;">##CAR {cargo_reitor}</p>
        </div>
    </div>
    """

    # Conteúdo em RTF para download
    previa_rtf = f"""{{\\rtf1\\ansi\\deff0
{{\\fonttbl{{\\f0\\fnil\\fcharset0 Calibri;}}}}
\\viewkind4\\uc1\\pard\\qc\\b\\f0\\fs18 ##ATO AVISO DE REGISTRO DE DIPLOMAS\\b0\\par
\\par
\\pard\\qj\\fs18 O Instituto Federal de Educacao, Ciencia e Tecnologia da Paraiba - IFPB, CNPJ no 10.738.898/0001-75, em atendimento ao disposto no art. 21 da Portaria MEC numero 1.095 de 25 de outubro de 2018 informa que, no mes de {mes_nome} do corrente ano, registrou {total_diplomas} diplomas assim distribuidos: {resumo_livros_texto}.\\par
\\par
A relacao dos diplomas registrados podera ser consultada em ate trinta dias, no endereco eletronico https://www.ifpb.edu.br/pre/controle-academico/erd.\\par
\\par
\\par
\\pard\\qc\\b\\fs18 ##DAT Joao Pessoa, {data_emissao_texto}\\par
\\par
##ASS {nome_reitor}\\par
##CAR {cargo_reitor}\\b0\\par
}}"""

    dados_tabela_final = df.to_dict(orient="records")

    return {
        "total_geral": total_diplomas,
        "resumo_livros": resumo_livros_lista,
        "previa_html": previa_html,
        "previa_texto_rtf": previa_rtf,
        "dados_tabela": dados_tabela_final
    }