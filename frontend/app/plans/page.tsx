"use client";

import { useEffect, useState } from "react";
import axios from "axios";
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
        const plansResponse = await axios.get("/api/plans");
        setPlans(plansResponse.data);

        const userResponse = await axios.get("/api/user-plan");
        setUserPlan(userResponse.data.name);
        setRenewalDate(userResponse.data.renewalDate);
      } catch (err) {
        setError("Erro ao carregar os planos.");
      } finally {
        setLoading(false);
      }
    };

    fetchPlans();
  }, []);

  if (loading) return <p className="text-center text-lg">Carregando planos...</p>;
  if (error) return <p className="text-center text-red-500">{error}</p>;

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 to-gray-800 p-8 flex flex-col items-center">
      <div className="max-w-5xl w-full bg-white dark:bg-gray-800 p-10 rounded-xl shadow-2xl text-center">
        
        <h1 className="text-4xl font-extrabold text-gray-900 dark:text-white mb-6">
          Escolha o Melhor Plano para Você 🚀
        </h1>

        <p className="text-lg text-gray-700 dark:text-gray-300 mb-8">
          Selecione um dos nossos planos e aproveite os benefícios exclusivos.
        </p>

        {/* Exibir Plano Atual */}
        {userPlan && (
          <div className="mb-10">
            <PlanCard
              name={userPlan}
              status="ativo"
              renewalDate={renewalDate || "Não informado"}
              features={["Suporte 24/7", "Acesso completo", "Atualizações gratuitas"]}
            />
          </div>
        )}

        {/* Exibir Planos Disponíveis */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {plans
            .filter(plan => plan.name !== userPlan) // Excluir plano atual da lista de escolha
            .map((plan) => (
              <PlanCard
                key={plan.id}
                name={plan.name}
                status="disponível"
                features={plan.features}
                upgradeUrl={`/checkout?plan=${plan.id}`}
              />
          ))}
        </div>
      </div>
    </div>
  );
}
