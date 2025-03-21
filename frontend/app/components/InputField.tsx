"use client";

import { Controller, Control, FieldErrors } from "react-hook-form";
import { IconType } from "react-icons"; // Suporte para ícones dinâmicos

interface InputFieldProps {
  label: string;
  name: string;
  type?: "text" | "email" | "password" | "number" | "textarea" | "tel";
  control: Control<any>;
  rules?: any;
  placeholder?: string;
  disabled?: boolean;
  errors: FieldErrors<any>;
  Icon?: IconType; // Ícone opcional
}

export default function InputField({
  label,
  name,
  type = "text",
  control,
  rules,
  disabled,
  placeholder,
  errors,
  Icon,
}: InputFieldProps) {
  const isError = !!errors[name]; // Verifica se há erro

  return (
    <div className="w-full">
      <label htmlFor={name} className="block text-sm font-medium text-gray-700 dark:text-gray-300">
        {label}
      </label>

      <div className="relative">
        {/* Ícone dentro do input */}
        {Icon && <Icon className="absolute left-3 top-3 text-gray-500" size={20} />}

        <Controller
          name={name}
          control={control}
          rules={rules}
          render={({ field }) => {
            return type === "textarea" ? (
              <textarea
                {...field}  // Não precisa passar "value" explicitamente
                id={name}
                disabled={disabled}
                placeholder={placeholder}
                className={`w-full pl-10 pr-3 py-3 border rounded-md focus:outline-none focus:ring-2 ${isError ? "border-red-500 focus:ring-red-500" : "border-gray-300 focus:ring-indigo-500"
                  }`}
                rows={4}
                aria-invalid={isError ? "true" : "false"}
                aria-describedby={isError ? `${name}-error` : undefined}
              />
            ) : (
              <input
                {...field}  // "field" já inclui o valor do campo
                id={name}
                disabled={disabled}
                type={type}
                placeholder={placeholder}
                className={`w-full pl-10 pr-3 py-3 border rounded-md focus:outline-none focus:ring-2 ${isError ? "border-red-500 focus:ring-red-500" : "border-gray-300 focus:ring-indigo-500"
                  }`}
                aria-invalid={isError ? "true" : "false"}
                aria-describedby={isError ? `${name}-error` : undefined}
              />
            );
          }}
        />

      </div>

      {/* Exibe erro apenas se existir */}
      {isError && (
        <p id={`${name}-error`} className="text-red-500 text-sm mt-1">
          {errors[name]?.message as string}
        </p>
      )}
    </div>
  );
}
