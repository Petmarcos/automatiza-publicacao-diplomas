import pandas as pd
from datetime import datetime
from collections import namedtuple

# ... (Mantenha as funções calcular_resumo_livros e descobrir_mes_referencia como estão) ...

# Renomeei para forçar o Python a ler a nova versão
def gerar_texto_rtf_v2(df_final, resumo_livros, total_geral, mes_referencia, data_assinatura):
    trechos = [f"livro {r.Livro} com {r.Total_Registros} registros numerados no intervalo de {r.Primeiro_Registro} a {r.Ultimo_Registro}" for r in resumo_livros]
    texto_livros_corrido = "; ".join(trechos)
    
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

# --- CHAMADA NO FLUXO PRINCIPAL ---
resumo = calcular_resumo_livros(df_final)
total = df_final.shape[0]
mes, ano = descobrir_mes_referencia(df_final)
mes_ref = f"{mes} de {ano}"
data_ass = datetime.now().strftime("%d de %B de %Y")

# Chamando a V2:
conteudo_rtf = gerar_texto_rtf_v2(df_final, resumo, total, mes_ref, data_ass)