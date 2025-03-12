import { Geist, Geist_Mono } from "next/font/google";
import Link from "next/link";
import "./globals.css";
import ThemeProvider from "./ThemeProvider"; // Importando o provider do tema

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="pt-BR">
      <body className={`${geistSans.variable} ${geistMono.variable} antialiased bg-white dark:bg-gray-900 dark:text-white`}>
        <ThemeProvider>
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
                  <li>
                    <Link href="/search" className="hover:text-indigo-200">
                      Buscar
                    </Link>
                  </li>
                </ul>
              </nav>
            </aside>

            {/* Conteúdo Principal */}
            <main className="flex-1 p-6">
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
                </div>
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