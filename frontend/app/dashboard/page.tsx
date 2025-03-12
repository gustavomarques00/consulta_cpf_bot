"use client";

import { useEffect, useState } from "react";
import axios from "axios";
import { Bar } from "react-chartjs-2";
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
} from "chart.js";

// Registrar componentes do Chart.js
ChartJS.register(CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend);

interface CPFStats {
  total: number;
  sucesso: number;
  falhas: number;
  pendentes: number;
}

export default function DashboardPage() {
  const [stats, setStats] = useState<CPFStats | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchStats = async () => {
      try {
        const response = await axios.get("/api/cpf-stats"); // Endpoint fictício
        setStats(response.data);
      } catch (err) {
        setError("Erro ao carregar estatísticas.");
      } finally {
        setLoading(false);
      }
    };

    fetchStats();
  }, []);

  if (loading) return <p className="text-center text-lg">Carregando estatísticas...</p>;
  if (error) return <p className="text-center text-red-500">{error}</p>;
  if (!stats) return <p className="text-center">Nenhuma estatística disponível.</p>;

  // Dados para o gráfico de barras
  const chartData = {
    labels: ["Total", "Sucesso", "Falhas", "Pendentes"],
    datasets: [
      {
        label: "CPFs Processados",
        data: [stats.total, stats.sucesso, stats.falhas, stats.pendentes],
        backgroundColor: ["#4f46e5", "#10b981", "#ef4444", "#f59e0b"],
      },
    ],
  };

  return (
    <div className="container mx-auto p-6">
      <h1 className="text-3xl font-bold text-center mb-6">Dashboard de CPFs Processados</h1>

      {/* Estatísticas */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <StatCard label="Total Processados" value={stats.total} color="bg-blue-500" />
        <StatCard label="Com Sucesso" value={stats.sucesso} color="bg-green-500" />
        <StatCard label="Falhas" value={stats.falhas} color="bg-red-500" />
        <StatCard label="Pendentes" value={stats.pendentes} color="bg-yellow-500" />
      </div>

      {/* Gráfico */}
      <div className="mt-8">
        <h2 className="text-2xl font-semibold text-center mb-4">Distribuição dos Processamentos</h2>
        <div className="w-full max-w-lg mx-auto bg-white p-6 rounded-lg shadow-md">
          <Bar data={chartData} />
        </div>
      </div>
    </div>
  );
}

// Componente reutilizável para exibir estatísticas
function StatCard({ label, value, color }: { label: string; value: number; color: string }) {
  return (
    <div className={`p-6 rounded-lg shadow-md text-white ${color}`}>
      <h3 className="text-lg font-semibold">{label}</h3>
      <p className="text-2xl font-bold">{value}</p>
    </div>
  );
}
