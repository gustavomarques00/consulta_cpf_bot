"use client";

import { useEffect } from "react";
import Link from "next/link";

const TELEGRAM_SUPPORT_URL = "https://t.me/seu_bot_de_suporte"; // Substitua pelo link real

export default function SupportPage() {
  useEffect(() => {
    document.title = "Suporte | SaaS XYZ";
  }, []);

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 p-8 flex items-center justify-center">
      <div className="max-w-md w-full bg-white dark:bg-gray-800 p-8 rounded-lg shadow-md text-center">
        <h1 className="text-3xl font-bold mb-6 text-gray-900 dark:text-white">
          Precisa de Ajuda? 🤔
        </h1>
        <p className="text-gray-700 dark:text-gray-300 mb-4">
          Nossa equipe de suporte está disponível no Telegram para ajudar você com qualquer dúvida ou problema.
        </p>
        <p className="text-gray-700 dark:text-gray-300 mb-6">
          Clique no botão abaixo para acessar nosso suporte.
        </p>

        <a
          href={TELEGRAM_SUPPORT_URL}
          target="_blank"
          rel="noopener noreferrer"
          className="inline-block bg-blue-600 text-white py-3 px-6 rounded-md hover:bg-blue-700 transition duration-200"
          aria-describedby="suporte-info"
        >
          Acessar Suporte no Telegram
        </a>

        <p id="suporte-info" className="text-sm text-gray-500 dark:text-gray-400 mt-4">
          Você será redirecionado para nosso suporte no Telegram.
        </p>

        {/* Botão para voltar */}
        <div className="mt-6">
          <Link
            href="/"
            className="text-indigo-600 dark:text-indigo-400 hover:underline"
          >
            Voltar para a Página Inicial
          </Link>
        </div>
      </div>
    </div>
  );
}
