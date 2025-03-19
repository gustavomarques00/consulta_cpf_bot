import React from "react";
import { Controller, Control, FieldErrors } from "react-hook-form"; // Certifique-se de importar o Controller
import { IconType } from "react-icons"; // Import IconType from react-icons

interface SelectFieldProps {
  label: string;
  name: string;
  control: Control<any>;
  errors: FieldErrors<any>;
  options: string[]; // Defina a propriedade `options` para o select
  rules?: any; // Validações adicionais
  placeholder?: string;
  onChange?: (value: string) => void; // Add onChange property
  Icon?: IconType; // Ícone opcional
}

export default function SelectField({
  label,
  name,
  control,
  errors,
  options,
  rules,
  Icon,
  placeholder,
}: SelectFieldProps) {
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
          rules={rules} // Passando 'rules' para o Controller
          render={({ field }) => (
            <select
            
              {...field}
              id={name}
              onChange={(e) => {
                field.onChange(e);
              }}
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
