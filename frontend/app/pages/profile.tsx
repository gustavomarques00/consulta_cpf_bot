import { useState } from "react";
import { useForm } from "react-hook-form";
import axios from "axios";
import RootLayout from "../layout"; // Importando o layout
import EmailInput from "../components/EmailInput"; // Importando o componente de email
import PasswordInput from "../components/PasswordInput"; // Importando o componente de senha
import InputField from "../components/InputField"; // Componente de input genérico

interface ProfileFormData {
  email: string;
  password: string;
  nome: string;
  telefone: string;
}

export default function Profile() {
  const [loading, setLoading] = useState<boolean>(false); // Controle de carregamento
  const [error, setError] = useState<string>(""); // Mensagens de erro
  const [successMessage, setSuccessMessage] = useState<string>(""); // Mensagem de sucesso após atualização

  // Usando react-hook-form para validação
  const { control, handleSubmit, formState: { errors }, watch } = useForm<ProfileFormData>();

  // Função de atualização de perfil ao submeter o formulário
  const onSubmit = async (data: ProfileFormData) => {
    setLoading(true);
    setError(""); // Resetar erro
    setSuccessMessage(""); // Resetar mensagem de sucesso

    try {
      const response = await axios.put("http://localhost:5000/profile", {
        email: data.email,
        password: data.password,
        nome: data.nome,
        telefone: data.telefone,
      });

      // Sucesso na atualização do perfil
      setSuccessMessage("Perfil atualizado com sucesso!"); // Feedback visual de sucesso
    } catch (err: any) {
      setError("Erro ao tentar atualizar o perfil. Tente novamente.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <RootLayout>
      <div className="min-h-screen bg-gray-50 p-8 flex items-center justify-center">
        <div className="max-w-md w-full bg-white p-8 rounded-lg shadow-md">
          <h1 className="text-3xl font-bold mb-6 text-center">Perfil</h1>

          {/* Formulário de edição de perfil */}
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

            {/* Campo de Nome */}
            <InputField
              label="Nome"
              name="nome"
              type="text" // Passando o tipo correto
              control={control}
              rules={{ required: "O nome é obrigatório" }}
              errors={errors}
            />

            {/* Campo de Telefone */}
            <InputField
              label="Telefone"
              name="telefone"
              type="text" // Passando o tipo correto
              control={control}
              rules={{
                required: "O telefone é obrigatório",
                pattern: {
                  value: /^\(\d{2}\) \d{5}-\d{4}$/,
                  message: "Telefone inválido. Use o formato (11) 98765-4321",
                },
              }}
              errors={errors}
              placeholder="Exemplo: (11) 98765-4321"
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

            {/* Botão de Submissão */}
            <div>
              <button
                type="submit"
                disabled={loading}
                className="w-full bg-indigo-600 text-white py-3 rounded-md hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500"
              >
                {loading ? "Processando..." : "Atualizar Perfil"}
              </button>
            </div>
          </form>

          {/* Exibir erros */}
          {error && <p className="mt-4 text-red-500 text-center">{error}</p>}

          {/* Exibir sucesso */}
          {successMessage && (
            <p className="mt-4 text-green-500 text-center">{successMessage}</p>
          )}
        </div>
      </div>
    </RootLayout>
  );
}
