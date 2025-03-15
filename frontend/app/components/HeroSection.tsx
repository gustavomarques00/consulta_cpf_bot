import Link from "next/link";
import { FiUserPlus, FiLogIn } from "react-icons/fi";

export default function HeroSection() {
  return (
    <div className="h-[70vh] flex flex-col justify-center text-center px-6">
      <h1 className="text-5xl font-bold mb-6">
        🚀 A solução definitiva para sua produtividade!
      </h1>
      <p className="text-lg text-gray-300 max-w-2xl mx-auto">
        Um SaaS moderno para otimizar processos e escalar seus resultados. Experimente agora mesmo!
      </p>
      <div className="mt-6 flex justify-center gap-4">
        <Link href="/register" className="bg-blue-600 hover:bg-blue-700 px-6 py-3 rounded-lg text-lg font-semibold flex items-center gap-2 transition-all">
          <FiUserPlus size={20} />
          Cadastre-se Gratuitamente
        </Link>
        <Link href="/login" className="border border-gray-300 px-6 py-3 rounded-lg text-lg hover:bg-gray-700 flex items-center gap-2 transition-all">
          <FiLogIn size={20} />
          Entrar
        </Link>
      </div>
    </div>
  );
}
