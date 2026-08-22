import React, { useState } from 'react';

export default function App() {
  const [fileDigitais, setFileDigitais] = useState(null);
  const [fileEmitidos, setFileEmitidos] = useState(null);
  
  const [loading, setLoading] = useState(false);
  const [resultado, setResultado] = useState(null);

  const API_URL = "https://automatiza-publicacao-api.onrender.com";

  const handleProcessar = async (e) => {
    e.preventDefault();
    if (!fileDigitais || !fileEmitidos) {
      alert("Selecione ambas as planilhas!");
      return;
    }

    setLoading(true);
    setResultado(null);

    const formData = new FormData();
    formData.append("file_digitais", fileDigitais);
    formData.append("file_emitidos", fileEmitidos);
    formData.append("nome_reitor", "Mary Roberta Meira Marinho");
    formData.append("cargo_reitor", "Reitora");

    try {
      const response = await fetch(`${API_URL}/api/processar`, {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        throw new Error("Erro no processamento das planilhas");
      }

      const data = await response.json();
      console.log("Retorno do Backend:", data); // Inspecionar estrutura no DevTools (F12)
      setResultado(data);
    } catch (err) {
      alert(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleDownloadRTF = () => {
    if (!resultado?.relatorio?.previa_texto_rtf) return;
    const element = document.createElement("a");
    const file = new Blob([resultado.relatorio.previa_texto_rtf], { type: 'text/rtf' });
    element.href = URL.createObjectURL(file);
    element.download = "ATO_AVISO_REGISTRO_DIPLOMAS.rtf";
    document.body.appendChild(element);
    element.click();
    document.body.removeChild(element);
  };

  const handleDownloadExcel = async () => {
    if (!fileDigitais || !fileEmitidos) return;

    const formData = new FormData();
    formData.append("file_digitais", fileDigitais);
    formData.append("file_emitidos", fileEmitidos);

    try {
      const response = await fetch(`${API_URL}/api/download-excel`, {
        method: "POST",
        body: formData,
      });

      if (!response.ok) throw new Error("Erro ao baixar o arquivo Excel");

      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = "Cruzamento_Diplomas_Processado.xlsx";
      document.body.appendChild(a);
      a.click();
      a.remove();
    } catch (err) {
      alert(err.message);
    }
  };

  // Mapeia todas as possíveis chaves que o backend pode usar para retornar pendências/inconsistências
  const registrosSemCorrespondencia = 
    resultado?.relatorio?.sem_correspondencia ||
    resultado?.relatorio?.inconsistencias ||
    resultado?.relatorio?.diplomas_sem_correspondencia ||
    resultado?.sem_correspondencia ||
    resultado?.inconsistencias ||
    resultado?.diplomas_sem_correspondencia ||
    [];

  return (
    <div style={{ backgroundColor: '#f8fafc', minHeight: '100vh', fontFamily: "'Segoe UI', system-ui, -apple-system, sans-serif", paddingBottom: '50px' }}>
      
      {/* CABEÇALHO INSTITUCIONAL DO IFPB */}
      <header style={{ backgroundColor: '#ffffff', paddingTop: '30px', paddingBottom: '20px', textAlign: 'center', borderBottom: '5px solid #00a843' }}>
        <h1 style={{ fontSize: '22px', fontWeight: '800', color: '#000000', margin: '0 0 6px 0', letterSpacing: '0.5px' }}>
          INSTITUTO FEDERAL DE EDUCAÇÃO, CIÊNCIA E TECNOLOGIA DA PARAÍBA - IFPB
        </h1>
        <p style={{ margin: '0 0 4px 0', fontSize: '14px', color: '#4b5563', fontWeight: '500' }}>
          Diretoria de Cadastro Acadêmico, Certificação e Diplomação
        </p>
        <p style={{ margin: 0, fontSize: '13px', color: '#6b7280' }}>
          Melhoria de processo para uso interno da DCACD-PRE/IFPB em conformidade com a Portaria MEC nº 1.095 de 25 de outubro de 2018
        </p>
      </header>

      {/* CONTAINER PRINCIPAL */}
      <main style={{ maxWidth: '850px', margin: '40px auto 0 auto', padding: '0 20px' }}>
        
        {/* CARD DE UPLOAD */}
        <div style={{ backgroundColor: '#ffffff', border: '1px solid #e5e7eb', borderRadius: '12px', padding: '35px 40px', boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.05)' }}>
          <h2 style={{ fontSize: '18px', fontWeight: '600', color: '#374151', marginTop: 0, marginBottom: '25px' }}>
            Upload das Planilhas de Origem
          </h2>

          <form onSubmit={handleProcessar} style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
            
            {/* INPUT 1: DIPLOMAS DIGITAIS */}
            <div>
              <label style={{ display: 'block', fontSize: '14px', color: '#374151', marginBottom: '8px', fontWeight: '500' }}>
                1. Diplomas Digitais (digitais.xls)
              </label>
              <div style={{ border: '1px solid #9ca3af', borderRadius: '6px', padding: '6px 12px', display: 'flex', alignItems: 'center' }}>
                <input 
                  type="file" 
                  accept=".xlsx, .xls" 
                  onChange={(e) => setFileDigitais(e.target.files[0])} 
                  required 
                  style={{ fontSize: '14px', color: '#4b5563', width: '100%', cursor: 'pointer' }} 
                />
              </div>
            </div>

            {/* INPUT 2: DIPLOMAS EMITIDOS */}
            <div>
              <label style={{ display: 'block', fontSize: '14px', color: '#374151', marginBottom: '8px', fontWeight: '500' }}>
                2. Diplomas Emitidos (emitidos_2026.xls)
              </label>
              <div style={{ border: '1px solid #9ca3af', borderRadius: '6px', padding: '6px 12px', display: 'flex', alignItems: 'center' }}>
                <input 
                  type="file" 
                  accept=".xlsx, .xls" 
                  onChange={(e) => setFileEmitidos(e.target.files[0])} 
                  required 
                  style={{ fontSize: '14px', color: '#4b5563', width: '100%', cursor: 'pointer' }} 
                />
              </div>
            </div>

            {/* BOTÃO PRINCIPAL VERDE */}
            <button 
              type="submit" 
              disabled={loading} 
              style={{ 
                backgroundColor: loading ? '#86efac' : '#00a843', 
                color: '#ffffff', 
                fontSize: '16px', 
                fontWeight: '700', 
                padding: '14px', 
                border: 'none', 
                borderRadius: '8px', 
                cursor: loading ? 'not-allowed' : 'pointer', 
                marginTop: '10px',
                transition: 'background-color 0.2s ease' 
              }}
            >
              {loading ? "Processando e Gerando Documentos..." : "Gerar Prévias dos Documentos"}
            </button>
          </form>
        </div>

        {/* ÁREA DE RESULTADOS */}
        {resultado && (
          <div style={{ marginTop: '35px', display: 'flex', flexDirection: 'column', gap: '25px' }}>
            
            {/* ALERTAS GERAIS DA API */}
            {resultado.alertas?.map((alerta, idx) => (
              <div key={idx} style={{ backgroundColor: '#fffbeb', borderLeft: '4px solid #f59e0b', padding: '14px 18px', borderRadius: '0 8px 8px 0', color: '#b45309', fontSize: '14px' }}>
                ⚠️ {alerta.mensagem}
              </div>
            ))}

            {/* 1ª SAÍDA: QUADRO RESUMO DOS REGISTROS POR LIVRO */}
            {resultado.relatorio?.resumo_livros?.length > 0 && (
              <div style={{ backgroundColor: '#ffffff', border: '2px solid #006622', borderRadius: '12px', padding: '30px', boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.05)' }}>
                <h3 style={{ fontSize: '16px', fontWeight: '700', color: '#111827', margin: '0 0 16px 0' }}>
                  Quadro Resumo de Registros por Livro
                </h3>
                
                <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '14px', textAlign: 'left' }}>
                  <thead>
                    <tr style={{ backgroundColor: '#f3f4f6', borderBottom: '2px solid #e5e7eb' }}>
                      <th style={{ padding: '10px 14px', color: '#374151', fontWeight: '700' }}>Livro</th>
                      <th style={{ padding: '10px 14px', color: '#374151', fontWeight: '700', textAlign: 'center' }}>Registros</th>
                      <th style={{ padding: '10px 14px', color: '#374151', fontWeight: '700' }}>Intervalo</th>
                    </tr>
                  </thead>
                  <tbody>
                    {resultado.relatorio.resumo_livros.map((item, index) => (
                      <tr key={index} style={{ borderBottom: '1px solid #e5e7eb', backgroundColor: index % 2 === 0 ? '#ffffff' : '#f9fafb' }}>
                        <td style={{ padding: '10px 14px', color: '#111827', fontWeight: '500' }}>{item.livro}</td>
                        <td style={{ padding: '10px 14px', color: '#111827', textAlign: 'center' }}>{item.quantidade}</td>
                        <td style={{ padding: '10px 14px', color: '#4b5563' }}>{item.intervalo}</td>
                      </tr>
                    ))}
                  </tbody>
                  <tfoot>
                    <tr style={{ backgroundColor: '#f9fafb', borderTop: '2px solid #e5e7eb', fontWeight: '700' }}>
                      <td style={{ padding: '12px 14px', color: '#111827' }}>Total</td>
                      <td style={{ padding: '12px 14px', color: '#111827', textAlign: 'center' }}>{resultado.relatorio.total_geral}</td>
                      <td style={{ padding: '12px 14px' }}></td>
                    </tr>
                  </tfoot>
                </table>
              </div>
            )}

            {/* 2ª SAÍDA: PRÉVIA DO DOCUMENTO ARD */}
            <div style={{ backgroundColor: '#ffffff', border: '2px solid #006622', borderRadius: '12px', padding: '35px', boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.05)' }}>
              <div dangerouslySetInnerHTML={{ __html: resultado.relatorio.previa_html }} />
              
              <div style={{ marginTop: '30px', paddingTop: '20px', borderTop: '1px solid #f3f4f6' }}>
                <button 
                  onClick={handleDownloadRTF} 
                  style={{ backgroundColor: '#00a843', color: '#ffffff', fontWeight: '600', fontSize: '14px', padding: '10px 20px', border: 'none', borderRadius: '6px', cursor: 'pointer' }}
                >
                  📄 Baixar Documento (.RTF)
                </button>
              </div>
            </div>

            {/* ALERTA DE REGISTROS SEM CORRESPONDÊNCIA (FUNDO VERMELHO, LETRAS BRANCAS) */}
            {registrosSemCorrespondencia.length > 0 && (
              <div style={{ backgroundColor: '#dc2626', color: '#ffffff', borderRadius: '12px', padding: '24px 30px', boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)' }}>
                <h4 style={{ margin: '0 0 12px 0', fontSize: '16px', fontWeight: '700', display: 'flex', alignItems: 'center', gap: '8px' }}>
                  ⚠️ Registros em digitais.xls sem correspondentes em emitidos_2026.xls ({registrosSemCorrespondencia.length})
                </h4>
                <p style={{ margin: '0 0 14px 0', fontSize: '13px', color: '#fef2f2' }}>
                  Os seguintes alunos constam na planilha de digitais, mas não foram localizados na planilha de emitidos:
                </p>
                <ul style={{ margin: 0, paddingLeft: '20px', fontSize: '14px', lineHeight: '1.6', fontWeight: '500' }}>
                  {registrosSemCorrespondencia.map((item, idx) => {
                    if (typeof item === 'object' && item !== null) {
                      const matricula = item.matricula || item.MATRICULA || item.Matricula || item['Matrícula'] || item['MATRÍCULA'] || Object.values(item)[0];
                      const nome = item.nome || item.NOME || item.Nome || item['Nome do Aluno'] || item['NOME DO ALUNO'] || Object.values(item)[1];
                      return <li key={idx}>{matricula} - {nome}</li>;
                    }
                    return <li key={idx}>{String(item)}</li>;
                  })}
                </ul>
              </div>
            )}

            {/* 3ª SAÍDA: PRÉVIA DA PLANILHA FINAL PROCESSADA */}
            {resultado.relatorio?.dados_tabela?.length > 0 && (
              <div style={{ backgroundColor: '#ffffff', border: '2px solid #006622', borderRadius: '12px', padding: '30px', boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.05)' }}>
                
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
                  <h3 style={{ fontSize: '16px', fontWeight: '700', color: '#111827', margin: 0 }}>
                    Prévia da Planilha Final Processada
                  </h3>
                  
                  {/* BOTÃO DE DOWNLOAD DO EXCEL */}
                  <button 
                    onClick={handleDownloadExcel} 
                    style={{ backgroundColor: '#15803d', color: '#ffffff', fontWeight: '600', fontSize: '13px', padding: '8px 16px', border: 'none', borderRadius: '6px', cursor: 'pointer' }}
                  >
                    📊 Baixar Planilha Processada (.XLSX)
                  </button>
                </div>

                <div style={{ overflowX: 'auto', maxHeight: '400px', border: '1px solid #e5e7eb', borderRadius: '6px' }}>
                  <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '13px', textAlign: 'left' }}>
                    <thead>
                      <tr style={{ backgroundColor: '#f9fafb', position: 'sticky', top: 0, zIndex: 1 }}>
                        {Object.keys(resultado.relatorio.dados_tabela[0]).map((col) => (
                          <th key={col} style={{ padding: '10px 14px', borderBottom: '2px solid #e5e7eb', color: '#374151', fontWeight: '700', whiteSpace: 'nowrap' }}>
                            {col}
                          </th>
                        ))}
                      </tr>
                    </thead>
                    <tbody>
                      {resultado.relatorio.dados_tabela.map((row, index) => (
                        <tr key={index} style={{ borderBottom: '1px solid #f3f4f6', backgroundColor: index % 2 === 0 ? '#ffffff' : '#f9fafb' }}>
                          {Object.values(row).map((val, colIdx) => (
                            <td key={colIdx} style={{ padding: '8px 14px', color: '#4b5563', whiteSpace: 'nowrap' }}>
                              {String(val)}
                            </td>
                          ))}
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            )}

          </div>
        )}

      </main>
    </div>
  );
}