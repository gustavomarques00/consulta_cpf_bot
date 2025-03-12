import { useState } from "react";
import { useForm } from "react-hook-form";
import axios from "axios";
import RootLayout from "../layout"; // Importando o layout
import EmailInput from "../components/EmailInput"; // Importando o componente de email
import PasswordInput from "../components/PasswordInput"; // Importando o componente de senha

interface LoginFormData {
  email: string;
  password: string;
}

export default function Login() {
  const [loading, setLoading] = useState<boolean>(false); // Controle de carregamento
  const [error, setError] = useState<string>(""); // Mensagens de erro

  // Usando react-hook-form para validação
  const { control, handleSubmit, formState: { errors }, watch } = useForm<LoginFormData>();

  // Função de login ao submeter o formulário
  const onSubmit = async (data: LoginFormData) => {
    setLoading(true);
    setError(""); // Resetar erro

    try {
      const response = await axios.post("http://localhost:5000/login", {
        email: data.email,
        password: data.password,
      });

      // Sucesso no login
      console.log("Login bem-sucedido:", response.data);
      // Aqui você pode redirecionar o usuário para outra página após o login (ex: Dashboard)
    } catch (err: any) {
      setError("Erro ao tentar fazer login. Verifique suas credenciais.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <RootLayout>
      <div className="min-h-screen bg-gray-50 p-8 flex items-center justify-center">
        <div className="max-w-md w-full bg-white p-8 rounded-lg shadow-md">
          <h1 className="text-3xl font-bold mb-6 text-center">Login</h1>

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
              watch={watch}
            />

            {/* Botão de Submissão */}
            <div>
              <button
                type="submit"
                disabled={loading}
                className="w-full bg-indigo-600 text-white py-3 rounded-md hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500"
              >
                {loading ? "Processando..." : "Entrar"}
              </button>
            </div>
          </form>

          {/* Exibir erros */}
          {error && <p className="mt-4 text-red-500 text-center">{error}</p>}

          {/* Link para a página de registro */}
          <div className="mt-4 text-center">
            <p>
              Não tem uma conta?{" "}
              <a href="/register" className="text-indigo-600 hover:text-indigo-800">
                Registre-se
              </a>
            </p>
          </div>
        </div>
      </div>
    </RootLayout>
  );
}
