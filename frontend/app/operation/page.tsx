"use client";

import { useState, useEffect } from "react";
import OperationTable from "../components/OperationTable";
import { formatDateTime, formatPhone, formatCurrency } from "../utils/dataUtils";
import PopUp from "../components/PopUp"; // Importando o novo componente

export default function OperationPage() {
  const [operations, setOperations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchOperations = async () => {
    try {
      const response = await fetch("/api/operations");
      if (!response.ok) {
        throw new Error("Erro ao carregar os dados");
      }
      const data = await response.json();

      const formattedData = data.map((op: any) => ({
        operador: op.operador,
        horario: formatDateTime(),
        email: op.email,
        telefone: formatPhone(op.telefone),
        cpf: op.cpf,
        nascimento: op.nascimento,
        nome: op.nome,
        sobrenome: op.sobrenome,
        renda: formatCurrency(op.renda),
        status: op.status as "Criar" | "Criada" | "Recusada",
      }));

      setOperations(formattedData);
    } catch (err) {
      setError("Erro ao carregar operações");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchOperations();
  }, []);

  return (
    <div className="w-screen h-screen bg-gray-900 p-0">
      <div className="w-full h-full bg-gray-800 p-8 rounded-lg shadow-lg">
        <h1 className="text-4xl font-bold text-center text-white mb-6">
          📊 Operações em Andamento
        </h1>

        {/* Exibição do PopUp em caso de erro */}
        {error && <PopUp message={error} onClose={() => setError(null)} />}

        {loading ? (
          <p className="text-center text-gray-300">Carregando operações...</p>
        ) : (
          <div className="w-full h-[90%] overflow-auto">
            <OperationTable data={operations} />
          </div>
        )}
      </div>
    </div>
  );
}
