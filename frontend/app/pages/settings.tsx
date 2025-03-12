import { useState, useEffect } from "react";
import { useForm, Controller } from "react-hook-form"; // Corrigido a importação do Controller
import axios from "axios";
import RootLayout from "../layout"; // Importando o layout
import EmailInput from "../components/EmailInput"; // Importando o componente de email
import PasswordInput from "../components/PasswordInput"; // Importando o componente de senha
import InputField from "../components/InputField"; // Componente de input genérico
import CheckboxInput from "../components/CheckboxInput"; // Importando o componente de checkbox

interface SettingsFormData {
    email: string;
    password: string;
    tema: string; // Para alterar o tema (claro ou escuro)
    notificacoes: boolean; // Para alterar as preferências de notificações
}

export default function Settings() {
    const [loading, setLoading] = useState<boolean>(false); // Controle de carregamento
    const [error, setError] = useState<string>(""); // Mensagens de erro
    const [successMessage, setSuccessMessage] = useState<string>(""); // Mensagem de sucesso após atualização

    // Usando react-hook-form para validação
    const { control, handleSubmit, formState: { errors }, watch } = useForm<SettingsFormData>();

    // Carregar tema salvo do localStorage ou definir como 'claro' por padrão
    useEffect(() => {
        const savedTheme = localStorage.getItem("theme") || "claro";
        // Ajuste do tema com base no valor
        document.documentElement.setAttribute('data-theme', savedTheme);
    }, []);

    // Função de atualização de configurações ao submeter o formulário
    const onSubmit = async (data: SettingsFormData) => {
        setLoading(true);
        setError(""); // Resetar erro
        setSuccessMessage(""); // Resetar mensagem de sucesso

        // Salvar preferências de tema no localStorage
        localStorage.setItem("theme", data.tema);

        try {
            const response = await axios.put("http://localhost:5000/settings", {
                email: data.email,
                password: data.password,
                tema: data.tema,
                notificacoes: data.notificacoes,
            });

            // Sucesso na atualização das configurações
            setSuccessMessage("Configurações atualizadas com sucesso!"); // Feedback visual de sucesso
        } catch (err: any) {
            setError("Erro ao tentar atualizar as configurações. Tente novamente.");
        } finally {
            setLoading(false);
        }
    };

    return (
        <RootLayout>
            <div className="min-h-screen bg-gray-50 p-8 flex items-center justify-center">
                <div className="max-w-md w-full bg-white p-8 rounded-lg shadow-md">
                    <h1 className="text-3xl font-bold mb-6 text-center">Configurações</h1>

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
                            placeholder="Exemplo: claro ou escuro"
                        />

                        {/* Campo de Notificações */}
                        <CheckboxInput
                            label="Notificações"
                            name="notificacoes"
                            control={control}
                            rules={{ required: "Notificação é obrigatória" }}
                            errors={errors}
                        />

                        {/* Botão de Submissão */}
                        <div>
                            <button
                                type="submit"
                                disabled={loading}
                                className="w-full bg-indigo-600 text-white py-3 rounded-md hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500"
                            >
                                {loading ? "Processando..." : "Atualizar Configurações"}
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
