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