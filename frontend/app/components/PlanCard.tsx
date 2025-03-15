import { FiCheckCircle, FiClock, FiXCircle } from "react-icons/fi";

interface PlanCardProps {
  name: string;
  status: "ativo" | "expirado" | "pendente";
  renewalDate: string;
  features: string[];
}

export default function PlanCard({ name, status, renewalDate, features }: PlanCardProps) {
  const statusInfo = {
    ativo: { color: "text-green-600", icon: <FiCheckCircle size={24} /> },
    expirado: { color: "text-red-600", icon: <FiXCircle size={24} /> },
    pendente: { color: "text-yellow-600", icon: <FiClock size={24} /> },
  };

  return (
    <div className="w-full max-w-3xl bg-white dark:bg-gray-800 p-8 rounded-lg shadow-md text-gray-900 dark:text-white">
      <h2 className="text-2xl font-semibold text-center mb-6">🎟️ Seu Plano Atual</h2>

      {/* Status do Plano */}
      <div className={`p-4 rounded-md flex items-center gap-3 ${statusInfo[status].color} bg-opacity-20`}>
        {statusInfo[status].icon}
        <div>
          <h3 className="text-xl font-semibold capitalize">{name}</h3>
          <p className="text-sm">Status: <strong>{status.toUpperCase()}</strong></p>
          <p className="text-sm">Renovação: <strong>{renewalDate}</strong></p>
        </div>
      </div>

      {/* Benefícios do Plano */}
      <h3 className="text-xl font-semibold mt-6 mb-4">✅ O que você tem acesso:</h3>
      <ul className="list-disc list-inside text-gray-700 dark:text-gray-300 mb-6">
        {features.map((feature, index) => (
          <li key={index} className="flex items-center gap-2">
            <FiCheckCircle size={18} className="text-green-500" />
            {feature}
          </li>
        ))}
      </ul>
    </div>
  );
}
