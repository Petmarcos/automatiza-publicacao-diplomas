import React, { useState } from 'react';

const API_URL = import.meta.env.VITE_API_URL || "https://automatiza-publicacao-api.onrender.com";

const MESES = [
  "janeiro", "fevereiro", "março", "abril", "maio", "junho",
  "julho", "agosto", "setembro", "outubro", "novembro", "dezembro"
];

export default function App() {
  const [fileDigitais, setFileDigitais] = useState(null);
  const [fileEmitidos, setFileEmitidos] = useState(null);
  const [nomeReitor, setNomeReitor] = useState("Mary Roberta Meira Marinho");
  const [cargoReitor, setCargoReitor] = useState("Reitora");
  
  // Seleciona por padrão o mês atual do sistema (Agosto)
  const mesAtualNome = MESES[new Date().getMonth()];
  const [mesReferencia, setMesReferencia] = useState(mesAtualNome);

  const [carregando, setCarregando] = useState(false);
  const [dadosProcessados, setDadosProcessados] = useState(null);

  const handleProcessar = async () => {
    if (!fileDigitais || !fileEmitidos) {
      alert("Por favor, selecione ambos os arquivos (.xls) antes de continuar.");
      return;
    }

    setCarregando(true);
    const formData = new FormData();
    formData.append("file_digitais", fileDigitais);
    formData.append("file_emitidos", fileEmitidos);
    formData.append("nome_reitor", nomeReitor);
    formData.append("cargo_reitor", cargoReitor);
    formData.append("mes_referencia", mesReferencia); // Envia o mês selecionado para a API

    try {
      const response = await fetch(`${API_URL}/api/processar-diplomas`, {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || "Erro ao processar as planilhas.");
      }

      const data = await response.json();
      setDadosProcessados(data);
    } catch (error) {
      alert(error.message);
    } finally {
      setCarregando(false);
    }
  };

  const baixarRTF = () => {
    if (!dadosProcessados || !dadosProcessados.previa_texto_rtf) return;
    const blob = new Blob([dadosProcessados.previa_texto_rtf], { type: "text/rtf" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = `Aviso_de_Registro_de_Diplomas_${mesReferencia}.rtf`;
    link.click();
  };

  const baixarExcel = () => {
    window.location.href = `${API_URL}/api/download-excel`;
  };

  return (
    <div className="min-h-screen bg-gray-50 p-8 font-sans text-gray-800">
      <header className="mb-8 border-b-4 border-green-600 bg-white p-6 shadow-sm text-center">
        <h1 className="text-2xl font-bold text-gray-900 tracking-wide uppercase">
          Instituto Federal de Educação, Ciência e Tecnologia da Paraíba - IFPB
        </h1>
        <p className="text-sm text-gray-500 font-medium">
          Diretoria de Cadastro Acadêmico, Certificação e Diplomação
        </p>
        <p className="text-sm text-gray-500 font-medium">
          Melhoria de processo para uso interno da DCACD-PRE/IFPB em conformidade com a Portaria MEC nº 1.095 de 25 de outubro de 2018
        </p>
      </header>

      {!dadosProcessados ? (
        <main className="max-w-2xl mx-auto bg-white p-8 rounded-xl shadow-md border border-gray-100">
          <h2 className="text-lg font-semibold mb-6 text-gray-700">
            Upload das Planilhas de Origem e Configurações
          </h2>
          
          <div className="space-y-6">
            {/* CONFIGURAÇÕES DE MÊS, REITOR E CARGO */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 bg-gray-50 p-4 rounded-lg border border-gray-200">
              <div className="md:col-span-1">
                <label className="block text-xs font-semibold uppercase text-gray-600 mb-1">
                  Mês de Referência
                </label>
                <select
                  value={mesReferencia}
                  onChange={(e) => setMesReferencia(e.target.value)}
                  className="w-full text-sm border rounded-md p-2 bg-white text-gray-800 border-gray-300 focus:outline-none focus:ring-2 focus:ring-green-500 capitalize"
                >
                  {MESES.map((m) => (
                    <option key={m} value={m}>{m}</option>
                  ))}
                </select>
              </div>

              <div className="md:col-span-1">
                <label className="block text-xs font-semibold uppercase text-gray-600 mb-1">
                  Nome do(a) Reitor(a)
                </label>
                <input
                  type="text"
                  value={nomeReitor}
                  onChange={(e) => setNomeReitor(e.target.value)}
                  className="w-full text-sm border rounded-md p-2 bg-white text-gray-800 border-gray-300 focus:outline-none focus:ring-2 focus:ring-green-500"
                  required
                />
              </div>

              <div className="md:col-span-1">
                <label className="block text-xs font-semibold uppercase text-gray-600 mb-1">
                  Cargo do Signatário
                </label>
                <input
                  type="text"
                  value={cargoReitor}
                  onChange={(e) => setCargoReitor(e.target.value)}
                  className="w-full text-sm border rounded-md p-2 bg-white text-gray-800 border-gray-300 focus:outline-none focus:ring-2 focus:ring-green-500"
                  required
                />
              </div>
            </div>

            {/* SELEÇÃO DE ARQUIVOS EXCEL/XLS */}
            <div>
              <label className="block text-sm font-semibold text-gray-600 mb-2">
                1. Diplomas Digitais (digitais.xls)
              </label>
              <input
                type="file"
                accept=".xls,.xlsx"
                onChange={(e) => setFileDigitais(e.target.files[0])}
                className="w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-md file:border-0 file:text-sm file:font-semibold file:bg-green-50 file:text-green-700 hover:file:bg-green-100 cursor-pointer border rounded-md p-2"
              />
            </div>

            <div>
              <label className="block text-sm font-semibold text-gray-600 mb-2">
                2. Diplomas Emitidos (emitidos_2026.xls)
              </label>
              <input
                type="file"
                accept=".xls,.xlsx"
                onChange={(e) => setFileEmitidos(e.target.files[0])}
                className="w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-md file:border-0 file:text-sm file:font-semibold file:bg-green-50 file:text-green-700 hover:file:bg-green-100 cursor-pointer border rounded-md p-2"
              />
            </div>
            
            <button
              onClick={handleProcessar}
              disabled={carregando}
              className="w-full mt-4 bg-green-600 text-white font-bold py-3 px-4 rounded-md hover:bg-green-700 transition duration-200 disabled:bg-gray-400"
            >
              {carregando ? "Processando..." : "Gerar Prévias dos Documentos"}
            </button>
          </div>
        </main>
      ) : (
        /* TELA DE RESULTADOS */
        <main className="max-w-6xl mx-auto space-y-8">
          <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-100">
            <h3 className="text-xl font-bold mb-6 text-gray-800 border-b pb-2">
              Processamento Concluído (Mês: {mesReferencia})
            </h3>

            {dadosProcessados.alertas && dadosProcessados.alertas.length > 0 && (
              <div className="mb-6 p-4 bg-amber-50 border-l-4 border-amber-500 rounded-r-md text-amber-900">
                <h4 className="font-bold mb-2 flex items-center gap-2">
                  ⚠️ Alertas de Consistência ({dadosProcessados.alertas.length})
                </h4>
                <ul className="list-disc list-inside text-sm space-y-1">
                  {dadosProcessados.alertas.map((alerta, index) => (
                    <li key={index}>{alerta.mensagem}</li>
                  ))}
                </ul>
              </div>
            )}

            {dadosProcessados.resumo_livros && (
              <div className="mb-6 bg-gray-50 p-4 rounded-lg border border-gray-200">
                <h4 className="font-bold text-gray-800 mb-3 text-sm uppercase tracking-wider">
                  Resumo do Lote Processado
                </h4>
                <div className="overflow-x-auto">
                  <table className="min-w-full text-sm border-collapse bg-white rounded-md overflow-hidden shadow-sm">
                    <thead>
                      <tr className="bg-gray-200 text-gray-700 text-left">
                        <th className="p-3 border-b">Livro</th>
                        <th className="p-3 border-b text-center">Quantidade de Registros</th>
                        <th className="p-3 border-b text-right">Intervalo</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-gray-100">
                      {dadosProcessados.resumo_livros.map((item, index) => (
                        <tr key={index} className="hover:bg-gray-50">
                          <td className="p-3 font-semibold text-gray-800">{item.livro}</td>
                          <td className="p-3 text-center">{item.quantidade}</td>
                          <td className="p-3 text-right text-gray-600 font-mono">{item.intervalo}</td>
                        </tr>
                      ))}
                      <tr className="bg-gray-100 font-bold text-gray-900 border-t-2 border-gray-300">
                        <td className="p-3">Total</td>
                        <td className="p-3 text-center">{dadosProcessados.total_geral}</td>
                        <td className="p-3 text-right">-</td>
                      </tr>
                    </tbody>
                  </table>
                </div>
              </div>
            )}

            {dadosProcessados.previa_html && (
              <div className="mb-6 p-4 bg-white border rounded-md max-h-96 overflow-y-auto shadow-inner">
                <h4 className="font-bold mb-4 text-gray-900 underline">Prévia do Documento Oficial:</h4>
                <div dangerouslySetInnerHTML={{ __html: dadosProcessados.previa_html }} />
              </div>
            )}

            <div className="flex gap-4 pt-4 border-t">
              <button
                onClick={baixarRTF}
                className="bg-blue-600 text-white py-2.5 px-5 rounded-md font-semibold hover:bg-blue-700 transition shadow-sm"
              >
                Baixar RTF
              </button>
              <button
                onClick={baixarExcel}
                className="bg-green-600 text-white py-2.5 px-5 rounded-md font-semibold hover:bg-green-700 transition shadow-sm"
              >
                Baixar Excel
              </button>
            </div>
          </div>

          <div className="text-center">
            <button
              onClick={() => setDadosProcessados(null)}
              className="text-sm font-semibold text-gray-500 hover:text-gray-700 underline"
            >
              ← Voltar e Processar Novas Planilhas
            </button>
          </div>
        </main>
      )}
    </div>
  );
}