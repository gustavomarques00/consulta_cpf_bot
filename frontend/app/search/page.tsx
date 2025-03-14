"use client";

import { useState } from "react";
import { read, utils } from "xlsx";
import FileUploader from "../components/FileUploader";
import StatsPanel from "../components/StatsPanel";
import CpfList from "../components/CpfList";
import { isValidCPF } from "../utils/dataUtils";

export default function SearchPage() {
  const [cpfList, setCpfList] = useState<string[]>([]);
  const [stats, setStats] = useState({ total: 0, valid: 0, invalid: 0, duplicates: 0 });

  const handleFileUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    if (event.target.files?.length) {
      const file = event.target.files[0];

      // Lendo o arquivo XLSX/CSV
      const reader = new FileReader();
      reader.readAsArrayBuffer(file);
      reader.onload = (e) => {
        if (e.target?.result) {
          const workbook = read(new Uint8Array(e.target.result as ArrayBuffer), { type: "array" });
          const sheet = workbook.Sheets[workbook.SheetNames[0]];
          const data = utils.sheet_to_json(sheet, { header: 1 });

          // Extraindo CPFs da primeira coluna
          const extractedCpfs = data
            .slice(1) // Ignorando o cabeçalho
            .map((row: any) => String(row[0]).trim().replace(/\D/g, "")) // Remove caracteres não numéricos
            .filter((cpf) => cpf.length === 11); // Filtra apenas CPFs com 11 dígitos

          // Separando CPFs válidos e inválidos
          const validCpfs = extractedCpfs.filter(isValidCPF);
          const invalidCpfs = extractedCpfs.filter((cpf) => !isValidCPF(cpf));

          // Removendo duplicatas
          const uniqueValidCpfs = Array.from(new Set(validCpfs));

          setCpfList(uniqueValidCpfs);
          setStats({
            total: extractedCpfs.length,
            valid: uniqueValidCpfs.length,
            invalid: invalidCpfs.length,
            duplicates: validCpfs.length - uniqueValidCpfs.length,
          });
        }
      };
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
