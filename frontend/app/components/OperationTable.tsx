"use client";

import { useState } from "react";
import { FaUser, FaClock, FaCopy } from "react-icons/fa";
import { formatDateTime } from "../utils/dataUtils";

interface Operation {
    operador: string;
    horario: string;
    email: string;
    telefone: string;
    cpf: string;
    nascimento: string;
    nome: string;
    sobrenome: string;
    renda: string;
    status: "Criar" | "Criada" | "Recusada";
}

interface OperationTableProps {
    data?: Operation[];
}

export default function OperationTable({ data = [] }: OperationTableProps) {
    const [operations, setOperations] = useState<Operation[]>(data);
    const [copiedField, setCopiedField] = useState<string | null>(null);

    // Função para copiar valor para a área de transferência
    const copyToClipboard = (value: string, field: string) => {
        navigator.clipboard.writeText(value);
        setCopiedField(field);
        setTimeout(() => setCopiedField(null), 1000);
    };

    // Atualizar status e horário
    const updateStatus = (index: number, newStatus: "Criar" | "Criada" | "Recusada") => {
        const updatedOperations = [...operations];
        updatedOperations[index].status = newStatus;
        updatedOperations[index].horario = formatDateTime();
        setOperations(updatedOperations);
    };

    return (
        <div className="w-full h-full overflow-auto p-6">
            <table className="w-full border-collapse bg-gray-900 dark:bg-gray-800 shadow-lg rounded-lg text-white">
                <thead className="bg-gray-700 dark:bg-gray-900 text-white uppercase font-bold text-lg">
                    <tr>
                        {["Operador / Horário", "Email", "Telefone", "CPF", "Data de Nascimento", "Nome", "Sobrenome", "Renda", "Status"].map((header) => (
                            <th key={header} className="p-4 border border-gray-600 text-left">{header}</th>
                        ))}
                    </tr>
                </thead>
                <tbody>
                    {operations.length > 0 ? (
                        operations.map((item, index) => (
                            <tr
                                key={index}
                                className={`border-t border-gray-700 text-gray-200 transition duration-300 ${item.status === "Criada" ? "bg-green-900" :
                                    item.status === "Recusada" ? "bg-red-900" : "bg-gray-800"
                                    }`}
                            >
                                {/* Operador */}
                                <td className="p-4 flex items-center gap-2">
                                    <FaUser className="text-gray-400" />
                                    <span>{item.operador}</span>
                                </td>

                                {/* Horário */}
                                <td className="p-4 flex items-center gap-2">
                                    <FaClock className="text-gray-400" />
                                    <span>{item.horario}</span>
                                </td>

                                {/* Email */}
                                <td className="p-4">
                                    <span>{item.email}</span>
                                    <button
                                        onClick={() => copyToClipboard(item.email, `email-${index}`)}
                                        className={`pl-4 text-gray-500 hover:text-indigo-500 transition ${copiedField === `email-${index}` ? "text-green-500" : ""
                                            }`}
                                        title="Copiar"
                                    >
                                        <FaCopy />
                                    </button>
                                </td>

                                {/* Telefone */}
                                <td className="p-4">
                                    <span>{item.telefone}</span>
                                    <button
                                        onClick={() => copyToClipboard(item.telefone, `telefone-${index}`)}
                                        className={`pl-4 text-gray-500 hover:text-indigo-500 transition ${copiedField === `telefone-${index}` ? "text-green-500" : ""
                                            }`}
                                        title="Copiar"
                                    >
                                        <FaCopy />
                                    </button>
                                </td>

                                {/* CPF */}
                                <td className="p-4">
                                    <span>{item.cpf}</span>
                                    <button
                                        onClick={() => copyToClipboard(item.cpf, `cpf-${index}`)}
                                        className={`pl-4 text-gray-500 hover:text-indigo-500 transition ${copiedField === `cpf-${index}` ? "text-green-500" : ""
                                            }`}
                                        title="Copiar"
                                    >
                                        <FaCopy />
                                    </button>
                                </td>

                                {/* Data de Nascimento */}
                                <td className="p-4">
                                    <span>{item.nascimento}</span>
                                    <button
                                        onClick={() => copyToClipboard(item.nascimento, `nascimento-${index}`)}
                                        className={`pl-4 text-gray-500 hover:text-indigo-500 transition ${copiedField === `nascimento-${index}` ? "text-green-500" : ""
                                            }`}
                                        title="Copiar"
                                    >
                                        <FaCopy />
                                    </button>
                                </td>


                                {/* Nome */}
                                <td className="p-4">
                                    <span>{item.nome}</span>
                                    <button
                                        onClick={() => copyToClipboard(item.nome, `nome-${index}`)}
                                        className={`pl-4 text-gray-500 hover:text-indigo-500 transition ${copiedField === `nome-${index}` ? "text-green-500" : ""
                                            }`}
                                        title="Copiar"
                                    >
                                        <FaCopy />
                                    </button>
                                </td>

                                {/* Nome */}
                                <td className="p-4">
                                    <span>{item.sobrenome}</span>
                                    <button
                                        onClick={() => copyToClipboard(item.sobrenome, `sobrenome-${index}`)}
                                        className={`pl-4 text-gray-500 hover:text-indigo-500 transition ${copiedField === `sobrenome-${index}` ? "text-green-500" : ""
                                            }`}
                                        title="Copiar"
                                    >
                                        <FaCopy />
                                    </button>
                                </td>


                                {/* Renda */}
                                <td className="p-4">
                                    <span>{item.renda}</span>
                                    <button
                                        onClick={() => copyToClipboard(item.renda, `renda-${index}`)}
                                        className={`text-gray-500 pl-4 hover:text-indigo-500 transition ${copiedField === `renda-${index}` ? "text-green-500" : ""
                                            }`}
                                        title="Copiar"
                                    >
                                        <FaCopy />
                                    </button>
                                </td>

                                {/* Status Dropdown */}
                                <td className="p-4">
                                    <select
                                        value={item.status}
                                        onChange={(e) => updateStatus(index, e.target.value as "Criar" | "Criada" | "Recusada")}
                                        className={`px-3 py-1 rounded-md text-white cursor-pointer ${item.status === "Criar" ? "bg-blue-500" :
                                            item.status === "Criada" ? "bg-green-500" : "bg-red-500"
                                            }`}
                                    >
                                        <option value="Criar">Criar</option>
                                        <option value="Criada">Criada</option>
                                        <option value="Recusada">Recusada</option>
                                    </select>
                                </td>
                            </tr>
                        ))
                    ) : (
                        <tr>
                            <td colSpan={10} className="p-4 text-center text-gray-400">
                                Nenhum dado encontrado.
                            </td>
                        </tr>
                    )}
                </tbody>

            </table>
        </div>
    );
}
