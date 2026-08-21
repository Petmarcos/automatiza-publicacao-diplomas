from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
import pandas as pd
import io

from processador import processar_planilhas
from gerador_relatorios import gerar_dados_relatorio

app = FastAPI(title="API de Automação de Publicação de Diplomas")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"status": "API operacional"}

@app.post("/api/processar")
async def processar(
    file_digitais: UploadFile = File(...),
    file_emitidos: UploadFile = File(...),
    nome_reitor: str = Form("Mary Roberta Meira Marinho"),
    cargo_reitor: str = Form("Reitora")
):
    try:
        bytes_digitais = io.BytesIO(await file_digitais.read())
        bytes_emitidos = io.BytesIO(await file_emitidos.read())

        df_final, alertas, buffer_excel = processar_planilhas(bytes_digitais, bytes_emitidos)

        dados_relatorio = gerar_dados_relatorio(
            df=df_final,
            nome_reitor=nome_reitor,
            cargo_reitor=cargo_reitor
        )

        return {
            "sucesso": True,
            "alertas": alertas,
            "relatorio": dados_relatorio
        }

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/download-excel")
async def download_excel(
    file_digitais: UploadFile = File(...),
    file_emitidos: UploadFile = File(...)
):
    try:
        bytes_digitais = io.BytesIO(await file_digitais.read())
        bytes_emitidos = io.BytesIO(await file_emitidos.read())

        _, _, buffer_excel = processar_planilhas(bytes_digitais, bytes_emitidos)

        return StreamingResponse(
            buffer_excel,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": "attachment; filename=Cruzamento_Diplomas.xlsx"}
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))