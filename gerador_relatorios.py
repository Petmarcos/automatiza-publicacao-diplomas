import pandas as pd
import re
from datetime import datetime

MESES_PT = {
    1: "janeiro", 2: "fevereiro", 3: "março", 4: "abril",
    5: "maio", 6: "junho", 7: "julho", 8: "agosto",
    9: "setembro", 10: "outubro", 11: "novembro", 12: "dezembro"
}

def extrair_mes_dominante(df):
    """
    Procura por datas em formato DD/MM/AAAA em todas as colunas do DataFrame,
    garantindo que não confunda com números seriais do Excel nemIDs.
    """
    meses_encontrados = []
    
    # Identifica colunas candidatas
    colunas_candidatas = [col for col in df.columns if any(p in str(col).lower() for p in ['homolog', 'data', 'dt'])]
    
    # Se não achou por nome, testa todas as colunas
    if not colunas_candidatas:
        colunas_candidatas = df.columns

    for col in colunas_candidatas:
        for val in df[col].dropna():
            val_str = str(val).strip()
            # Procura o padrão dd/mm/aaaa ou dd-mm-aaaa com regex estrito
            match = re.search(r'\b(\d{1,2})[/.-](\d{1,2})[/.-](\d{2,4})\b', val_str)
            if match:
                p1, p2, ano = int(match.group(1)), int(match.group(2)), int(match.group(3))
                
                # Formato brasileiro: p1 = dia, p2 = mês
                if 1 <= p2 <= 12 and 1 <= p1 <= 31:
                    meses_encontrados.append(p2)
                # Caso o dia venha depois (ex: aaaa-mm-dd)
                elif 1 <= p1 <= 12 and len(str(ano)) == 4 and p1 > 12:
                    meses_encontrados.append(p1)

    if meses_encontrados:
        # Retorna o mês mais frequente (moda)
        mes_mais_comum = max(set(meses_encontrados), key=meses_encontrados.count)
        return MESES_PT.get(mes_mais_comum, "agosto")
        
    # Se não encontrou nenhuma data, usa o mês atual (Agosto)
    return MESES_PT.get(datetime.now().month, "agosto")

def extrair_ano_dominante(df):
    """Extrai o ano mais frequente procurando padrões de 4 dígitos (ex: 2026)."""
    anos_encontrados = []
    
    colunas_candidatas = [col for col in df.columns if any(p in str(col).lower() for p in ['homolog', 'data', 'dt'])]
    if not colunas_candidatas:
        colunas_candidatas = df.columns

    for col in colunas_candidatas:
        for val in df[col].dropna():
            match = re.search(r'\b(202\d)\b', str(val))
            if match:
                anos_encontrados.append(int(match.group(1)))

    if anos_encontrados:
        return max(set(anos_encontrados), key=anos_encontrados.count)
        
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
        
        col_reg = None
        for c in grupo.columns:
            if 'registro' in str(c).lower():
                col_reg = c
                break
                
        if col_reg:
            for reg in grupo[col_reg]:
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
    
    # 1. Se o mês veio selecionado do frontend React, usa ele diretamente.
    # 2. Caso contrário, faz a busca estrita via expressão regular por DD/MM/AAAA.
    if mes_referencia and str(mes_referencia).strip() != "":
        mes_nome = str(mes_referencia).strip().lower()
    else:
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

    # Prévia HTML
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

    # Documento RTF
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