// Code: Página de Registro de Usuário

// Ajustar o campo SelectField para aceitar a propriedade onChange
// Adicionar a propriedade onChange ao componente SelectField
// Passar a função onChange para o componente SelectField
// Atualizar o valor do campo código de chefe conforme o tipo de usuário selecionado
// Adicionar a propriedade disabled ao campo de código de chefe
// Desabilitar o campo de código de chefe conforme o tipo de usuário selecionado

'use client';

import React, { useState, useEffect } from "react";
import { useForm } from "react-hook-form";
import axios from "axios";
import SelectField from "../components/SelectField"; // Componente de Seletor
import InputField from "../components/InputField"; // Componente de Input
import ConfirmPasswordInput from "../components/ConfirmPasswordInput"; // Componente de Confirmação de Senha
import PopUp from "../components/PopUp"; // PopUp para mensagens de erro ou sucesso
import { FiUser, FiMail, FiPhone, FiLock, FiKey } from "react-icons/fi"; // Ícones

interface RegisterFormData {
  name: string;
  email: string;
  phone: string;
  tipoUsuario: string;
  password: string;
  confirmPassword: string;
  codigoChefe?: string;
}

export default function Register() {
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string>("");
  const [success, setSuccess] = useState<string>("");
  const [isClient, setIsClient] = useState(false);
  const [showPopUp, setShowPopUp] = useState<boolean>(false);
  const [tipoUsuario, setTipoUsuario] = useState<string>("Chefe de Equipe"); // Definindo Chefe de Equipe como padrão
  const [codigoChefe, setCodigoChefe] = useState<string>("");

  const { control, handleSubmit, formState: { errors }, watch, setValue } = useForm<RegisterFormData>();

  useEffect(() => {
    setIsClient(true); // Define que o cliente está pronto
    setValue("tipoUsuario", "Chefe de Equipe"); // Set default value for tipoUsuario
    setValue("codigoChefe", ""); // Certifique-se de inicializar o campo
  }, [setValue, tipoUsuario]);

  const onSubmit = async (data: RegisterFormData) => {
    setLoading(true);
    setError("");
    setSuccess("");

    try {
      await axios.post("http://localhost:5000/register", {
        name: data.name,
        email: data.email,
        phone: data.phone,
        tipoUsuario: data.tipoUsuario,
        password: data.password,
        codigoChefe: data.codigoChefe,
      });

      setSuccess("Cadastro realizado com sucesso! Você pode fazer login agora.");
      setShowPopUp(true); // Exibe o PopUp de sucesso
    } catch (err: any) {
      setError("Erro ao tentar fazer o registro. Tente novamente.");
      setShowPopUp(true); // Exibe o PopUp de erro
    } finally {
      setLoading(false);
    }
  };

  const handleTipoUsuarioChange = (value: string) => {
    console.log(value); // Verifica o valor selecionado
    setTipoUsuario(value); // Atualiza o estado
    setValue("tipoUsuario", value); // Atualiza o valor no React Hook Form

    // Atualiza o campo código de chefe, se necessário
    if (value === "Chefe de Equipe") {
      const generatedCode = "CE-" + Math.random().toString(36).substring(2, 8).toUpperCase();
      setCodigoChefe(generatedCode);
      setValue("codigoChefe", generatedCode);
    } else {
      setCodigoChefe("");
      setValue("codigoChefe", "");
    }
  };

  if (!isClient) {
    return null;  // Retorna nulo se não for um cliente
  }

  return (
    <div className="min-h-screen bg-gray-900 flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full bg-white p-8 rounded-2xl shadow-2xl transition-all duration-300 hover:shadow-xl">
        <h1 className="text-4xl font-semibold mb-6 text-center text-gray-900">Criar Conta</h1>

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

          {/* Tipo de Usuário */}
          <div className="relative">
            <SelectField
              label="Tipo de Usuário"
              name="tipoUsuario"
              Icon={FiUser}
              control={control}
              errors={errors}
              options={["Operador", "Chefe de Equipe", "Independente"]}
              onChange={handleTipoUsuarioChange} // Passando a função que lida com a mudança
              placeholder="Selecione o tipo de usuário"
            />
            <p className="text-sm text-gray-500 mt-2">
              <strong>Operador:</strong> Precisa inserir o código do chefe de equipe.<br />
              <strong>Chefe de Equipe:</strong> Código gerado automaticamente.<br />
              <strong>Independente:</strong> Não há necessidade de código.
            </p>
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
                validate: (value: string) => value === watch("password") || "As senhas não coincidem"
              }}
            />
          </div>

          {/* Código de Equipe */}
          <div className="relative">
            <InputField
              label="Código do Chefe de Equipe"
              name="codigoChefe"
              control={control}
              errors={errors}
              type="text"
              Icon={FiKey}
              placeholder="Digite o código do chefe de equipe"
              rules={tipoUsuario === "Operador" ? { required: "O código do chefe é obrigatório" } : {}}
              disabled={tipoUsuario === "Independente" || tipoUsuario === "Chefe de Equipe"} // Desabilita para "Independente" ou "Chefe de Equipe"
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

        {showPopUp && (error || success) && (
          <PopUp message={error || success} onClose={() => setShowPopUp(false)} />
        )}
      </div>
    </div>
  );
}
