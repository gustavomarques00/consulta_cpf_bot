"use client";

import { useEffect, useState } from "react";

interface PopUpProps {
  message: string;
  onClose: () => void;
}

export default function PopUp({ message, onClose }: PopUpProps) {
  const [isVisible, setIsVisible] = useState(true);

  // Fechar automaticamente após 5s
  useEffect(() => {
    const timer = setTimeout(() => {
      setIsVisible(false); // Começa a animação de saída
      setTimeout(onClose, 500); // Fecha o PopUp após a animação
    }, 5000);

    return () => clearTimeout(timer);
  }, [onClose]);

  if (!isVisible) return null; // Não renderiza o PopUp após o tempo de animação de saída

  return (
    <div className="fixed top-4 right-4 bg-red-500 text-white p-4 rounded-lg shadow-lg z-50 animate-fade-in transition-all duration-500 ease-in-out">
      <p>{message}</p>
      <button
        onClick={() => {
          setIsVisible(false); // Inicia a animação de saída
          setTimeout(onClose, 500); // Fecha após a animação
        }}
        className="ml-4 text-lg font-bold"
      >
        ✖
      </button>
    </div>
  );
}
