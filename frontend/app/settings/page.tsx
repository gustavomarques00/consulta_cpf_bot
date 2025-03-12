"use client";

import { useState, useEffect } from "react";
import { useForm } from "react-hook-form";
import axios from "axios";
import EmailInput from "../components/EmailInput";
import PasswordInput from "../components/PasswordInput";
import InputField from "../components/InputField";
import CheckboxInput from "../components/CheckboxInput";

interface SettingsFormData {
  email: string;
  password: string;
  tema: "claro" | "escuro";
  notificacoes: boolean;
}

export default function Settings() {
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string>("");
  const [successMessage, setSuccessMessage] = useState<string>("");

  const {
    control,
    handleSubmit,
    formState: { errors },
    watch,
    setValue,
  } = useForm<SettingsFormData>();

  // Carregar preferências salvas do usuário
  useEffect(() => {
    const savedTheme = localStorage.getItem("theme") as "claro" | "escuro";
    if (savedTheme) {
      document.documentElement.classList.toggle("dark", savedTheme === "escuro");
      setValue("tema", savedTheme);
    }
  }, [setValue]);

  // Atualizar configurações do usuário
  const onSubmit = async (data: SettingsFormData) => {
    setLoading(true);
    setError("");
    setSuccessMessage("");

    try {
      // Atualizar tema no localStorage
      localStorage.setItem("theme", data.tema);
      document.documentElement.classList.toggle("dark", data.tema === "escuro");

      // Simular requisição para salvar configurações no backend
      await axios.put("/api/settings", data);

      setSuccessMessage("Configurações atualizadas com sucesso!");
    } catch (err) {
      setError("Erro ao atualizar as configurações. Tente novamente.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 p-8 flex items-center justify-center">
      <div className="max-w-md w-full bg-white dark:bg-gray-800 p-8 rounded-lg shadow-md">
        <h1 className="text-3xl font-bold mb-6 text-center text-gray-900 dark:text-white">
          Configurações
        </h1>

        {error && (
          <p className="text-red-500 text-center mb-4" aria-live="assertive">
            {error}
          </p>
        )}

        {successMessage && (
          <p className="text-green-500 text-center mb-4" aria-live="polite">
            {successMessage}
          </p>
        )}

        {/* Formulário de edição de configurações */}
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
            label="Nova Senha"
            name="password"
            control={control}
            rules={{
              required: "A senha é obrigatória",
              minLength: { value: 6, message: "A senha deve ter pelo menos 6 caracteres" },
              pattern: {
                value: /^(?=.*[A-Z])(?=.*[0-9])(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{6,}$/,
                message: "A senha deve conter pelo menos 1 letra maiúscula, 1 número e 1 caractere especial",
              },
            }}
            errors={errors}
            watch={watch}
          />

          {/* Campo de Tema */}
          <InputField
            label="Tema"
            name="tema"
            type="text"
            control={control}
            rules={{
              required: "O tema é obrigatório",
            }}
            errors={errors}
            placeholder="Digite: claro ou escuro"
          />

          {/* Campo de Notificações */}
          <CheckboxInput
            label="Ativar Notificações"
            name="notificacoes"
            control={control}
            rules={{ required: "Você deve escolher uma opção" }}
            errors={errors}
          />

          {/* Botão de Submissão */}
          <button
            type="submit"
            disabled={loading}
            className="w-full bg-indigo-600 text-white py-3 rounded-md hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 transition duration-200"
          >
            {loading ? "Atualizando..." : "Salvar Configurações"}
          </button>
        </form>
      </div>
    </div>
  );
}
