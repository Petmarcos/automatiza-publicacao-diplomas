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

  return (
    <div style={{ maxWidth: '1000px', margin: '0 auto', padding: '20px', fontFamily: 'sans-serif' }}>
      <h2>Automação de Publicação de Diplomas</h2>

      <form onSubmit={handleProcessar} style={{ display: 'grid', gap: '15px', background: '#f8fafc', padding: '20px', borderRadius: '8px' }}>
        <div>
          <label><strong>Planilha Digitais (.xlsx): </strong></label>
          <input type="file" accept=".xlsx, .xls" onChange={(e) => setFileDigitais(e.target.files[0])} required />
        </div>

        <div>
          <label><strong>Planilha Acumulada Emitidos (.xlsx): </strong></label>
          <input type="file" accept=".xlsx, .xls" onChange={(e) => setFileEmitidos(e.target.files[0])} required />
        </div>

        <div style={{ display: 'flex', gap: '15px' }}>
          <div style={{ flex: 1 }}>
            <label><strong>Nome do Reitor: </strong></label>
            <input type="text" value={nomeReitor} onChange={(e) => setNomeReitor(e.target.value)} style={{ width: '100%', padding: '8px' }} />
          </div>
          <div style={{ flex: 1 }}>
            <label><strong>Cargo: </strong></label>
            <input type="text" value={cargoReitor} onChange={(e) => setCargoReitor(e.target.value)} style={{ width: '100%', padding: '8px' }} />
          </div>
        </div>

        <button type="submit" disabled={loading} style={{ padding: '10px 20px', background: '#2563eb', color: '#fff', border: 'none', borderRadius: '4px', cursor: 'pointer' }}>
          {loading ? "Processando..." : "Processar Planilhas"}
        </button>
      </form>

      {resultado && (
        <div style={{ marginTop: '30px' }}>
          {resultado.alertas?.map((alerta, idx) => (
            <div key={idx} style={{ background: '#fef3c7', borderLeft: '4px solid #f59e0b', padding: '10px', marginBottom: '15px' }}>
              <strong>Aviso: </strong>{alerta.mensagem}
            </div>
          ))}

          {/* DOCUMENTO ARD */}
          <div style={{ background: '#fff', border: '1px solid #ccc', padding: '25px', borderRadius: '4px', boxShadow: '0 2px 4px rgba(0,0,0,0.05)' }}>
            <div dangerouslySetInnerHTML={{ __html: resultado.relatorio.previa_html }} />
            <button onClick={handleDownloadRTF} style={{ marginTop: '20px', padding: '8px 16px', background: '#059669', color: '#fff', border: 'none', borderRadius: '4px', cursor: 'pointer' }}>
              Baixar Documento (.rtf)
            </button>
          </div>

          {/* TABELA PRÉVIA DA PLANILHA FINAL */}
          {resultado.relatorio?.dados_tabela?.length > 0 && (
            <div style={{ marginTop: '40px' }}>
              <h3>Prévia da Planilha Final Processada</h3>
              <div style={{ overflowX: 'auto', maxHeight: '400px', border: '1px solid #e5e7eb' }}>
                <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '13px', textAlign: 'left' }}>
                  <thead>
                    <tr style={{ background: '#f3f4f6', borderBottom: '2px solid #e5e7eb' }}>
                      {Object.keys(resultado.relatorio.dados_tabela[0]).map((col) => (
                        <th key={col} style={{ padding: '10px', border: '1px solid #e5e7eb' }}>{col}</th>
                      ))}
                    </tr>
                  </thead>
                  <tbody>
                    {resultado.relatorio.dados_tabela.map((row, index) => (
                      <tr key={index} style={{ borderBottom: '1px solid #e5e7eb' }}>
                        {Object.values(row).map((val, colIdx) => (
                          <td key={colIdx} style={{ padding: '8px', border: '1px solid #e5e7eb' }}>{String(val)}</td>
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