import React, { useState } from "react";
import { Controller, Control, FieldErrors } from "react-hook-form";
import { AiFillEye, AiFillEyeInvisible } from "react-icons/ai"; // Ícones de olho

interface PasswordInputProps {
  label: string;
  name: string;
  control: Control<any>;
  errors: FieldErrors<any>;
  rules?: any;
}

export default function PasswordInput({
  label,
  name,
  control,
  errors,
  rules,
}: PasswordInputProps) {
  const [showPassword, setShowPassword] = useState(false); // Controla a visibilidade da senha
  const isError = Boolean(errors[name]); // Verifica se há erro

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
              value={field.value ?? ""} // Garante que o valor seja sempre uma string (evita undefined)
              onChange={(e) => field.onChange(e.target.value)} // Atualiza o valor do formulário
              className={`w-full pl-3 pr-3 py-3 border rounded-md focus:outline-none focus:ring-2 ${isError
                ? "border-red-500 focus:ring-red-500"
                : "border-gray-300 focus:ring-indigo-500"
                }`}
              aria-invalid={isError ? "true" : "false"}
              aria-describedby={isError ? `${name}-error` : undefined}
            />
          )}
        />
        <button
          type="button"
          onClick={() => setShowPassword((prev) => !prev)} // Alterna o estado de visibilidade
          className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-500"
        >
          {showPassword ? <AiFillEyeInvisible size={20} /> : <AiFillEye size={20} />}
        </button>
      </div>

      {isError && (
        <p id={`${name}-error`} className="text-red-500 text-sm mt-1">
          {errors[name]?.message as string}
        </p>
      )}
    </div>
  );
}




