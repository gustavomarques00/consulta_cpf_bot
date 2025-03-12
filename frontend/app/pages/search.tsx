import { useState } from "react";
import axios from "axios";
import { useForm } from "react-hook-form";
import RootLayout from "../layout"; // Importando o layout
import InputField from "../components/InputField"; // Componente de campo de entrada
import ErrorMessage from "../components/ErrorMessage"; // Componente de mensagem de erro

// Função para validação do CPF
const validateCPF = (cpf: string) => {
  const regex = /^(?:\d{3}\.\d{3}\.\d{3}-\d{2}|\d{11})$/;
  return regex.test(cpf);
};

interface SearchFormData {
  cpfs: string;
}

export default function Search() {
  const [resultados, setResultados] = useState<any[]>([]); // Armazenar os resultados
  const [loading, setLoading] = useState<boolean>(false); // Controle de carregamento
  const [error, setError] = useState<string>(""); // Mensagens de erro

  // Usando react-hook-form para validação
  const { control, handleSubmit, formState: { errors } } = useForm<SearchFormData>(); // Aqui declaramos o useForm

  const onSubmit = async (data: SearchFormData) => {
    setLoading(true);
    setError(""); // Resetar erro
    setResultados([]); // Limpar resultados anteriores

    try {
      // Enviar CPFs para o backend
      const response = await axios.post("http://localhost:5000/processar", {
        cpfs: data.cpfs.split("\n").map((cpf: string) => cpf.trim()), // Trata CPFs enviados
      });

      setResultados(response.data);
    } catch (err: any) {
      setError("Erro ao processar os CPFs. Tente novamente.");
    } finally {
      setLoading(false);
    }
  };

  const exportToGoogleSheets = async () => {
    try {
      // Supondo que o backend tem um endpoint para exportar para o Google Sheets
      await axios.post("http://localhost:5000/export-to-google-sheets", {
        dados: resultados,
      });
      alert("Dados exportados com sucesso para o Google Sheets!");
    } catch (err) {
      alert("Erro ao exportar para o Google Sheets. Tente novamente.");
    }
  };

  return (
    <RootLayout>
      <div className="container mx-auto px-4">
        <div className="max-w-lg mx-auto mt-10">
          <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
            <InputField
              label="CPFs (separados por vírgula ou linha):"
              name="cpfs"
              type="text"
              control={control}
              rules={{
                required: "Os CPFs são obrigatórios",
                validate: {
                  validCPFs: (value: string) =>
                    value.split("\n").every((cpf: string) => validateCPF(cpf.trim())) ||
                    "Um ou mais CPFs informados não são válidos",
                },
              }}
              placeholder="Exemplo: 123.456.789-00, 987.654.321-00"
              errors={errors} // Passando erros para o componente de erro
            />
            <ErrorMessage error={errors.cpfs} /> {/* Exibindo erro, se houver */}

            <div>
              <button
                type="submit"
                disabled={loading}
                className="w-full bg-indigo-600 text-white py-3 rounded-md hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500"
              >
                {loading ? "Buscando..." : "Buscar CPFs"}
              </button>
            </div>
          </form>

          {error && <p className="mt-4 text-red-500 text-center">{error}</p>} {/* Exibe erro de requisição */}

          {/* Exibir resultados em uma tabela */}
          {resultados.length > 0 && (
            <div className="mt-6">
              <h2 className="text-2xl font-semibold mb-4">Resultados:</h2>
              <table className="min-w-full bg-white">
                <thead>
                  <tr>
                    <th className="py-2">CPF</th>
                    <th className="py-2">Nome</th>
                    <th className="py-2">Email</th>
                    <th className="py-2">Telefone</th>
                    <th className="py-2">Status</th>
                  </tr>
                </thead>
                <tbody>
                  {resultados.map((resultado, index) => (
                    <tr key={index} className="bg-gray-100 border-b">
                      <td className="py-2 px-4">{resultado.cpf}</td>
                      <td className="py-2 px-4">{resultado.nome}</td>
                      <td className="py-2 px-4">{resultado.email}</td>
                      <td className="py-2 px-4">{resultado.telefone}</td>
                      <td className="py-2 px-4">{resultado.status}</td>
                    </tr>
                  ))}
                </tbody>
              </table>

              {/* Botão para exportar para o Google Sheets */}
              <div className="mt-4">
                <button
                  onClick={exportToGoogleSheets}
                  className="w-full bg-green-600 text-white py-3 rounded-md hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-green-500"
                >
                  Exportar para Google Sheets
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </RootLayout>
  );
}
