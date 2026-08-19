from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
import io
import pandas as pd 
from typing import Optional

from processador import processar_diplomas
from gerador_relatorios import calcular_resumo_livros, gerar_texto_rtf

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

dados_cache = {}

@app.post("/api/processar-diplomas")
async def api_processar(
    file_digitais: UploadFile = File(...), 
    file_emitidos: UploadFile = File(...),
    nome_reitor: Optional[str] = Form("Mary Roberta Meira Marinho"),
    cargo_reitor: Optional[str] = Form("Reitora")
):
    try:
        conteudo_digitais = io.BytesIO(await file_digitais.read())
        conteudo_emitidos = io.BytesIO(await file_emitidos.read())
        
        # Processa a planilha e extrai os alertas dos alunos sem emitidos
        df_resultado, alertas = processar_diplomas(conteudo_digitais, conteudo_emitidos)
        
        dados_cache["ultimo_resultado"] = df_resultado.copy()
        
        total_geral = len(df_resultado)
        resumo_livros_obj = calcular_resumo_livros(df_resultado)
        
        # Formata o resumo resumido estruturado para a resposta do React
        resumo_json = []
        for row in resumo_livros_obj:
            inicio = int(row.Primeiro_Registro) if not pd.isna(row.Primeiro_Registro) else 0
            fim = int(row.Ultimo_Registro) if not pd.isna(row.Ultimo_Registro) else 0
            resumo_json.append({
                "livro": row.Livro,
                "quantidade": row.Total_Registros,
                "intervalo": f"{inicio} a {fim}" if inicio != fim else f"{inicio}"
            })

        resultado_rtf = gerar_texto_rtf(
            df_resultado, 
            resumo_livros_obj, 
            total_geral, 
            nome_reitor=nome_reitor,
            cargo_reitor=cargo_reitor
        )
        
        return {
            "total_geral": total_geral,
            "previa_texto_rtf": resultado_rtf["rtf"],
            "previa_html": resultado_rtf["html_previa"],
            "previa_tabela": df_resultado.to_dict(orient="records"),
            "alertas": alertas,
            "resumo_livros": resumo_json
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro interno ao processar as planilhas: {str(e)}")

@app.get("/api/download-excel")
async def download_excel():
    if "ultimo_resultado" not in dados_cache:
        raise HTTPException(status_code=400, detail="Nenhum dado processado disponível para download.")
    
    df_exportar = dados_cache["ultimo_resultado"].copy()
    df_exportar = df_exportar.astype(str)
    
    output = io.BytesIO()
    try:
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df_exportar.to_excel(writer, index=False, sheet_name="Listagem Publicacao")
        output.seek(0)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao gerar arquivo Excel: {str(e)}")
    
    return StreamingResponse(
        output,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=Listagem_Publicacao_Diplomas.xlsx"}
    )