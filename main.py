from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response, StreamingResponse
import io
import pandas as pd

from processador import processar_planilhas
from gerador_relatorios import gerar_dados_relatorio

app = FastAPI(title="Automatiza Publicação IFPB")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Cache em memória para o download do Excel
CACHE_EXCEL = {}

@app.post("/api/processar-diplomas")
async def api_processar_diplomas(
    file_digitais: UploadFile = File(...),
    file_emitidos: UploadFile = File(...),
    nome_reitor: str = Form("Mary Roberta Meira Marinho"),
    cargo_reitor: str = Form("Reitora"),
    mes_referencia: str = Form(None)
):
    try:
        content_digitais = await file_digitais.read()
        content_emitidos = await file_emitidos.read()

        # 1. Processa e cruza os dados
        df_final, alertas, buffer_excel = processar_planilhas(
            io.BytesIO(content_digitais),
            io.BytesIO(content_emitidos)
        )

        # Guarda a planilha tratada para o download do Excel
        CACHE_EXCEL["ultimo_excel"] = buffer_excel

        # 2. Gera a prévia do relatório em RTF, HTML e Resumos por Livro
        relatorio = gerar_dados_relatorio(
            df_final,
            nome_reitor=nome_reitor,
            cargo_reitor=cargo_reitor,
            mes_referencia=mes_referencia
        )

        return {
            "total_geral": relatorio["total_geral"],
            "resumo_livros": relatorio["resumo_livros"],
            "alertas": alertas,
            "previa_html": relatorio["previa_html"],
            "previa_texto_rtf": relatorio["previa_texto_rtf"]
        }

    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Erro ao processar planilhas: {str(e)}")


@app.get("/api/download-excel")
async def download_excel():
    if "ultimo_excel" not in CACHE_EXCEL:
        raise HTTPException(status_code=404, detail="Nenhum arquivo processado disponível para download.")
    
    excel_buffer = CACHE_EXCEL["ultimo_excel"]
    excel_buffer.seek(0)
    
    return StreamingResponse(
        excel_buffer,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=Listagem_Publicacao_Diplomas.xlsx"}
    )