"use client";

import { useEffect, useState } from "react";
import axios from "axios";
import { useRouter } from "next/navigation";
import Link from "next/link";

interface UserPlan {
  name: string;
  features: string[];
  status: "ativo" | "expirado" | "pendente";
  renewalDate: string;
}

export default function Home() {
  const [userPlan, setUserPlan] = useState<UserPlan | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const router = useRouter();

  useEffect(() => {
    const fetchUserPlan = async () => {
      try {
        const response = await axios.get("/api/user-plan");
        setUserPlan(response.data);
      } catch (err) {
        setError("Erro ao carregar os dados do plano.");
      } finally {
        setLoading(false);
      }
    };

    fetchUserPlan();
  }, []);

  if (loading) return <p className="text-center text-lg">Carregando informações...</p>;
  if (error) return <p className="text-center text-red-500">{error}</p>;
  if (!userPlan) return <p className="text-center">Nenhum plano encontrado.</p>;

  const planStatusClass =
    userPlan.status === "ativo"
      ? "text-green-600 bg-green-100"
      : userPlan.status === "expirado"
      ? "text-red-600 bg-red-100"
      : "text-yellow-600 bg-yellow-100";

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 p-8 flex items-center justify-center">
      <div className="max-w-3xl w-full bg-white dark:bg-gray-800 p-8 rounded-lg shadow-md">
        <h1 className="text-3xl font-bold mb-6 text-center text-gray-900 dark:text-white">
          Bem-vindo ao SaaS XYZ 🚀
        </h1>

        {/* Status do Plano */}
        <div className={`p-4 rounded-md mb-6 ${planStatusClass}`}>
          <h2 className="text-xl font-semibold">
            Plano: <span className="capitalize">{userPlan.name}</span>
          </h2>
          <p className="text-sm">
            Status: <strong>{userPlan.status.toUpperCase()}</strong>
          </p>
          <p className="text-sm">
            Renovação: <strong>{userPlan.renewalDate}</strong>
          </p>
        </div>

        {/* Benefícios do Plano */}
        <h2 className="text-2xl font-semibold mb-4 text-gray-900 dark:text-white">O que você tem acesso:</h2>
        <ul className="list-disc list-inside text-gray-700 dark:text-gray-300 mb-6">
          {userPlan.features.map((feature, index) => (
            <li key={index} className="mb-2">{feature}</li>
          ))}
        </ul>

        {/* Ações baseadas no status do plano */}
        {userPlan.status === "expirado" && (
          <div className="text-center">
            <p className="text-red-600 mb-2">Seu plano expirou. Renove para continuar usando nossos serviços.</p>
            <Link
              href="/billing"
              className="bg-red-600 text-white py-3 px-6 rounded-md hover:bg-red-700 transition duration-200"
            >
              Renovar Plano
            </Link>
          </div>
        )}

        {userPlan.status === "pendente" && (
          <div className="text-center">
            <p className="text-yellow-600 mb-2">Seu pagamento ainda está pendente.</p>
            <Link
              href="/support"
              className="bg-yellow-600 text-white py-3 px-6 rounded-md hover:bg-yellow-700 transition duration-200"
            >
              Contatar Suporte
            </Link>
          </div>
        )}

        {userPlan.status === "ativo" && (
          <div className="text-center">
            <p className="text-green-600 mb-2">Tudo certo! Aproveite os recursos do seu plano.</p>
            <Link
              href="/dashboard"
              className="bg-indigo-600 text-white py-3 px-6 rounded-md hover:bg-indigo-700 transition duration-200"
            >
              Acessar Dashboard
            </Link>
          </div>
        )}

        {/* Suporte e Upgrade */}
        <div className="mt-6 flex flex-col sm:flex-row sm:justify-between gap-4">
          <Link
            href="/support"
            className="w-full text-center bg-gray-600 text-white py-3 rounded-md hover:bg-gray-700 transition duration-200"
          >
            Suporte
          </Link>
          <Link
            href="/plans"
            className="w-full text-center bg-blue-600 text-white py-3 rounded-md hover:bg-blue-700 transition duration-200"
          >
            Ver Planos
          </Link>
        </div>
      </div>
    </div>
  );
}