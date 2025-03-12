// app/layout.tsx

import { Geist, Geist_Mono } from "next/font/google";
import { ReactNode, useEffect, useState } from "react";
import Link from "next/link";
import "./globals.css";

// Definindo as fontes com next/font para garantir que as fontes sejam carregadas corretamente.
const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata = {
  title: "Sistema de Autenticação",
  description: "Sistema de login e registro com layout completo.",
};

export default function RootLayout({ children }: { children: ReactNode }) {
  const [darkMode, setDarkMode] = useState<boolean | null>(null);

  // Usando useEffect para garantir que o estado do tema seja alterado somente no cliente
  useEffect(() => {
    const savedTheme = localStorage.getItem("theme");
    if (savedTheme) {
      setDarkMode(savedTheme === "dark");
    } else {
      setDarkMode(false); // Padrão para modo claro
    }
  }, []);

  // Alternar entre modos claro e escuro
  const toggleTheme = () => {
    setDarkMode((prev) => {
      const newTheme = !prev;
      localStorage.setItem("theme", newTheme ? "dark" : "light");
      return newTheme;
    });
  };

  if (darkMode === null) return null; // Espera o estado ser carregado

  return (
    <html lang="pt-BR" className={darkMode ? "dark" : ""}>
      <body
        className={`${geistSans.variable} ${geistMono.variable} antialiased bg-white dark:bg-gray-900 dark:text-white`}
      >
        <div className="flex min-h-screen">
          {/* Sidebar */}
          <aside className="w-64 bg-indigo-600 text-white p-4">
            <h2 className="text-xl font-bold mb-6">Painel de Controle</h2>
            <nav>
              <ul className="space-y-4">
                <li>
                  <Link href="/login" className="hover:text-indigo-200">
                    Login
                  </Link>
                </li>
                <li>
                  <Link href="/register" className="hover:text-indigo-200">
                    Registrar
                  </Link>
                </li>
                <li>
                  <Link href="/dashboard" className="hover:text-indigo-200">
                    Dashboard
                  </Link>
                </li>
              </ul>
            </nav>
          </aside>

          {/* Main Content Area */}
          <main className="flex-1 p-6">
            {/* Header */}
            <header className="bg-white shadow-md p-4 mb-6 dark:bg-gray-800 dark:text-white">
              <div className="flex justify-between items-center">
                <h1 className="text-3xl font-semibold">Sistema de Autenticação</h1>
                <nav>
                  <ul className="flex space-x-6">
                    <li>
                      <Link href="/profile" className="hover:text-indigo-600">
                        Perfil
                      </Link>
                    </li>
                    <li>
                      <Link href="/settings" className="hover:text-indigo-600">
                        Configurações
                      </Link>
                    </li>
                  </ul>
                </nav>
                <button
                  onClick={toggleTheme}
                  className="text-indigo-600 dark:text-indigo-400"
                >
                  {darkMode ? "Modo Claro" : "Modo Escuro"}
                </button>
              </div>
            </header>

            {/* Renderiza o conteúdo principal aqui (filhos) */}
            <section>{children}</section>
          </main>
        </div>
      </body>
    </html>
  );
}
