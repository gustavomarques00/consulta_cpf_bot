"use client";

import { useEffect, useState } from "react";
import axios from "axios";
import UserProfileCard from "../components/UserProfileCard";
import { FiLogOut, FiArrowLeft } from "react-icons/fi";
import Link from "next/link";
import { useRouter } from "next/navigation";

interface User {
  name: string;
  email: string;
  phone: string;
}

export default function ProfilePage() {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const router = useRouter();


  
  useEffect(() => {
    const fetchUserProfile = async () => {
      try {
        const response = await axios.get("/api/user-profile");
        setUser(response.data);
      } catch (err) {
        setError("Erro ao carregar perfil.");
      } finally {
        setLoading(false);
      }
    };

    fetchUserProfile();
  }, []);
  

  const handleLogout = () => {
    // Simulação de logout (remover token e redirecionar para login)
    localStorage.removeItem("authToken");
    router.push("/login");
  };

  //if (loading) return <p className="text-center text-lg">Carregando perfil...</p>;
  if (error) return <p className="text-center text-red-500">{error}</p>;

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 to-gray-800 flex flex-col items-center p-8">
      <div className="max-w-lg w-full bg-white dark:bg-gray-800 p-10 rounded-xl shadow-2xl text-center">
        
        {/* Perfil do Usuário */}
        {user && <UserProfileCard name={user.name} email={user.email} phone={user.phone} />}

        {/* Botões de Ação */}
        <div className="mt-6 flex flex-col gap-4">
          {/* Logout */}
          <button
            onClick={handleLogout}
            className="flex items-center gap-2 bg-red-600 text-white py-3 px-6 rounded-lg hover:bg-red-700 transition-all duration-300 transform hover:scale-105 shadow-md"
          >
            <FiLogOut size={20} />
            Sair da Conta
          </button>

          {/* Voltar */}
          <Link
            href="/dashboard"
            className="flex items-center justify-center gap-2 text-lg font-semibold text-indigo-600 dark:text-indigo-400 hover:underline transition-all duration-300 hover:text-indigo-500"
          >
            <FiArrowLeft size={18} />
            Voltar para o Dashboard
          </Link>
        </div>
      </div>
    </div>
  );
}
