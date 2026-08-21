import React, { useState } from 'react';

export default function App() {
  const [fileDigitais, setFileDigitais] = useState(null);
  const [fileEmitidos, setFileEmitidos] = useState(null);
  const [nomeReitor, setNomeReitor] = useState("Mary Roberta Meira Marinho");
  const [cargoReitor, setCargoReitor] = useState("Reitora");
  
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
    formData.append("nome_reitor", nomeReitor);
    formData.append("cargo_reitor", cargoReitor);

    try {
      const response = await fetch(`${API_URL}/api/processar`, {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        throw new Error("Erro no processamento das planilhas");
      }

      const data = await response.json();
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

  return (
    <div style={{ maxWidth: '1100px', margin: '30px auto', padding: '0 20px', fontFamily: "'Segoe UI', Roboto, Helvetica, Arial, sans-serif", color: '#1e293b' }}>
      
      {/* CABEÇALHO */}
      <header style={{ borderBottom: '2px solid #e2e8f0', paddingBottom: '15px', marginBottom: '25px' }}>
        <h1 style={{ fontSize: '24px', fontWeight: '700', color: '#0f172a', margin: '0 0 8px 0' }}>Automação de Publicação de Diplomas</h1>
        <p style={{ margin: 0, color: '#64748b', fontSize: '14px' }}>Cruzamento automático de planilhas e geração do Ato Aviso de Registro de Diplomas (ARD).</p>
      </header>

      {/* FORMULÁRIO */}
      <form onSubmit={handleProcessar} style={{ background: '#ffffff', border: '1px solid #cbd5e1', borderRadius: '8px', padding: '24px', boxShadow: '0 1px 3px rgba(0,0,0,0.05)', display: 'grid', gap: '20px' }}>
        
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px' }}>
          <div style={{ background: '#f8fafc', padding: '16px', border: '1px solid #e2e8f0', borderRadius: '6px' }}>
            <label style={{ display: 'block', fontWeight: '600', marginBottom: '8px', fontSize: '14px' }}>Planilha de Digitais (.xlsx / .xls):</label>
            <input type="file" accept=".xlsx, .xls" onChange={(e) => setFileDigitais(e.target.files[0])} required style={{ fontSize: '13px', width: '100%' }} />
          </div>

          <div style={{ background: '#f8fafc', padding: '16px', border: '1px solid #e2e8f0', borderRadius: '6px' }}>
            <label style={{ display: 'block', fontWeight: '600', marginBottom: '8px', fontSize: '14px' }}>Planilha Acumulada de Emitidos (.xlsx / .xls):</label>
            <input type="file" accept=".xlsx, .xls" onChange={(e) => setFileEmitidos(e.target.files[0])} required style={{ fontSize: '13px', width: '100%' }} />
          </div>
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px' }}>
          <div>
            <label style={{ display: 'block', fontWeight: '600', marginBottom: '6px', fontSize: '14px' }}>Nome da Reitoria / Assinatura:</label>
            <input type="text" value={nomeReitor} onChange={(e) => setNomeReitor(e.target.value)} style={{ width: '100%', padding: '10px', border: '1px solid #cbd5e1', borderRadius: '6px', fontSize: '14px' }} />
          </div>

          <div>
            <label style={{ display: 'block', fontWeight: '600', marginBottom: '6px', fontSize: '14px' }}>Cargo do Subscritor:</label>
            <input type="text" value={cargoReitor} onChange={(e) => setCargoReitor(e.target.value)} style={{ width: '100%', padding: '10px', border: '1px solid #cbd5e1', borderRadius: '6px', fontSize: '14px' }} />
          </div>
        </div>

        <button type="submit" disabled={loading} style={{ background: loading ? '#94a3b8' : '#2563eb', color: '#ffffff', fontWeight: '600', fontSize: '15px', padding: '12px 24px', border: 'none', borderRadius: '6px', cursor: loading ? 'not-allowed' : 'pointer', justifySelf: 'start', transition: 'background 0.2s' }}>
          {loading ? "Processando e Cruzando Dados..." : "Processar Planilhas"}
        </button>
      </form>

      {/* RESULTADOS */}
      {resultado && (
        <div style={{ marginTop: '30px', display: 'grid', gap: '25px' }}>
          
          {/* ALERTAS */}
          {resultado.alertas?.map((alerta, idx) => (
            <div key={idx} style={{ background: '#fffbeb', borderLeft: '4px solid #f59e0b', padding: '14px 18px', borderRadius: '0 6px 6px 0', color: '#b45309', fontSize: '14px', fontWeight: '500' }}>
              ⚠️ {alerta.mensagem}
            </div>
          ))}

          {/* DOCUMENTO ARD */}
          <div style={{ background: '#ffffff', border: '1px solid #cbd5e1', borderRadius: '8px', padding: '30px', boxShadow: '0 1px 3px rgba(0,0,0,0.05)' }}>
            <div dangerouslySetInnerHTML={{ __html: resultado.relatorio.previa_html }} />
            
            <div style={{ marginTop: '25px', paddingTop: '15px', borderTop: '1px solid #e2e8f0', display: 'flex', gap: '12px' }}>
              <button onClick={handleDownloadRTF} style={{ background: '#059669', color: '#ffffff', fontWeight: '600', fontSize: '14px', padding: '10px 20px', border: 'none', borderRadius: '6px', cursor: 'pointer', display: 'inline-flex', alignItems: 'center', gap: '8px' }}>
                📄 Baixar Documento Oficial (.RTF)
              </button>
            </div>
          </div>

          {/* TABELA PRÉVIA DA PLANILHA FINAL */}
          {resultado.relatorio?.dados_tabela?.length > 0 && (
            <div style={{ background: '#ffffff', border: '1px solid #cbd5e1', borderRadius: '8px', padding: '24px', boxShadow: '0 1px 3px rgba(0,0,0,0.05)' }}>
              
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
                <h3 style={{ fontSize: '18px', fontWeight: '700', color: '#0f172a', margin: 0 }}>Prévia da Planilha Final Processada</h3>
                
                {/* BOTÃO PARA DOWNLOAD DO EXCEL */}
                <button onClick={handleDownloadExcel} style={{ background: '#16a34a', color: '#ffffff', fontWeight: '600', fontSize: '13px', padding: '8px 16px', border: 'none', borderRadius: '6px', cursor: 'pointer', display: 'inline-flex', alignItems: 'center', gap: '6px' }}>
                  📊 Baixar Planilha Processada (.XLSX)
                </button>
              </div>

              <div style={{ overflowX: 'auto', maxHeight: '420px', border: '1px solid #e2e8f0', borderRadius: '6px' }}>
                <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '13px', textAlign: 'left' }}>
                  <thead>
                    <tr style={{ background: '#f1f5f9', position: 'sticky', top: 0, zIndex: 1 }}>
                      {Object.keys(resultado.relatorio.dados_tabela[0]).map((col) => (
                        <th key={col} style={{ padding: '10px 14px', borderBottom: '2px solid #cbd5e1', color: '#334155', fontWeight: '700', whiteSpace: 'nowrap' }}>{col}</th>
                      ))}
                    </tr>
                  </thead>
                  <tbody>
                    {resultado.relatorio.dados_tabela.map((row, index) => (
                      <tr key={index} style={{ borderBottom: '1px solid #e2e8f0', background: index % 2 === 0 ? '#ffffff' : '#f8fafc' }}>
                        {Object.values(row).map((val, colIdx) => (
                          <td key={colIdx} style={{ padding: '8px 14px', color: '#475569', whiteSpace: 'nowrap' }}>{String(val)}</td>
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
    </div>
  );
}