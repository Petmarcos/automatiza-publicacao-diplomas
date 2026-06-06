import React, { useState } from 'react';

// URL da API com fallback para o Render caso a variável de ambiente falhe
const API_URL = import.meta.env.VITE_API_URL || "https://automatiza-publicacao-api.onrender.com";

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
    link.download = "Aviso_de_Registro_de_Diplomas.rtf";
    link.click();
  };

  const baixarExcel = () => {
    window.location.href = `${API_URL}/api/download-excel`;
  };

  return (
    <div className="min-h-screen bg-gray-50 p-8 font-sans text-gray-800">
      <header className="mb-8 border-b-4 border-green-600 bg-white p-6 shadow-sm text-center">
        <h1 className="text-2xl font-bold text-gray-900 tracking-wide uppercase">Instituto Capivara Learning</h1>
        <p className="text-sm text-gray-500 font-medium">Diretoria de Cadastro Acadêmico, Certificação e Diplomação</p>
      </header>

      {!dadosProcessados ? (
        // TELA DE UPLOAD
        <main className="max-w-2xl mx-auto bg-white p-8 rounded-xl shadow-md border border-gray-100">
          <h2 className="text-lg font-semibold mb-6 text-gray-700">Upload das Planilhas de Origem</h2>
          <div className="space-y-6">
            <div>
              <label className="block text-sm font-semibold text-gray-600 mb-2">1. Diplomas Digitais (digitais.xls)</label>
              <input
                type="file"
                accept=".xls,.xlsx"
                onChange={(e) => setFileDigitais(e.target.files[0])}
                className="w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-md file:border-0 file:text-sm file:font-semibold file:bg-green-50 file:text-green-700 hover:file:bg-green-100 cursor-pointer border rounded-md p-2"
              />
            </div>
            <div>
              <label className="block text-sm font-semibold text-gray-600 mb-2">2. Diplomas Emitidos (emitidos_2026.xls)</label>
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
        // TELA DE RESULTADOS
        <main className="max-w-6xl mx-auto space-y-8">
          <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-100">
            <h3 className="text-xl font-bold mb-4">Processamento Concluído</h3>
                /* Aqui você mantém a lógica de exibição dos resultados */

            /* 1. PRÉVIA DO TEXTO RTF */
            {dadosProcessados.previa_texto_rtf && (
              <div className="mb-6 p-4 bg-gray-50 border rounded-md max-h-60 overflow-y-auto whitespace-pre-wrap text-sm text-gray-700">
                <h4 className="font-bold mb-2 underline">Prévia do Conteúdo (RTF):</h4>
                {dadosProcessados.previa_texto_rtf}
              </div>
            )}

            {/* 2. PRÉVIA DA TABELA (AJUSTE CONFORME O NOME DO CAMPO QUE O SEU BACKEND ENVIA) */}
            {/* Geralmente o campo se chama 'lista_alunos', 'dados' ou 'tabela' */}
            {dadosProcessados.lista_alunos && Array.isArray(dadosProcessados.lista_alunos) && (
              <div className="mb-6 overflow-x-auto">
                <h4 className="font-bold mb-2 underline">Listagem Processada:</h4>
                <table className="min-w-full text-sm border-collapse border border-gray-200">
                  <thead className="bg-gray-100">
                    <tr>
                      {/* Ajuste os nomes das colunas conforme o seu Excel */}
                      <th className="border p-2">Nome</th>
                      <th className="border p-2">CPF</th>
                      <th className="border p-2">e-MEC</th>
                    </tr>
                  </thead>
                  <tbody>
                    {dadosProcessados.lista_alunos.map((aluno, index) => (
                      <tr key={index} className="hover:bg-gray-50">
                        <td className="border p-2">{aluno.nome}</td>
                        <td className="border p-2">{aluno.cpf}</td>
                        <td className="border p-2">{aluno.e-MEC}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}

            <div className="flex gap-4">
              <button onClick={baixarRTF} className="bg-blue-600 text-white py-2 px-4 rounded">Baixar RTF</button>
              <button onClick={baixarExcel} className="bg-green-600 text-white py-2 px-4 rounded">Baixar Excel</button>
            </div>
          </div>

          <div className="text-center">
            <button onClick={() => setDadosProcessados(null)} className="text-sm font-semibold text-gray-500 hover:text-gray-700 underline">
              ← Voltar e Processar Novas Planilhas
            </button>
          </div>
        </main>
      )}
    </div>
  );
}