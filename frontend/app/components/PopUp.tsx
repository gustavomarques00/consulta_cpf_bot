"use client";

import { useEffect } from "react";

interface PopUpProps {
  message: string;
  onClose: () => void;
}

export default function PopUp({ message, onClose }: PopUpProps) {
  useEffect(() => {
    const timer = setTimeout(onClose, 5000); // Fecha automaticamente após 5s
    return () => clearTimeout(timer);
  }, [onClose]);

  return (
    <div className="fixed top-4 right-4 bg-red-500 text-white p-4 rounded-lg shadow-lg z-50 animate-fade-in">
      <p>{message}</p>
      <button onClick={onClose} className="ml-4 text-lg font-bold">✖</button>
    </div>
  );
}
