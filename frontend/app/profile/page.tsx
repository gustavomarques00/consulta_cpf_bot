"use client";

import { useState } from "react";
import { useForm } from "react-hook-form";
import Link from "next/link";
import { useRouter } from "next/navigation";
import axios from "axios";

interface LoginForm {
  username: string;
  password: string;
}

export default function LoginPage() {
  const router = useRouter();
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState<boolean>(false);

  const { register, handleSubmit, formState: { errors } } = useForm<LoginForm>();

  const onSubmit = async (data: LoginForm) => {
    setLoading(true);
    setError(null);

    try {
      // Simulação de autenticação via API (substituir por backend real)
      const response = await axios.post("/api/auth/login", data);

      if (response.status === 200) {
        // Redireciona para o painel após login bem-sucedido
        router.push("/dashboard");
      } else {
        setError("Credenciais inválidas. Tente novamente.");
      }
    } catch (err) {
      setError("Erro ao autenticar. Verifique suas credenciais.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex min-h-screen items-center justify-center bg-gray-100 dark:bg-gray-900">
      <div className="w-full max-w-md bg-white dark:bg-gray-800 p-6 rounded-lg shadow-lg">
        <h2 className="text-2xl font-semibold text-center mb-4 text-gray-900 dark:text-white">
          Login
        </h2>

        {error && <p className="text-red-500 text-center">{error}</p>}

        <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
          {/* Campo de Usuário */}
          <div>
            <label className="block text-gray-700 dark:text-gray-300">Usuário</label>
            <input
              type="text"
              {...register("username", { required: "Usuário é obrigatório" })}
              className="w-full px-4 py-2 rounded-md border border-gray-300 dark:border-gray-600 dark:bg-gray-700 dark:text-white focus:outline-none focus:ring-2 focus:ring-indigo-500"
              placeholder="Digite seu usuário"
            />
            {errors.username && <p className="text-red-500">{errors.username.message}</p>}
          </div>

          {/* Campo de Senha */}
          <div>
            <label className="block text-gray-700 dark:text-gray-300">Senha</label>
            <input
              type="password"
              {...register("password", { required: "Senha é obrigatória" })}
              className="w-full px-4 py-2 rounded-md border border-gray-300 dark:border-gray-600 dark:bg-gray-700 dark:text-white focus:outline-none focus:ring-2 focus:ring-indigo-500"
              placeholder="Digite sua senha"
            />
            {errors.password && <p className="text-red-500">{errors.password.message}</p>}
          </div>

          {/* Botão de Login */}
          <button
            type="submit"
            disabled={loading}
            className="w-full bg-indigo-600 text-white py-3 rounded-md hover:bg-indigo-700 transition duration-200"
          >
            {loading ? "Entrando..." : "Entrar"}
          </button>
        </form>

        {/* Link para o Telegram caso o usuário não tenha conta */}
        <div className="text-center mt-4">
          <p className="text-gray-600 dark:text-gray-300">Ainda não tem conta?</p>
          <Link
            href="https://t.me/seu_bot_de_vendas"
            target="_blank"
            className="text-indigo-600 dark:text-indigo-400 hover:underline"
          >
            Acesse nosso bot no Telegram
          </Link>
        </div>
      </div>
    </div>
  );
}
