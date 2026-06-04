from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
import io
import pandas as pd  # ← ESSA LINHA SE SEGURANÇA QUE ESTAVA FALTANDO!

from processador import processar_diplomas
from gerador_relatorios import calcular_resumo_livros, gerar_texto_rtf

# ... restante do código do seu main.py continua igual ...

app = FastAPI()



from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
import io
import pandas as pd  # ← ESSA LINHA SE SEGURANÇA QUE ESTAVA FALTANDO!

from processador import processar_diplomas
from gerador_relatorios import calcular_resumo_livros, gerar_texto_rtf

# ... restante do código do seu main.py continua igual ...




app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Armazenamento temporário em memória para o download do Excel
dados_cache = {}

@app.post("/api/processar-diplomas")
async def api_processar(file_digitais: UploadFile = File(...), file_emitidos: UploadFile = File(...)):
    try:
        conteudo_digitais = io.BytesIO(await file_digitais.read())
        conteudo_emitidos = io.BytesIO(await file_emitidos.read())
        
        # Processa e ordena alfabeticamente
        df_resultado = processar_diplomas(conteudo_digitais, conteudo_emitidos)
        
        # Salva o dataframe em memória para permitir download posterior
        dados_cache["ultimo_resultado"] = df_resultado.copy()
        
        total_geral = len(df_resultado)
        resumo_livros = calcular_resumo_livros(df_resultado)
        texto_rtf = gerar_texto_rtf(df_resultado, resumo_livros, total_geral)
        
        # Converte para JSON para o React ler
        lista_previa = df_resultado.to_dict(orient="records")
        
        return {
            "total_geral": total_geral,
            "previa_texto_rtf": texto_rtf,
            "previa_tabela": lista_previa
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro interno ao processar as planilhas: {str(e)}")

@app.get("/api/download-excel")
async def download_excel():
    if "ultimo_resultado" not in dados_cache:
        raise HTTPException(status_code=400, detail="Nenhum dado processado disponível para download.")
    
    # Copia os dados para não afetar a tabela da memória viva
    df_exportar = dados_cache["ultimo_resultado"].copy()
    
    # 🔥 Força absolutamente todas as células a irem como formato Texto Puro para o arquivo Excel
    # Isso evita conflito do openpyxl com hífens, datas textuais ou códigos e-MEC
    df_exportar = df_exportar.astype(str)
    
    output = io.BytesIO()
    try:
        # Usa o engine openpyxl de forma explícita e segura
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