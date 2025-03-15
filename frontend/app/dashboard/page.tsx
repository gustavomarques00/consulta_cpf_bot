"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { Tooltip, ResponsiveContainer, BarChart, Bar, XAxis, YAxis, CartesianGrid, Legend } from "recharts";
import { formatDateTime, formatPhone, formatCurrency } from "../utils/dataUtils";

export default function DashboardPage() {
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

  interface WorkHour {
    day: string;
    hours: number;
  }

  const [operations, setOperations] = useState<Operation[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [workHours, setWorkHours] = useState<WorkHour[]>([]);
  const router = useRouter();

  const fetchOperations = async () => {
    setLoading(true);
    setError(null);

    try {
      const token = localStorage.getItem("authToken");
      if (!token) {
        router.push("/login");
        return;
      }

      const response = await fetch("/api/operations", {
        method: "GET",
        headers: {
          Authorization: `Bearer ${token}`,
          "Content-Type": "application/json",
        },
      });

      if (response.status === 401) {
        router.push("/login");
        return;
      }

      if (!response.ok) {
        throw new Error("Erro ao carregar os dados.");
      }

      const data = await response.json();

      // Sanitizando os dados recebidos do backend
      const formattedData = data.map((op: any) => ({
        operador: op.operador?.toString() || "Desconhecido",
        horario: formatDateTime(),
        email: op.email?.toString() || "Não informado",
        telefone: formatPhone(op.telefone) || "Não informado",
        cpf: op.cpf?.toString() || "Não informado",
        nascimento: op.nascimento?.toString() || "Não informado",
        nome: op.nome?.toString() || "Não informado",
        sobrenome: op.sobrenome?.toString() || "Não informado",
        renda: formatCurrency(op.renda) || "0,00",
        status: (["Criar", "Criada", "Recusada"].includes(op.status) ? op.status : "Indefinido") as "Criar" | "Criada" | "Recusada",
      }));

      setOperations(formattedData);
    } catch (err: any) {
      setError(err.message || "Erro desconhecido.");
    } finally {
      setLoading(false);
    }
  };

  const fetchWorkHours = async () => {
    try {
      const token = localStorage.getItem("authToken");
      if (!token) return;

      const response = await fetch("/api/work-hours", {
        method: "GET",
        headers: {
          Authorization: `Bearer ${token}`,
          "Content-Type": "application/json",
        },
      });

      if (!response.ok) {
        throw new Error("Erro ao carregar tempo de trabalho.");
      }

      const workData = await response.json();
      setWorkHours(workData);
    } catch (err) {
      setError("Erro ao carregar tempo de trabalho.");
    }
  };

  useEffect(() => {
    fetchOperations();
    fetchWorkHours();
  }, []);

  // Estatísticas do Dashboard
  const totalOperations = operations.length;
  const statusCounts = {
    Criar: operations.filter((op) => op.status === "Criar").length,
    Criada: operations.filter((op) => op.status === "Criada").length,
    Recusada: operations.filter((op) => op.status === "Recusada").length,
  };

  const totalWorkHours = workHours.reduce((acc, curr) => acc + curr.hours, 0);
  const avgDailyHours = (totalWorkHours / workHours.length).toFixed(1);
  const avgWeeklyHours = (parseFloat(avgDailyHours) * 7).toFixed(1);

  const pieData = [
    { name: "Criar", value: statusCounts.Criar, color: "#FFB400" },
    { name: "Criada", value: statusCounts.Criada, color: "#00C49F" },
    { name: "Recusada", value: statusCounts.Recusada, color: "#FF4D4D" },
  ];

  return (
    <div className="w-screen h-screen bg-gray-900 p-6 flex items-center justify-center">
      <div className="max-w-5xl w-full bg-gray-800 p-6 rounded-lg shadow-lg">
        <h1 className="text-4xl font-bold text-center text-white mb-6">📊 Dashboard</h1>

        {error && <p className="text-red-500 text-center">{error}</p>}

        {loading ? (
          <div className="text-center text-gray-300">
            <div className="w-12 h-12 border-4 border-blue-500 border-t-transparent rounded-full animate-spin mx-auto"></div>
            Carregando dados...
          </div>
        ) : (
          <>
            {/* Cards de estatísticas */}
            <div className="grid grid-cols-3 gap-6 mb-8">
              <div className="bg-gray-700 p-4 rounded-lg text-center">
                <h2 className="text-lg text-gray-300">Total de Operações</h2>
                <p className="text-3xl font-bold text-white">{totalOperations}</p>
              </div>
              <div className="bg-blue-600 p-4 rounded-lg text-center">
                <h2 className="text-lg text-gray-200">Média Diária</h2>
                <p className="text-3xl font-bold text-white">{avgDailyHours}h</p>
              </div>
              <div className="bg-purple-600 p-4 rounded-lg text-center">
                <h2 className="text-lg text-gray-200">Média Semanal</h2>
                <p className="text-3xl font-bold text-white">{avgWeeklyHours}h</p>
              </div>
            </div>

            {/* Gráfico de Tempo de Trabalho */}
            <div className="w-full flex justify-center mb-8">
              <ResponsiveContainer width="100%" height={250}>
                <BarChart data={workHours}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="day" />
                  <YAxis />
                  <Tooltip />
                  <Legend />
                  <Bar dataKey="hours" fill="#4A90E2" />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </>
        )}
      </div>
    </div>
  );
}
