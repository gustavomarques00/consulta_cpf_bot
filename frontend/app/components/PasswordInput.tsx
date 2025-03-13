'use client';

import { Controller, Control, FieldErrors } from "react-hook-form";
import { useState } from "react";
import { AiFillEye, AiFillEyeInvisible } from "react-icons/ai"; // ícones de olho
import ErrorMessage from "./ErrorMessage";

interface PasswordInputProps {
  label: string;
  name: string;
  control: Control<any>;
  rules: any;
  errors: FieldErrors<any>;
}

export default function PasswordInput({ label, name, control, rules, errors }: PasswordInputProps) {
  const [showPassword, setShowPassword] = useState(false); // Estado para alternar a visibilidade
  const error = errors[name];

  return (
    <div className="w-full">
      <label htmlFor={name} className="block text-sm font-medium text-gray-700 dark:text-gray-300">
        {label}
      </label>

      <div className="relative">
        <Controller
          name={name}
          control={control}
          rules={rules}
          render={({ field }) => (
            <input
              {...field}
              id={name}
              type={showPassword ? "text" : "password"} // Alterna o tipo do campo
              className={`w-full mt-2 p-3 border rounded-md focus:outline-none focus:ring-2 ${
                error ? "border-red-500 focus:ring-red-500" : "border-gray-300 focus:ring-indigo-500"
              }`}
              placeholder="Sua senha"
              aria-invalid={error ? "true" : "false"}
              aria-describedby={error ? `${name}-error` : undefined}
            />
          )}
        />
        
        {/* Ícone de olho */}
        <button
          type="button"
          onClick={() => setShowPassword((prev) => !prev)} // Alterna o estado de visibilidade
          className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-500"
        >
          {showPassword ? <AiFillEyeInvisible size={20} /> : <AiFillEye size={20} />}
        </button>
      </div>

      {/* Exibe erro apenas se existir */}
      {error && <ErrorMessage error={error} />}
    </div>
  );
}
