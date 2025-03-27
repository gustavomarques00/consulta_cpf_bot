"use client";  // Este componente será renderizado no cliente

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";  // Usando o hook de roteamento correto
import PlanCard from "../components/PlanCard";

interface Plan {
  id: string;
  nome: string;
  renewalDate: string;
  price: string;
  preco_final: string;  // Adicionando campo 'preco_final'
  features: string[];
}

export default function PlansPage() {
  const [plans, setPlans] = useState<Plan[]>([]);
  const [userPlan, setUserPlan] = useState<string | null>(null);
  const [renewalDate, setRenewalDate] = useState<string | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [isTokenValid, setIsTokenValid] = useState<boolean>(true);  // Verifica se o token é válido
  const router = useRouter();  // Hook de roteamento do cliente

  useEffect(() => {
    const checkUserLogin = () => {
      if (typeof window !== 'undefined') {
        const token = localStorage.getItem("authToken"); // Pegando o token do localStorage
        console.log(token);
        if (token) {
          fetchPlans(token);  // Chama a função para buscar os planos, passando o token
        } else {
          setIsTokenValid(false);  // Marca que o token não é válido
          setLoading(false);  // Termina o loading
        }
      }
    };

    checkUserLogin();  // Verificar login do usuário
  }, []);  // Rodar apenas uma vez quando o componente for montado

  const fetchPlans = async (token: string) => {
    try {
      const plansResponse = await fetch("http://127.0.0.1:5000/api/plans");
      if (!plansResponse.ok) throw new Error("Erro ao carregar os planos.");
      const plansData = await plansResponse.json();
      setPlans(plansData);

      // Verificando o plano do usuário com o token fornecido
      const userResponse = await fetch("http://127.0.0.1:5000/api/user-plans", {
        headers: {
          "Authorization": `Bearer ${token}`,  // Enviar o token como parte do cabeçalho
        },
      });
      console.log(userResponse);

      if (!userResponse.ok) throw new Error("Erro ao carregar seu plano.");
      const userData = await userResponse.json();
      setUserPlan(userData.name); // Armazenando o nome do plano do usuário
      setRenewalDate(userData.renewalDate); // Armazenando a data de renovação
    } catch (err) {
      setError((err as Error).message || "Erro ao carregar os dados.");
    } finally {
      setLoading(false);
    }
  };

  // Exibição do Spinner enquanto carrega
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

  // Se o token for inválido ou ausente, exibe uma mensagem de login
  if (!isTokenValid) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-gray-900 to-gray-800 flex items-center justify-center p-8">
        <div className="max-w-lg w-full bg-red-600 text-white p-6 rounded-lg shadow-lg">
          <p className="text-center text-xl">Você precisa estar logado para acessar os planos.</p>
          <button
            className="mt-4 bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700"
            onClick={() => router.push('/login')}  // Redireciona para a tela de login
          >
            Ir para o Login
          </button>
        </div>
      </div>
    );
  }

  // Exibição de erro
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

        {/* Exibir Plano Atual */}
        {userPlan && (
          <div className="mb-10 bg-blue-600 p-6 rounded-lg shadow-lg border-l-4 border-green-500 hover:shadow-2xl transform hover:scale-105 transition-all duration-300">
            <h2 className="text-2xl font-semibold text-center text-white mb-4">
              🎟️ Seu Plano Atual
            </h2>
            <PlanCard
              nome={userPlan}
              status="Ativo"
              renewalDate={renewalDate || "Não informado"}
              features={["Suporte 24/7", "Acesso completo", "Atualizações gratuitas"]}
            />
          </div>
        )}

        {/* Exibir Planos Disponíveis */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {plans
            .filter((plan) => plan.nome !== userPlan) // Excluir plano atual da lista de escolha
            .map((plan) => (
              <div
                key={plan.id}
                className="transition-transform transform hover:scale-105"
              >
                <PlanCard
                  key={plan.id} // Chave única para cada plano
                  nome={plan.nome}  // Nome do plano
                  features={plan.features || []}  // Garantir que 'features' seja sempre um array
                  price={plan.preco_final}  // Exibe o preço final
                />
              </div>
            ))}
        </div>
      </div>
    </div>
  );
}
