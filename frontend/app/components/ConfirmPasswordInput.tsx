'use client';

import { Controller, Control, FieldErrors } from "react-hook-form";
import ErrorMessage from "./ErrorMessage";
import { IconType } from "react-icons"; // Suporte para ícones dinâmicos

interface ConfirmPasswordInputProps {
  label: string;
  name: string;
  control: Control<any>;
  rules: any;
  errors: FieldErrors<any>;
  watch: (field: string) => string; // Função watch para comparação de senhas
  Icon?: IconType; // Ícone opcional
}

export default function ConfirmPasswordInput({
  label,
  name,
  control,
  rules,
  errors,
  watch,
  Icon,
}: ConfirmPasswordInputProps) {
  const error = errors[name]; // Obtém o erro específico do campo, se houver

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
          rules={{
            ...rules,
            validate: (value: string) => {
              const password = watch("password");
              return value === password || "As senhas não coincidem";
            },
          }}
          render={({ field }) => {
            const fieldValue = field.value ?? ""; // Garantir que o valor seja controlado

            return (
              <input
                {...field}
                id={name}
                type="password"
                value={fieldValue}
                className={`w-full pl-10 pr-3 py-3 border rounded-md focus:outline-none focus:ring-2 ${error ? "border-red-500 focus:ring-red-500" : "border-gray-300 focus:ring-indigo-500"
                  }`}
                placeholder="Confirme sua senha"
                aria-invalid={error ? "true" : "false"}
                aria-describedby={error ? `${name}-error` : undefined}
              />
            );
          }}
        />
      </div>


      {/* Exibe erro apenas se existir */}
      {error && <ErrorMessage error={error} />}
    </div>
  );
}
