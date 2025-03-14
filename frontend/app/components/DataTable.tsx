"use client";

import { useState } from "react";
import { FaCopy } from "react-icons/fa";
import { formatCurrency, formatPhone } from "../utils/dataUtils";

interface DataTableProps {
  data: {
    email: string;
    telefone: string;
    cpf: string;
    nascimento: string;
    nome: string;
    sobrenome: string;
    renda: string;
    poderAquisitivo: string;
    sexo: string;
    dataHora: string;
    proxy: string;
  }[];
}

export default function DataTable({ data }: DataTableProps) {
  const [copiedField, setCopiedField] = useState<string | null>(null);

  const copyToClipboard = (value: string, field: string) => {
    navigator.clipboard.writeText(value);
    setCopiedField(field);
    setTimeout(() => setCopiedField(null), 1000);
  };

  return (
    <div className="overflow-x-auto mt-6">
      <table className="w-full border-collapse bg-white dark:bg-gray-800 shadow-md rounded-lg">
        <thead className="bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300">
          <tr>
            {[
              "Email", "Telefone", "CPF", "Data de Nascimento", "Nome",
              "Sobrenome", "Renda", "Poder Aquisitivo", "Sexo", "Extraído em", "Proxy"
            ].map((header) => (
              <th key={header} className="p-3 border dark:border-gray-700">{header}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {data.length > 0 ? (
            data.map((item, index) => (
              <tr key={index} className="border-t dark:border-gray-700">
                <td className="p-3 flex items-center gap-2">
                  <span>{item.email}</span>
                  <button onClick={() => copyToClipboard(item.email, `email-${index}`)}
                    className={`text-gray-500 hover:text-indigo-500 transition ${
                      copiedField === `email-${index}` ? "text-green-500" : ""
                    }`}
                    title="Copiar">
                    <FaCopy />
                  </button>
                </td>
                <td className="p-3 flex items-center gap-2">
                  <span>{formatPhone(item.telefone)}</span>
                  <button onClick={() => copyToClipboard(item.telefone, `telefone-${index}`)}
                    className={`text-gray-500 hover:text-indigo-500 transition ${
                      copiedField === `telefone-${index}` ? "text-green-500" : ""
                    }`}
                    title="Copiar">
                    <FaCopy />
                  </button>
                </td>
                <td className="p-3 flex items-center gap-2">
                  <span>{item.cpf}</span>
                  <button onClick={() => copyToClipboard(item.cpf, `cpf-${index}`)}
                    className={`text-gray-500 hover:text-indigo-500 transition ${
                      copiedField === `cpf-${index}` ? "text-green-500" : ""
                    }`}
                    title="Copiar">
                    <FaCopy />
                  </button>
                </td>
                <td className="p-3">{item.nascimento}</td>
                <td className="p-3">{item.nome}</td>
                <td className="p-3">{item.sobrenome}</td>
                <td className="p-3 flex items-center gap-2">
                  <span>{formatCurrency(parseFloat(item.renda.replace(/[^0-9,]/g, "").replace(",", ".")))}</span>
                  <button onClick={() => copyToClipboard(item.renda, `renda-${index}`)}
                    className={`text-gray-500 hover:text-indigo-500 transition ${
                      copiedField === `renda-${index}` ? "text-green-500" : ""
                    }`}
                    title="Copiar">
                    <FaCopy />
                  </button>
                </td>
                <td className="p-3">{item.poderAquisitivo}</td>
                <td className="p-3">{item.sexo}</td>
                <td className="p-3 text-gray-600 dark:text-gray-400">{item.dataHora}</td>
                <td className="p-3">{item.proxy}</td>
              </tr>
            ))
          ) : (
            <tr>
              <td colSpan={11} className="p-3 text-center text-gray-500 dark:text-gray-400">
                Nenhum dado encontrado.
              </td>
            </tr>
          )}
        </tbody>
      </table>
    </div>
  );
}
