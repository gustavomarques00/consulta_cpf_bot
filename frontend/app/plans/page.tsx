"use client";

import { useEffect, useState } from "react";
import PlanCard from "../components/PlanCard";

interface Plan {
  id: string;
  name: string;
  price: string;
  features: string[];
}

export default function PlansPage() {
  const [plans, setPlans] = useState<Plan[]>([]);
  const [userPlan, setUserPlan] = useState<string | null>(null);
  const [renewalDate, setRenewalDate] = useState<string | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchPlans = async () => {
      try {
        // **Buscando os planos disponíveis do backend**
        const plansResponse = await fetch("/api/plans");
        if (!plansResponse.ok) throw new Error("Erro ao carregar os planos.");
        const plansData = await plansResponse.json();
        setPlans(plansData);

        // **Buscando o plano do usuário**
        const userResponse = await fetch("/api/user-plan");
        if (!userResponse.ok) throw new Error("Erro ao carregar seu plano.");
        const userData = await userResponse.json();
        setUserPlan(userData.name);
        setRenewalDate(userData.renewalDate);
      } catch (err) {
        setError(err.message || "Erro ao carregar os dados.");
      } finally {
        setLoading(false);
      }
    };

    fetchPlans();
  }, []);

  // **Exibição do Spinner enquanto carrega**
  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-gray-900 to-gray-800 flex items-center justify-center p-8">
        <div className="flex items-center justify-center space-x-2">
          <div className="w-8 h-8 border-4 border-t-4 border-gray-900 border-t-transparent rounded-full animate-spin"></div>
          <span className="text-lg text-gray-300">Carregando planos...</span>
        </div>
      </div>
    );
  }

  // **Exibição de erro**
  if (error) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-gray-900 to-gray-800 flex items-center justify-center p-8">
        <div className="max-w-lg w-full bg-red-600 text-white p-6 rounded-lg shadow-lg">
          <p className="text-center text-xl">{error}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 to-gray-800 p-8 flex flex-col items-center">
      <div className="max-w-5xl w-full bg-white dark:bg-gray-800 p-10 rounded-xl shadow-2xl text-center">
        
        <h1 className="text-4xl font-extrabold text-gray-900 dark:text-white mb-6">
          Escolha o Melhor Plano para Você 🚀
        </h1>

        <p className="text-lg text-gray-700 dark:text-gray-300 mb-8">
          Selecione um dos nossos planos e aproveite os benefícios exclusivos.
        </p>

        {/* **Exibir Plano Atual** */}
        {userPlan && (
          <div className="mb-10 bg-green-100 p-6 rounded-lg shadow-lg border-l-4 border-green-500">
            <h2 className="text-2xl font-semibold text-gray-800 dark:text-white">
              🎟️ Seu Plano Atual
            </h2>
            <PlanCard
              name={userPlan}
              status="ativo"
              renewalDate={renewalDate || "Não informado"}
              features={["Suporte 24/7", "Acesso completo", "Atualizações gratuitas"]}
            />
          </div>
        )}

        {/* **Exibir Planos Disponíveis** */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {plans
            .filter(plan => plan.name !== userPlan) // Excluir plano atual da lista de escolha
            .map((plan) => (
              <div key={plan.id} className="transition-transform transform hover:scale-105">
                <PlanCard
                  name={plan.name}
                  status="disponível"
                  features={plan.features}
                  upgradeUrl={`/checkout?plan=${plan.id}`}
                />
              </div>
            ))}
        </div>
      </div>
    </div>
  );
}
