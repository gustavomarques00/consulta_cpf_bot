"use client";

import { useEffect, useState } from "react";
import axios from "axios";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { FiHeadphones, FiTrendingUp } from "react-icons/fi";
import HeroSection from "./components/HeroSection";
import PlanCard from "./components/PlanCard";

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
        const token = localStorage.getItem("authToken");
        if (!token) return;

        const response = await axios.get("/api/user-plan", {
          headers: { Authorization: `Bearer ${token}` },
        });

        setUserPlan(response.data);
      } catch (err) {
        setError("Erro ao carregar os dados do plano.");
      } finally {
        setLoading(false);
      }
    };

    fetchUserPlan();
  }, []);

  return (
    <div className="min-h-screen bg-gray-900 text-white flex flex-col items-center">
      {/* Hero Section */}
      <HeroSection />

      {/* Verificação do Plano */}
      {loading && <p className="text-center text-lg">Carregando informações...</p>}
      {error && <p className="text-center text-red-500">{error}</p>}
      {!loading && !error && userPlan && <PlanCard {...userPlan} />}
      {!loading && !userPlan && (
        <p className="text-center text-lg">Nenhum plano encontrado. <Link href="/plans" className="text-blue-500 underline">Escolha um plano</Link></p>
      )}

      {/* Seção de Planos e Suporte */}
      <div className="mt-10 flex flex-col sm:flex-row sm:justify-center gap-6">
        <Link
          href="/support"
          className="w-full sm:w-[280px] flex items-center justify-center gap-4 bg-gray-700 text-white py-5 px-10 text-xl rounded-xl shadow-lg hover:bg-gray-600 transition-all duration-300 transform hover:scale-105"
        >
          <FiHeadphones size={30} />
          <span className="font-semibold">Suporte</span>
        </Link>

        <Link
          href="/plans"
          className="w-full sm:w-[280px] flex items-center justify-center gap-4 bg-gradient-to-r from-blue-600 to-blue-500 text-white py-5 px-10 text-xl rounded-xl shadow-lg hover:from-blue-700 hover:to-blue-600 transition-all duration-300 transform hover:scale-105"
        >
          <FiTrendingUp size={30} />
          <span className="font-semibold">Ver Planos</span>
        </Link>
      </div>
    </div>
  );
}
