import React, { useState } from 'react';

export default function App() {
  const [fileDigitais, setFileDigitais] = useState(null);
  const [fileEmitidos, setFileEmitidos] = useState(null);
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

    try {
      const response = await fetch("http://localhost:8000/api/processar-diplomas", {
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
    const blob = new Blob([dadosProcessados.previa_texto_rtf], { type: "text/rtf" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = "Aviso_de_Registro_de_Diplomas.rtf";
    link.click();
  };

  // 🔥 Chamada para baixar o arquivo Excel do Back-end
  const baixarExcel = () => {
    window.location.href = "http://localhost:8000/api/download-excel";
  };

  return (
    <div className="min-h-screen bg-gray-50 p-8 font-sans text-gray-800">
      
      <header className="mb-8 border-b-4 border-green-600 bg-white p-6 shadow-sm text-center">
        <h1 className="text-2xl font-bold text-gray-900 tracking-wide uppercase">Instituto Capivara Learning</h1>
        <p className="text-sm text-gray-500 font-medium">Diretoria de Cadastro Acadêmico, Certificação e Diplomação</p>
      </header>

      {!dadosProcessados && (
        <main className="max-w-2xl mx-auto bg-white p-8 rounded-xl shadow-md border border-gray-100">
          <h2 className="text-lg font-semibold mb-6 text-gray-700">Upload das Planilhas de Origem</h2>
          
          <div className="space-y-6">
            <div>
              <label className="block text-sm font-semibold text-gray-600 mb-2">
                1. Diplomas Digitais do Mês Anterior (digitais.xls)
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
                2. Todos os Diplomas Emitidos (emitidos_2026.xls)
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
              {carregando ? "Processando e Cruzando Dados com Pandas..." : "Gerar Prévias dos Documentos"}
            </button>
          </div>
        </main>
      )}

      {dadosProcessados && (
        <main className="max-w-6xl mx-auto space-y-8">
          
          {/* SEÇÃO DO RTF */}
          <section className="bg-white p-6 rounded-xl shadow-md border border-gray-200">
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-lg font-bold text-gray-700">Prévia do Aviso de Registro (DOU)</h2>
              <button 
                onClick={baixarRTF} 
                className="bg-blue-600 text-white text-sm font-bold py-2 px-4 rounded hover:bg-blue-700 transition shadow"
              >
                Download do Arquivo .RTF
              </button>
            </div>
            <div className="bg-gray-100 p-4 rounded border font-mono text-xs whitespace-pre-wrap max-h-60 overflow-y-auto leading-relaxed text-gray-700 shadow-inner">
              {dadosProcessados.previa_texto_rtf}
            </div>
          </section>

          {/* SEÇÃO DA LISTAGEM WEB COM SEQUÊNCIA ATUALIZADA */}
          <section className="bg-white p-6 rounded-xl shadow-md border border-gray-200 overflow-x-auto">
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-lg font-bold text-gray-700">Relação de Diplomas para Publicação (Ordem Alfabética)</h2>
              {/* 🔥 BOTÃO PARA BAIXAR O .XLS DA LISTAGEM */}
              <button 
                onClick={baixarExcel} 
                className="bg-green-600 text-white text-sm font-bold py-2 px-4 rounded hover:bg-green-700 transition shadow"
              >
                📥 Baixar Listagem (.xlsx)
              </button>
            </div>
            
            <table className="w-full border-collapse border border-gray-300 text-xs">
              <thead className="bg-gray-100 font-bold uppercase text-gray-700">
                <tr className="text-center">
                  <th className="border border-gray-300 p-2">Nome</th>
                  <th className="border border-gray-300 p-2">CPF</th>
                  <th className="border border-gray-300 p-2">e-MEC</th>
                  <th className="border border-gray-300 p-2">Curso</th>
                  <th className="border border-gray-300 p-2">Ingresso</th>
                  <th className="border border-gray-300 p-2">Conclusão</th>
                  <th className="border border-gray-300 p-2">Homologação</th>
                  <th className="border border-gray-300 p-2">Folha</th>
                  <th className="border border-gray-300 p-2">Livro</th>
                  <th className="border border-gray-300 p-2">Registro</th>
                </tr>
              </thead>
              <tbody>
                {dadosProcessados.previa_tabela.map((row, idx) => (
                  <tr key={idx} className="hover:bg-gray-50 text-center border-b border-gray-200">
                    <td className="border border-gray-300 p-2 font-bold text-left text-gray-900">{row.Aluno}</td>
                    <td className="border border-gray-300 p-2 text-gray-600 tracking-wider">{row.CPF}</td>
                    <td className="border border-gray-300 p-2 text-gray-500">{row["e-MEC"]}</td>
                    <td className="border border-gray-300 p-2 text-left text-gray-800">{row.Curso}</td>
                    <td className="border border-gray-300 p-2 text-gray-600">{row.Ingresso}</td>
                    <td className="border border-gray-300 p-2 text-gray-600">{row.Conclusao}</td>
                    <td className="border border-gray-300 p-2 text-gray-600">{row.Homologacao}</td>
                    <td className="border border-gray-300 p-2 text-gray-500">{row.Folha}</td>
                    <td className="border border-gray-300 p-2 bg-blue-50 font-bold text-blue-900">{row.Livro}</td>
                    <td className="border border-gray-300 p-2 font-bold text-green-700">{row["Registro da homologação"]}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </section>

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