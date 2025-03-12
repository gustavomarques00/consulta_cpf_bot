"use client";

import { useState } from "react";
import { useForm } from "react-hook-form";
import axios from "axios";
import { useRouter } from "next/navigation";
import Link from "next/link";
import EmailInput from "../components/EmailInput";
import PasswordInput from "../components/PasswordInput";

interface LoginFormData {
  email: string;
  password: string;
}

export default function Login() {
  const router = useRouter();
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string>("");

  const {
    control,
    handleSubmit,
    formState: { errors },
    watch,
  } = useForm<LoginFormData>();

  const onSubmit = async (data: LoginFormData) => {
    setLoading(true);
    setError("");

    try {
      const response = await axios.post("/api/auth/login", data);

      if (response.status === 200) {
        router.push("/dashboard"); // Redireciona para o Dashboard após login bem-sucedido
      } else {
        setError("Email ou senha inválidos.");
      }
    } catch (err) {
      setError("Erro ao tentar fazer login. Verifique suas credenciais.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 p-8 flex items-center justify-center">
      <div className="max-w-md w-full bg-white dark:bg-gray-800 p-8 rounded-lg shadow-md">
        <h1 className="text-3xl font-bold mb-6 text-center text-gray-900 dark:text-white">
          Login
        </h1>

        {error && (
          <p className="text-red-500 text-center mb-4" aria-live="assertive">
            {error}
          </p>
        )}

        {/* Formulário de login */}
        <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
          {/* Campo de Email */}
          <EmailInput
            label="Email"
            name="email"
            control={control}
            rules={{
              required: "O email é obrigatório",
              pattern: {
                value: /^[\w-]+(\.[\w-]+)*@([\w-]+\.)+[a-zA-Z]{2,7}$/,
                message: "Email inválido",
              },
            }}
            errors={errors}
          />

          {/* Campo de Senha */}
          <PasswordInput
            label="Senha"
            name="password"
            control={control}
            rules={{
              required: "A senha é obrigatória",
              minLength: { value: 6, message: "A senha deve ter pelo menos 6 caracteres" },
            }}
            errors={errors}
          />

          {/* Botão de Login */}
          <button
            type="submit"
            disabled={loading}
            className="w-full bg-indigo-600 text-white py-3 rounded-md hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 transition duration-200"
          >
            {loading ? "Processando..." : "Entrar"}
          </button>
        </form>

        {/* Link para Registro */}
        <div className="mt-4 text-center">
          <p className="text-gray-600 dark:text-gray-300">
            Não tem uma conta?{" "}
            <Link href="/register" className="text-indigo-600 hover:text-indigo-800">
              Registre-se
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
}
