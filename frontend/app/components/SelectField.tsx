import React from "react";
import { Controller, Control, FieldErrors, RegisterOptions } from "react-hook-form";

interface SelectFieldProps {
  label: string;
  name: string;
  control: Control<any>;
  errors: FieldErrors<any>;
  options: string[];
  rules?: RegisterOptions;  // Adicionando 'rules' ao tipo
  placeholder?: string;
}

export default function SelectField({
  label,
  name,
  control,
  errors,
  options,
  rules, // Recebe as regras de validação
  placeholder,
}: SelectFieldProps) {
  const isError = !!errors[name]; // Verifica se há erro

  return (
    <div className="w-full">
      <label htmlFor={name} className="block text-sm font-medium text-gray-700 dark:text-gray-300">
        {label}
      </label>

      <div className="relative">
        <Controller
          name={name}
          control={control}
          rules={rules}  // Passando 'rules' para o Controller
          render={({ field }) => (
            <select
              {...field}
              id={name}
              className={`w-full pl-3 pr-10 py-3 border rounded-md focus:outline-none focus:ring-2 ${isError
                ? "border-red-500 focus:ring-red-500"
                : "border-gray-300 focus:ring-indigo-500"
                }`}
              aria-invalid={isError ? "true" : "false"}
              aria-describedby={isError ? `${name}-error` : undefined}
            >
              <option value="" disabled>
                {placeholder || "Selecione uma opção"}
              </option>
              {options.map((option, index) => (
                <option key={index} value={option}>
                  {option}
                </option>
              ))}
            </select>
          )}
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
