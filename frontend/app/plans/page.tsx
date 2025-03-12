"use client";

import { useEffect, useState } from "react";
import axios from "axios";
import Link from "next/link";

interface Plan {
  id: string;
  name: string;
  price: string;
  features: string[];
}

export default function PlansPage() {
  const [plans, setPlans] = useState<Plan[]>([]);
  const [userPlan, setUserPlan] = useState<string | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchPlans = async () => {
      try {
        const plansResponse = await axios.get("/api/plans");
        setPlans(plansResponse.data);

        const userResponse = await axios.get("/api/user-plan");
        setUserPlan(userResponse.data.name);
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
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 p-8 flex items-center justify-center">
      <div className="max-w-4xl w-full bg-white dark:bg-gray-800 p-8 rounded-lg shadow-md">
        <h1 className="text-3xl font-bold mb-6 text-center text-gray-900 dark:text-white">
          Escolha o Plano Ideal para Você 🚀
        </h1>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {plans.map((plan) => (
            <div
              key={plan.id}
              className={`p-6 border rounded-lg ${
                userPlan === plan.name ? "border-indigo-500 bg-indigo-100 dark:bg-indigo-900" : "border-gray-300"
              }`}
            >
              <h2 className="text-xl font-semibold mb-2 text-gray-900 dark:text-white">
                {plan.name}
              </h2>
              <p className="text-lg font-bold text-gray-700 dark:text-gray-300">{plan.price}</p>

              <ul className="list-disc list-inside text-gray-700 dark:text-gray-300 mt-4">
                {plan.features.map((feature, index) => (
                  <li key={index} className="mb-2">{feature}</li>
                ))}
              </ul>

              {userPlan === plan.name ? (
                <p className="mt-4 text-center text-green-600 font-semibold">Plano Atual</p>
              ) : (
                <Link
                  href={`/checkout?plan=${plan.id}`}
                  className="mt-4 block bg-indigo-600 text-white text-center py-2 rounded-md hover:bg-indigo-700 transition duration-200"
                >
                  Escolher Plano
                </Link>
              )}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
