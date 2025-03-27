"use client";

import { useState } from "react";
import axios from "axios"; // Instale axios: npm install axios
import FileUploader from "../components/FileUploader";
import StatsPanel from "../components/StatsPanel";
import CpfList from "../components/CpfList";

export default function SearchPage() {
  const [cpfList, setCpfList] = useState<string[]>([]);
  const [stats, setStats] = useState({ total: 0, valid: 0, invalid: 0, duplicates: 0 });

  const handleFileUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    if (event.target.files?.length) {
      const file = event.target.files[0];

      // Criar um FormData para enviar o arquivo
      const formData = new FormData();
      formData.append("file", file);
      formData.append("source_type", "excel");  // Ou "google_sheets" se o arquivo for de lá

      try {
        // Enviar o arquivo para a rota do backend
        const response = await axios.post("http://localhost:5000/upload-cpf", formData, {
          headers: {
            "Content-Type": "multipart/form-data",
          },
        });

        // Processar a resposta
        const data = response.data;
        setCpfList(data.validCpfs);
        setStats({
          total: data.total,
          valid: data.valid,
          invalid: data.invalid,
          duplicates: data.duplicates,
        });
      } catch (error) {
        console.error("Erro ao enviar o arquivo", error);
        // Trate o erro conforme necessário
      }
    }
  };

  return (
    <div className="flex flex-col items-center justify-center min-h-screen bg-gray-50 dark:bg-gray-900 p-6">
      <div className="w-full max-w-3xl bg-white dark:bg-gray-800 p-8 rounded-lg shadow-lg">
        <h1 className="text-3xl font-bold text-center text-gray-900 dark:text-white mb-6">
          Upload de Arquivo - Busca de CPFs
        </h1>

        {/* Componente de Upload */}
        <FileUploader onFileUpload={handleFileUpload} />

        {/* Componente de Estatísticas */}
        <StatsPanel stats={stats} />

        {/* Componente da Lista de CPFs */}
        {cpfList.length > 0 && <CpfList cpfList={cpfList} />}
      </div>
    </div>
  );
}
