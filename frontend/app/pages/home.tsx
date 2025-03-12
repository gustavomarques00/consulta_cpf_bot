import { useState } from "react";
import RootLayout from "../layout"; // Importando o layout
import Link from "next/link";

export default function Home() {
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string>("");

  // Função de exemplo de boas-vindas ou ação do usuário
  const handleClick = () => {
    setLoading(true);
    setTimeout(() => {
      setLoading(false);
      setError("Bem-vindo ao Sistema de Autenticação!");
    }, 2000);
  };

  return (
    <RootLayout>
      <div className="min-h-screen bg-gray-50 p-8 flex items-center justify-center">
        <div className="max-w-lg w-full bg-white p-8 rounded-lg shadow-md">
          <h1 className="text-3xl font-bold mb-6 text-center">Bem-vindo ao Sistema de Autenticação</h1>

          <div className="mb-6">
            <p className="text-lg mb-4">Este é o painel de controle onde você pode acessar as funcionalidades do sistema.</p>

            {/* Botões para navegação */}
            <div className="space-y-4">
              <Link
                href="/search"
                className="w-full bg-indigo-600 text-white py-3 rounded-md hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500"
              >
                Buscar CPFs
              </Link>

              <Link
                href="/dashboard"
                className="w-full bg-green-600 text-white py-3 rounded-md hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-green-500"
              >
                Acessar Dashboard
              </Link>

              <Link
                href="/settings"
                className="w-full bg-yellow-600 text-white py-3 rounded-md hover:bg-yellow-700 focus:outline-none focus:ring-2 focus:ring-yellow-500"
              >
                Configurações
              </Link>
            </div>
          </div>

          {/* Mensagem de erro ou sucesso */}
          {error && <p className="mt-4 text-red-500 text-center">{error}</p>}

          {/* Exemplo de ação no botão */}
          <div className="text-center mt-4">
            <button
              onClick={handleClick}
              className="bg-blue-600 text-white py-3 px-6 rounded-md hover:bg-blue-700"
            >
              Teste de Ação
            </button>
          </div>
        </div>
      </div>
    </RootLayout>
  );
}
