"use client";

import { useState, useEffect } from "react";
import { useForm } from "react-hook-form";
import axios from "axios";
import InputField from "../components/InputField";
import ConfirmPasswordInput from "../components/ConfirmPasswordInput";
import { FiUser, FiMail, FiPhone, FiBriefcase, FiLock } from "react-icons/fi";

interface RegisterFormData {
  name: string;
  email: string;
  phone: string;
  sector: string;
  password: string;
  confirmPassword: string;
}

export default function Register() {
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string>("");
  const [success, setSuccess] = useState<string>("");
  const [isClient, setIsClient] = useState(false);

  const { control, handleSubmit, formState: { errors }, watch } = useForm<RegisterFormData>();

  useEffect(() => {
    setIsClient(true);
  }, []);

  const onSubmit = async (data: RegisterFormData) => {
    setLoading(true);
    setError("");
    setSuccess("");

    try {
      await axios.post("http://localhost:5000/register", {
        name: data.name,
        email: data.email,
        phone: data.phone,
        sector: data.sector,
        password: data.password,
      });

      setSuccess("Cadastro realizado com sucesso! Você pode fazer login agora.");
    } catch (err: any) {
      setError("Erro ao tentar fazer o registro. Tente novamente.");
    } finally {
      setLoading(false);
    }
  };

  if (!isClient) {
    return null;
  }

  return (
    <div className="min-h-screen bg-gray-900 flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full bg-white p-8 rounded-2xl shadow-2xl transition-all duration-300 hover:shadow-xl">
        <h1 className="text-4xl font-semibold mb-6 text-center text-gray-900">Criar Conta</h1>

        {/* Formulário */}
        <form onSubmit={handleSubmit(onSubmit)} className="space-y-5">
          
          {/* Nome */}
          <div className="relative">
            <InputField
              label="Nome Completo"
              name="name"
              Icon={FiUser}
              control={control}
              errors={errors}
              placeholder="Seu nome completo"
              rules={{ required: "O nome é obrigatório" }}
            />
          </div>

          {/* Email */}
          <div className="relative">
            <InputField
              label="Email"
              name="email"
              type="email"
              control={control}
              Icon={FiMail}
              errors={errors}
              placeholder="email@dominio.com"
              rules={{
                required: "O email é obrigatório",
                pattern: { value: /^[\w-]+@([\w-]+\.)+[\w-]{2,7}$/, message: "Email inválido" },
              }}
            />
          </div>

          {/* Telefone */}
          <div className="relative">
            <InputField
              label="Telefone"
              name="phone"
              type="tel"
              control={control}
              Icon={FiPhone}
              errors={errors}
              placeholder="(11) 99999-9999"
              rules={{
                required: "O telefone é obrigatório",
                pattern: { value: /^\(\d{2}\) \d{4,5}-\d{4}$/, message: "Formato inválido" },
              }}
            />
          </div>

          {/* Setor de Interesse */}
          <div className="relative">
            <InputField
              label="Setor de Interesse"
              name="sector"
              control={control}
              Icon={FiBriefcase}
              errors={errors}
              placeholder="Ex: Marketing, TI, Vendas..."
              rules={{ required: "Informe seu setor de interesse" }}
            />
          </div>

          {/* Senha */}
          <div className="relative">
            <InputField
              label="Senha"
              name="password"
              type="password"
              Icon={FiLock}
              control={control}
              errors={errors}
              placeholder="Senha"
              rules={{ required: "A senha é obrigatória", minLength: { value: 6, message: "Mínimo 6 caracteres" } }}
            />
          </div>

          {/* Confirmar Senha */}
          <div className="relative">
            <ConfirmPasswordInput
              label="Confirmar Senha"
              Icon={FiLock}
              name="confirmPassword"
              control={control}
              errors={errors}
              watch={watch}
              rules={{
                required: "A confirmação de senha é obrigatória",
                validate: (value: string) => value === watch("password") || "As senhas não coincidem",
              }}
            />
          </div>

          {/* Botão */}
          <button 
            type="submit" 
            disabled={loading} 
            className="w-full bg-gradient-to-r from-indigo-500 to-purple-600 text-white py-3 rounded-md hover:from-indigo-600 hover:to-purple-700 transition transform active:scale-95 shadow-md"
          >
            {loading ? "Processando..." : "Registrar"}
          </button>
        </form>

        {/* Exibir mensagens */}
        {error && <p className="text-red-500 text-center mt-4">{error}</p>}
        {success && <p className="text-green-500 text-center mt-4">{success}</p>}
      </div>
    </div>
  );
}
