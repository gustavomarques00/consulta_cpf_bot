"use client";

import { FiUser, FiMail, FiPhone, FiSettings } from "react-icons/fi";

interface UserProfileProps {
  name: string;
  email: string;
  phone: string;
}

export default function UserProfileCard({ name, email, phone }: UserProfileProps) {
  return (
    <div className="w-full bg-white dark:bg-gray-800 p-6 rounded-lg shadow-lg transition-all duration-300 hover:shadow-xl">
      <h2 className="text-2xl font-semibold text-gray-900 dark:text-white text-center mb-4">
        Meu Perfil
      </h2>

      <div className="space-y-4">
        {/* Nome */}
        <div className="flex items-center gap-3 text-gray-700 dark:text-gray-300">
          <FiUser size={22} className="text-indigo-500" />
          <p className="text-lg">{name}</p>
        </div>

        {/* Email */}
        <div className="flex items-center gap-3 text-gray-700 dark:text-gray-300">
          <FiMail size={22} className="text-indigo-500" />
          <p className="text-lg">{email}</p>
        </div>

        {/* Telefone */}
        <div className="flex items-center gap-3 text-gray-700 dark:text-gray-300">
          <FiPhone size={22} className="text-indigo-500" />
          <p className="text-lg">{phone}</p>
        </div>
      </div>

      {/* Botão de Editar Perfil */}
      <div className="mt-6 flex justify-center">
        <button className="flex items-center gap-2 bg-indigo-600 text-white py-2 px-4 rounded-lg hover:bg-indigo-700 transition-all duration-300 transform hover:scale-105 shadow-md">
          <FiSettings size={18} />
          Editar Perfil
        </button>
      </div>
    </div>
  );
}
