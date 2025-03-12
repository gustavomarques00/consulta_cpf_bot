"use client";

import { useEffect, useState } from "react";

export default function ThemeProvider({ children }: { children: React.ReactNode }) {
  const [darkMode, setDarkMode] = useState<boolean | null>(null);

  useEffect(() => {
    const savedTheme = localStorage.getItem("theme");
    setDarkMode(savedTheme === "dark" ? true : false);
  }, []);

  const toggleTheme = () => {
    setDarkMode((prev) => {
      const newTheme = !prev;
      localStorage.setItem("theme", newTheme ? "dark" : "light");
      document.documentElement.classList.toggle("dark", newTheme);
      return newTheme;
    });
  };

  if (darkMode === null) return null; // Evita piscar tema no carregamento

  return (
    <div>
      <button onClick={toggleTheme} className="absolute top-4 right-4 text-indigo-600 dark:text-indigo-400">
        {darkMode ? "Modo Claro" : "Modo Escuro"}
      </button>
      {children}
    </div>
  );
}
