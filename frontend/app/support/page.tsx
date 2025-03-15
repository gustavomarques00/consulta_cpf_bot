"use client";

import { useEffect } from "react";
import Link from "next/link";
import SupportButton from "../components/SupportButton";
import { FiHelpCircle, FiArrowLeft } from "react-icons/fi";
import { BsTelegram } from "react-icons/bs";

const TELEGRAM_SUPPORT_URL = "https://t.me/seu_bot_de_suporte"; // Substitua pelo link real

export default function SupportPage() {
  useEffect(() => {
    document.title = "Suporte | SaaS XYZ";
  }, []);

  return (
    <div className="min-h-screen flex items-center justify-center px-6 bg-gradient-to-br from-gray-900 to-gray-800">
      <div className="max-w-md w-full bg-white dark:bg-gray-800 p-10 rounded-2xl shadow-2xl text-center transition-all duration-300 hover:shadow-xl">
        
        {/* Ícone de Suporte com animação */}
        <div className="flex justify-center mb-4">
          <FiHelpCircle className="text-blue-600 dark:text-blue-400 animate-pulse" size={60} />
        </div>

        <h1 className="text-4xl font-extrabold text-gray-900 dark:text-white mb-4">
          Precisa de Ajuda? 🤔
        </h1>

        <p className="text-gray-600 dark:text-gray-300 text-lg mb-4">
          Nossa equipe de suporte está disponível no Telegram para ajudar você com qualquer dúvida ou problema.
        </p>

        <p className="text-gray-600 dark:text-gray-300 text-lg mb-6">
          Clique no botão abaixo para falar conosco.
        </p>

        {/* Botão de Suporte Melhorado */}
        <SupportButton url={TELEGRAM_SUPPORT_URL} label="Falar com Suporte" />

        <p className="text-sm text-gray-500 dark:text-gray-400 mt-5 flex items-center justify-center gap-2">
          Você será redirecionado para nosso suporte no Telegram.
        </p>

        {/* Botão para voltar */}
        <div className="mt-6">
          <Link
            href="/"
            className="inline-flex items-center gap-2 text-lg font-semibold text-indigo-600 dark:text-indigo-400 hover:underline transition-all duration-300 hover:text-indigo-500"
          >
            <FiArrowLeft size={18} />
            Voltar para a Página Inicial
          </Link>
        </div>
      </div>
    </div>
  );
}
