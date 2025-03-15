"use client";

import { FiSend } from "react-icons/fi";

interface SupportButtonProps {
  url: string;
  label: string;
}

export default function SupportButton({ url, label }: SupportButtonProps) {
  return (
    <a
      href={url}
      target="_blank"
      rel="noopener noreferrer"
      className="inline-flex items-center justify-center gap-3 bg-gradient-to-r from-blue-500 to-indigo-500 text-white py-3 px-8 rounded-lg shadow-md hover:shadow-xl transition-all duration-300 transform hover:scale-105"
      aria-label="Acessar suporte no Telegram"
    >
      <FiSend size={22} />
      <span className="font-semibold">{label}</span>
    </a>
  );
}
