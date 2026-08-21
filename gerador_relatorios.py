import pandas as pd
import re
from datetime import datetime

MESES_PT = {
    1: "janeiro", 2: "fevereiro", 3: "março", 4: "abril",
    5: "maio", 6: "junho", 7: "julho", 8: "agosto",
    9: "setembro", 10: "outubro", 11: "novembro", 12: "dezembro"
}

def encontrar_coluna_homologacao(df):
    """Localiza a coluna de homologação independentemente de acentos ou maiúsculas."""
    coli_map = {str(col).strip().lower(): col for col in df.columns}
    opcoes = ['data da homologação', 'data da homologacao', 'homologacao', 'data homologacao']
    
    for op in opcoes:
        if op in coli_map:
            return coli_map[op]
    return None

def extrair_mes_dominante(df):
    """Extrai o mês mais frequente interpretando o formato brasileiro DD/MM/AAAA."""
    col_homolog = encontrar_coluna_homologacao(df)
    
    if col_homolog:
        datas = pd.to_datetime(df[col_homolog], dayfirst=True, errors='coerce')
        datas_validas = datas.dropna()
        
        if not datas_validas.empty:
            mes_num = int(datas_validas.dt.month.mode()[0])
            return MESES_PT.get(mes_num, "agosto")
            
    # Fallback: mês atual da execução
    mes_atual = datetime.now().month
    return MESES_PT.get(mes_atual, "agosto")

def extrair_ano_dominante(df):
    """Extrai o ano mais frequente a partir da coluna de Homologação."""
    col_homolog = encontrar_coluna_homologacao(df)
    
    if col_homolog:
        datas = pd.to_datetime(df[col_homolog], dayfirst=True, errors='coerce')
        datas_validas = datas.dropna()
        if not datas_validas.empty:
            return int(datas_validas.dt.year.mode()[0])
            
    return datetime.now().year

def extrair_numero_inteiro(val):
    """Extrai números inteiros de campos compostos de texto/número."""
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

def gerar_dados_relatorio(df, nome_reitor="Mary Roberta Meira Marinho", cargo_reitor="Reitora", mes_referencia=None):
    total_diplomas = len(df)
    
    # Define o mês: se veio da requisição usa ele; senão, calcula via dataframe/sistema
    mes_nome = mes_referencia if mes_referencia else extrair_mes_dominante(df)
    ano_num = extrair_ano_dominante(df)
    
    # Data de emissão completa (ex: 21 de agosto de 2026)
    dia_atual = datetime.now().day
    mes_atual_nome = MESES_PT.get(datetime.now().month, "agosto")
    data_emissao_texto = f"{dia_atual} de {mes_atual_nome} de {ano_num}"

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

    # 2. Prévia HTML
    previa_html = f"""
    <div style="font-family: Arial, sans-serif; line-height: 1.6; text-align: justify; color: #1f2937;">
        <h3 style="text-align: center; margin-bottom: 20px; font-weight: bold; font-size: 16px;">ATO AVISO DE REGISTRO DE DIPLOMAS</h3>
        <p>O Instituto Federal de Educacao, Ciencia e Tecnologia da Paraiba - IFPB, CNPJ no 10.738.898/0001-75, em atendimento ao disposto no art. 21 da Portaria MEC numero 1.095 de 25 de outubro de 2018 informa que, no mes de <strong>{mes_nome}</strong> do corrente ano, registrou {total_diplomas} diplomas assim distribuidos: {resumo_livros_texto}.</p>
        <p style="margin-top: 20px;">A relacao dos diplomas registrados podera ser consultada em ate trinta dias, no endereco eletronico <a href="https://www.ifpb.edu.br/pre/controle-academico/erd" target="_blank">https://www.ifpb.edu.br/pre/controle-academico/erd</a>.</p>
        <br/>
        <div style="text-align: center; margin-top: 20px;">
            <p style="margin: 0; font-weight: bold;">Joao Pessoa, {data_emissao_texto}</p>
            <br/>
            <p style="margin: 0; font-weight: bold;">{nome_reitor}</p>
            <p style="margin: 0; color: #4b5563;">{cargo_reitor}</p>
        </div>
    </div>
    """

    # 3. Documento RTF
    previa_rtf = f"""{{\\rtf1\\ansi\\deff0
{{\\fonttbl{{\\f0\\fnil\\fcharset0 Arial;}}}}
\\viewkind4\\uc1\\pard\\qc\\b\\f0\\fs24 ATO AVISO DE REGISTRO DE DIPLOMAS\\b0\\par
\\par
\\pard\\qj\\fs20 O Instituto Federal de Educacao, Ciencia e Tecnologia da Paraiba - IFPB, CNPJ no 10.738.898/0001-75, em atendimento ao disposto no art. 21 da Portaria MEC numero 1.095 de 25 de outubro de 2018 informa que, no mes de {mes_nome} do corrente ano, registrou {total_diplomas} diplomas assim distribuidos: {resumo_livros_texto}.\\par
\\par
A relacao dos diplomas registrados podera ser consultada em ate trinta dias, no endereco eletronico https://www.ifpb.edu.br/pre/controle-academico/erd.\\par
\\par
\\par
\\pard\\qc Joao Pessoa, {data_emissao_texto}\\par
\\par
\\b {nome_reitor}\\b0\\par
{cargo_reitor}\\par
}}"""

    return {
        "total_geral": total_diplomas,
        "resumo_livros": resumo_livros_lista,
        "previa_html": previa_html,
        "previa_texto_rtf": previa_rtf
    }