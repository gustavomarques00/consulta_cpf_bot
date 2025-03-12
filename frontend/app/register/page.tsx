'use client'

import { useState } from "react";
import { useForm, Controller } from "react-hook-form";
import axios from "axios";
import RootLayout from "../layout"; // Importando o layout
import ConfirmPasswordInput from "../components/ConfirmPasswordInput"; // Importando o componente de confirmar senha

interface RegisterFormData {
  email: string;
  password: string;
  confirmPassword: string;
}

// Componente de campo de entrada
const InputField = ({ label, name, type, control, rules, placeholder }: any) => (
  <div>
    <label className="block text-sm font-medium text-gray-700">{label}</label>
    <Controller
      name={name}
      control={control}
      rules={rules}
      render={({ field }) => (
        <input
          type={type}
          {...field}
          className="w-full mt-2 p-3 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
          placeholder={placeholder}
        />
      )}
    />
  </div>
);

// Componente de mensagem de erro
const ErrorMessage = ({ error }: any) => (
  error ? <p className="text-red-500 text-sm">{error.message}</p> : null
);

export default function Register() {
  const [loading, setLoading] = useState<boolean>(false); // Controle de carregamento
  const [error, setError] = useState<string>(""); // Mensagens de erro
  const [success, setSuccess] = useState<string>(""); // Mensagens de sucesso

  // Usando react-hook-form para validação
  const { control, handleSubmit, formState: { errors }, watch } = useForm<RegisterFormData>();

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

  return (
      <div className="min-h-screen bg-gray-50 p-8 flex items-center justify-center">
        <div className="max-w-md w-full bg-white p-8 rounded-lg shadow-md">
          <h1 className="text-3xl font-bold mb-6 text-center">Registrar</h1>

          {/* Formulário de registro */}
          <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
            {/* Campo de Email */}
            <InputField
              label="Email:"
              name="email"
              type="email"
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
            <ErrorMessage error={errors.email} />

            {/* Campo de Senha */}
            <InputField
              label="Senha:"
              name="password"
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
            <ErrorMessage error={errors.password} />

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
                className="w-full bg-indigo-600 text-white py-3 rounded-md hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500"
              >
                {loading ? "Processando..." : "Registrar"}
              </button>
            </div>
          </form>

          {/* Exibir mensagens */}
          {error && <p className="mt-4 text-red-500 text-center">{error}</p>}
          {success && <p className="mt-4 text-green-500 text-center">{success}</p>}

          {/* Link para a página de login */}
          <div className="mt-4 text-center">
            <p>
              Já tem uma conta?{" "}
              <a href="/login" className="text-indigo-600 hover:text-indigo-800">
                Faça login
              </a>
            </p>
          </div>
        </div>
      </div>
  );
}