"use client";

interface StatsPanelProps {
  stats: {
    total: number;
    valid: number;
    invalid: number;
    duplicates: number;
  };
}

export default function StatsPanel({ stats }: StatsPanelProps) {
  return (
    <div className="mt-6 p-4 bg-gray-100 dark:bg-gray-700 rounded-lg">
      <h2 className="text-xl font-semibold text-gray-800 dark:text-white mb-3">Resumo da Operação</h2>
      <p className="text-gray-700 dark:text-gray-300">📂 Total de CPFs no arquivo: <strong>{stats.total}</strong></p>
      <p className="text-green-600 dark:text-green-400">✅ CPFs únicos e válidos: <strong>{stats.valid}</strong></p>
      <p className="text-red-600 dark:text-red-400">⚠️ CPFs inválidos: <strong>{stats.invalid}</strong></p>
      <p className="text-yellow-600 dark:text-yellow-400">🔁 Duplicatas removidas: <strong>{stats.duplicates}</strong></p>
    </div>
  );
}
