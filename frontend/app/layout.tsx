'use client';

import { useState, useEffect } from "react";
import { Geist, Geist_Mono } from "next/font/google";
import Link from "next/link";
import { FaHome, FaLock, FaRegHandshake, FaTachometerAlt, FaSearch, FaCreditCard, FaExchangeAlt, FaComments, FaUser, FaCog, FaChevronLeft, FaChevronRight, FaMoneyBill } from 'react-icons/fa'; // Ícones do React Icons
import SidebarLink from "./components/SidebarLink"; // Importando o componente SidebarLink
import "./globals.css";
import ThemeProvider from "./ThemeProvider";
import { FaCloudBolt } from "react-icons/fa6";

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
      <body className=" bg-white dark:bg-gray-900 dark:text-white min-h-screen">
        <ThemeProvider>
          <div className="flex overflow-hidden min-h-screen">
            {/* Sidebar Dinâmica - Com ícones e texto chamativo */}
            <aside className={`transition-all duration-300 ${sidebarOpen ? 'w-64' : 'w-20'} bg-blue-600 text-white p-4 flex flex-col justify-between`}>
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
                    <SidebarLink to="/operation" icon={FaExchangeAlt} label="Operação" isSidebarOpen={sidebarOpen} />
                    <SidebarLink to="/plans" icon={FaCreditCard} label="Planos" isSidebarOpen={sidebarOpen} />
                    <SidebarLink to="/admin-panel" icon={FaMoneyBill} label="Painel Admin" isSidebarOpen={sidebarOpen} />
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
            <main className="flex flex-col h-screen overflow-hidden w-full"> 
              <header className="h-20 bg-white shadow-md p-8 dark:bg-gray-800 dark:text-white flex justify-between items-center">
                <Link href="/" className="flex items-center">
                  <img src="/logo.webp" alt="Logo JUVO" className="w-20 h-20 mr-4 rounded-full" />
                  <h1 className="text-4xl font-extrabold text-gray-900 dark:text-white flex items-center">
                    Sistema de Extração - JUVO
                    <span className="text-3xl ml-3 text-indigo-500">🚀</span>
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
              <section className='flex-grow h-[calc(100vh-80px)] w-full overflow-auto'>
                {children}
              </section>
            </main>
          </div>
        </ThemeProvider>
      </body>
    </html>
  );
}
