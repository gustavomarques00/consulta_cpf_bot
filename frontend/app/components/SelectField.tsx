import React from "react";
import { Controller, Control, FieldErrors } from "react-hook-form";
import { IconType } from "react-icons"; // Suporte para ícones dinâmicos

interface SelectFieldProps {
  label: string;
  name: string;
  control: Control<any>;
  errors: FieldErrors<any>;
  options: string[];
  rules?: any;
  placeholder?: string;
  onChange?: (value: string) => void; // Propriedade onChange adicionada
  Icon?: IconType;
}

export default function SelectField({
  label,
  name,
  control,
  errors,
  options,
  rules,
  placeholder,
  onChange, // Passando a função onChange como prop
  Icon,
}: SelectFieldProps) {
  const isError = Boolean(errors[name]); // Verifica se há erro

  return (
    <div className="w-full">
      <label htmlFor={name} className="block text-sm font-medium text-gray-700 dark:text-gray-300">
        {label}
      </label>

      <div className="relative">
        {Icon && <Icon className="absolute left-3 top-3 text-gray-500" size={20} />}

        <Controller
          name={name}
          control={control}
          rules={rules}
          render={({ field }) => (
            <select
              {...field}
              value={field.value ?? ""} // Vincula o valor ao React Hook Form
              onChange={(e) => {
                const value = e.target.value;
                field.onChange(value); // Atualiza o valor no React Hook Form
                if (onChange) {
                  onChange(value); // Chama a função onChange do componente, se passada como prop
                }
              }}
              id={name}
              className={`w-full pl-10 pr-3 py-3 border rounded-md focus:outline-none focus:ring-2 ${
                isError ? "border-red-500 focus:ring-red-500" : "border-gray-300 focus:ring-indigo-500"
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
