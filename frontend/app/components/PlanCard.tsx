import SupportButton from "../components/SupportButton";  // Importe o botão de suporte
import { FiSend } from "react-icons/fi";  // Importe o ícone FiSend

interface PlanCardProps {
  nome: string;
  status?: string;
  features: string[]; // Garantindo que seja sempre um array
  renewalDate?: string;  // Adicionando a data de renovação
  price?: string;
  botUsername?: string;  // Adicionando o nome de usuário do bot
}

export default function PlanCard({
  nome,
  status,
  features,
  renewalDate,
  price,
  botUsername
}: PlanCardProps) {

  // Garantir que 'features' seja sempre um array
  const featureList = Array.isArray(features) ? features : [];

  // Função para formatar o preço com vírgula e ajustar de acordo com a lógica
  const formatPrice = (price: string) => {
    let parsedPrice = parseFloat(price.replace(',', '.')); // Convertendo para número
    let finalPrice: number;

    // Mantém o preço original sem ajustes
    finalPrice = parsedPrice;

    // Formata o valor com vírgula
    return new Intl.NumberFormat('pt-BR', { style: 'decimal', minimumFractionDigits: 2, maximumFractionDigits: 2 }).format(finalPrice);
  };

  // Definindo a cor do status com base no valor de "status"
  const statusClass = status === "Ativo" ? "text-green-500" : "text-red-500";

  return (
    <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow-lg hover:shadow-2xl transition-all duration-300 transform hover:scale-105">
      <h2 className="text-2xl font-semibold text-gray-800 dark:text-white mb-4">{nome}</h2>

      {/* Exibindo o status somente se existir, com cor condicional */}
      {status && (
        <p className="text-gray-700 dark:text-gray-300 mb-2">
          Status: <span className={`font-medium ${statusClass}`}>{status}</span>
        </p>
      )}

      {/* Exibindo a data de renovação */}
      {renewalDate && <p className="text-gray-700 dark:text-gray-300 mb-2">Data de Renovação: <span className="font-medium">{renewalDate}</span></p>}

      {/* Exibindo o preço somente se existir */}
      {price && <p className="text-lg text-indigo-600 dark:text-indigo-400 font-semibold mb-4">Preço: R$ <span className="text-xl">{formatPrice(price)}</span></p>}

      {/* Exibindo os benefícios */}
      {featureList.length > 0 ? (
        <>
          <h3 className="text-xl font-semibold text-gray-800 dark:text-white mb-4">✅ Benefícios:</h3>
          <ul className="list-none space-y-2">
            {featureList.map((feature, index) => (
              <li key={index} className="flex items-center gap-2 text-gray-700 dark:text-gray-300">
                <FiSend size={18} className="text-green-500" />
                {feature}
              </li>
            ))}
          </ul>
        </>
      ) : (
        <p className="text-gray-500 dark:text-gray-400">Nenhum benefício listado.</p>  // Mensagem para quando não houver benefícios
      )}

      {/* Botão de Suporte - Telegram */}
      <div className="mt-6">
        <SupportButton
          botUsername={botUsername || ''}  // Passando o nome de usuário do bot
          label="Faça o Upgrade!"  // Texto do botão
        />
      </div>
    </div>
  );
}
