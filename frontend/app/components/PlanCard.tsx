"use client";

import { FiCheckCircle, FiClock, FiXCircle } from "react-icons/fi";
import Link from "next/link";

interface PlanCardProps {
  name: string;
  status: "ativo" | "expirado" | "pendente" | "disponível";
  renewalDate?: string;
  features: string[];
  upgradeUrl?: string;
}

export default function PlanCard({
  name,
  status,
  renewalDate,
  features,
  upgradeUrl,
}: PlanCardProps) {
  const statusInfo = {
    ativo: { color: "text-green-600", icon: <FiCheckCircle size={28} /> },
    expirado: { color: "text-red-600", icon: <FiXCircle size={28} /> },
    pendente: { color: "text-yellow-600", icon: <FiClock size={28} /> },
    disponível: { color: "text-indigo-600", icon: <FiCheckCircle size={28} /> },
  };

  return (
    <div className="w-full bg-white dark:bg-gray-800 p-6 rounded-lg shadow-lg text-gray-900 dark:text-white transition-all duration-300 hover:shadow-xl hover:scale-105 transform">
      <h2 className="text-2xl font-semibold text-center mb-4">
        {status === "disponível" ? "Plano Disponível" : "🎟️ Seu Plano Atual"}
      </h2>

      {/* Status do Plano */}
      <div
        className={`p-4 rounded-md flex items-center gap-3 ${statusInfo[status].color} bg-opacity-20`}
      >
        <div className="p-2 rounded-full bg-opacity-10">{statusInfo[status].icon}</div>
        <div>
          <h3 className="text-xl font-semibold capitalize">{name}</h3>
          {renewalDate && (
            <p className="text-sm text-gray-600 dark:text-gray-400">
              Renovação: <strong>{renewalDate}</strong>
            </p>
          )}
        </div>
      </div>

      {/* Benefícios do Plano */}
      <h3 className="text-xl font-semibold mt-6 mb-4">✅ Benefícios:</h3>
      <ul className="list-none space-y-2">
        {features.map((feature, index) => (
          <li key={index} className="flex items-center gap-2">
            <FiCheckCircle size={18} className="text-green-500" />
            {feature}
          </li>
        ))}
      </ul>

      {/* Botão de Upgrade */}
      {upgradeUrl && (
        <Link
          href={upgradeUrl}
          className="mt-4 block bg-gradient-to-r from-indigo-600 to-purple-600 text-white text-center py-3 rounded-lg hover:from-indigo-700 hover:to-purple-700 transition-all duration-300 transform hover:scale-105 shadow-md"
        >
          Escolher Plano
        </Link>
      )}
    </div>
  );
}
