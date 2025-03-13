'use client';

import { useState, useEffect } from "react";
import { Geist, Geist_Mono } from "next/font/google";
import Link from "next/link";
import { FaHome, FaLock, FaRegHandshake, FaTachometerAlt, FaSearch, FaCreditCard, FaComments, FaUser, FaCog, FaChevronLeft, FaChevronRight  } from 'react-icons/fa'; // Ícones do React Icons
import SidebarLink from "./components/SidebarLink"; // Importando o componente SidebarLink
import "./globals.css";
import ThemeProvider from "./ThemeProvider";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export default function RootLayout({ children }: { children: React.ReactNode }) {
  const [sidebarOpen, setSidebarOpen] = useState<boolean>(true);

  useEffect(() => {
    // Aplique o tema no cliente apenas após a primeira renderização
    const savedTheme = localStorage.getItem("theme") || "light"; // Padrão 'light' se não houver no localStorage
    document.documentElement.setAttribute("data-theme", savedTheme);
  }, []);

  const toggleTheme = () => {
    const newTheme = document.documentElement.getAttribute("data-theme") === "dark" ? "light" : "dark";
    document.documentElement.setAttribute("data-theme", newTheme);
    localStorage.setItem("theme", newTheme);
  };

  return (
    <html lang="pt-BR">
      <body className="antialiased bg-white dark:bg-gray-900 dark:text-white">
        <ThemeProvider>
          <div className="flex min-h-screen">
            {/* Sidebar Dinâmica - Com ícones e texto chamativo */}
            <aside className={`transition-all duration-300 ${sidebarOpen ? "w-64" : "w-20"} bg-blue-600 text-white p-4 flex flex-col justify-between h-screen`}>
              <div>
                {/* Botão de Alternância com ícones */}
                <button
                  onClick={() => setSidebarOpen(!sidebarOpen)}
                  className="w-full text-left text-white hover:text-indigo-200 mb-4 focus:outline-none"
                  aria-label="Alternar menu"
                >
                  {sidebarOpen ? (
                    <SidebarLink icon={FaChevronLeft} label="Recuar" isSidebarOpen={sidebarOpen} />
                  ) : (
                    <SidebarLink icon={FaChevronRight} label="Expandir" isSidebarOpen={sidebarOpen} />
                  )}
                </button>

                <nav>
                  <ul className="space-y-4">
                    <SidebarLink to="/" icon={FaHome} label="Início" isSidebarOpen={sidebarOpen} />
                    <SidebarLink to="/login" icon={FaLock} label="Login" isSidebarOpen={sidebarOpen} />
                    <SidebarLink to="/register" icon={FaRegHandshake} label="Registrar" isSidebarOpen={sidebarOpen} />
                    <SidebarLink to="/dashboard" icon={FaTachometerAlt} label="Dashboard" isSidebarOpen={sidebarOpen} />
                    <SidebarLink to="/search" icon={FaSearch} label="Buscar" isSidebarOpen={sidebarOpen} />
                    <SidebarLink to="/plans" icon={FaCreditCard} label="Planos" isSidebarOpen={sidebarOpen} />
                    <SidebarLink to="/support" icon={FaComments} label="Suporte" isSidebarOpen={sidebarOpen} />
                  </ul>
                </nav>
              </div>

              {/* Fixando Perfil e Configurações na parte inferior */}
              <div className="mt-auto space-y-4">
                <SidebarLink to="/profile" icon={FaUser} label="Perfil" isSidebarOpen={sidebarOpen} />
                <SidebarLink to="/settings" icon={FaCog} label="Configurações" isSidebarOpen={sidebarOpen} />
              </div>
            </aside>

            {/* Conteúdo Principal */}
            <main className="flex-1 p-6 overflow-auto">
              <header className="bg-white shadow-md p-4 mb-6 dark:bg-gray-800 dark:text-white flex justify-between items-center">
                <Link href="/" className="flex items-center">
                  <img src="/logo.webp" alt="Logo JUVO" className="w-12 h-12 mr-2" />
                  <h1 className="text-3xl font-semibold text-gray-900 dark:text-white">
                    Sistema de Extração - JUVO <span className="text-2xl ml-2">🚀</span>
                  </h1>
                </Link>

                {/* Alternar Tema */}
                <button
                  onClick={toggleTheme}
                  className="text-indigo-600 dark:text-indigo-400 text-xl"
                  aria-label="Alternar Modo Claro/Escuro"
                >
                  🌙 / ☀️
                </button>
              </header>

              {/* Renderiza o conteúdo da página */}
              <section>{children}</section>
            </main>
          </div>
        </ThemeProvider>
      </body>
    </html>
  );
}
