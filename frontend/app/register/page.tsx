'use client';

import { useState, useEffect } from "react";
import { useForm } from "react-hook-form";
import axios from "axios";
import ConfirmPasswordInput from "../components/ConfirmPasswordInput"; // Importando o componente de confirmar senha
import InputField from "../components/InputField"; // Importando o componente de campo de entrada
import ErrorMessage from "../components/ErrorMessage"; // Importando o componente de mensagem de erro

interface RegisterFormData {
  email: string;
  password: string;
  confirmPassword: string;
}

export default function Register() {
  const [loading, setLoading] = useState<boolean>(false); // Controle de carregamento
  const [error, setError] = useState<string>(""); // Mensagens de erro
  const [success, setSuccess] = useState<string>(""); // Mensagens de sucesso
  const [isClient, setIsClient] = useState(false); // Controle para garantir que a renderização é no cliente

  // Usando react-hook-form para validação
  const { control, handleSubmit, formState: { errors }, watch } = useForm<RegisterFormData>();

  // Usando useEffect para garantir que o código só rode no cliente
  useEffect(() => {
    setIsClient(true); // Após a renderização inicial, estamos no cliente
  }, []);

  // Função de registro ao submeter o formulário
  const onSubmit = async (data: RegisterFormData) => {
    setLoading(true);
    setError(""); // Resetar erro
    setSuccess(""); // Resetar sucesso

    if (data.password !== data.confirmPassword) {
      setError("As senhas não coincidem.");
      setLoading(false);
      return;
    }

    try {
      const response = await axios.post("http://localhost:5000/register", {
        email: data.email,
        password: data.password,
      });

      // Sucesso no registro
      setSuccess("Cadastro realizado com sucesso! Você pode fazer login agora.");
    } catch (err: any) {
      setError("Erro ao tentar fazer o registro. Tente novamente.");
    } finally {
      setLoading(false);
    }
  };

  if (!isClient) {
    return null; // Impede o carregamento da página no lado do servidor, evitando erros de hidratação
  }

  return (
    <div className="min-h-screen bg-gray-100 flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full bg-white p-8 rounded-xl shadow-lg">
        <h1 className="text-3xl font-semibold mb-6 text-center text-gray-900">Registrar</h1>

        {/* Formulário de registro */}
        <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
          {/* Campo de Email */}
          <InputField
            label="Email:"
            name="email"
            type="email"
            errors={errors}
            control={control}
            rules={{
              required: "O email é obrigatório",
              pattern: {
                value: /^[\w-]+(\.[\w-]+)*@([\w-]+\.)+[a-zA-Z]{2,7}$/,
                message: "Email inválido",
              },
            }}
            placeholder="Exemplo: email@dominio.com"
          />
          

          {/* Campo de Senha */}
          <InputField
            label="Senha:"
            name="password"
            errors={errors}
            type="password"
            control={control}
            rules={{
              required: "A senha é obrigatória",
              minLength: {
                value: 6,
                message: "A senha deve ter pelo menos 6 caracteres",
              },
            }}
            placeholder="Sua senha"
          />

          {/* Confirmar Senha */}
          <ConfirmPasswordInput
            label="Confirmar Senha:"
            name="confirmPassword"
            control={control}
            rules={{
              required: "A confirmação de senha é obrigatória",
              
            }}
            errors={errors}
            watch={watch}
          />

          {/* Botão de Submissão */}
          <div>
            <button
              type="submit"
              disabled={loading}
              className="w-full bg-indigo-600 text-white py-3 rounded-md hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 transition ease-in-out duration-300 transform active:scale-95"
            >
              {loading ? "Processando..." : "Registrar"}
            </button>
          </div>
        </form>

        {/* Exibir mensagens */}
        {error && <p className="mt-4 text-red-500 text-center">{error}</p>}
        {success && <p className="mt-4 text-green-500 text-center">{success}</p>}

        {/* Link para a página de login */}
        <div className="mt-6 text-center text-gray-900">
          <p>
            Já tem uma conta?{" "}
            <a href="/login" className="text-indigo-600 hover:text-indigo-800 transition duration-300">
              Faça login
            </a>
          </p>
        </div>
      </div>
    </div>
  );
}
