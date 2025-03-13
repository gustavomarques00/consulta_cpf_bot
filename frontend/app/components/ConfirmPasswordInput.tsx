'use client';

import { Controller, Control, FieldErrors } from "react-hook-form";
import ErrorMessage from "./ErrorMessage";

interface ConfirmPasswordInputProps {
  label: string;
  name: string;
  control: Control<any>;
  rules: any;
  errors: FieldErrors<any>;
  watch: (field: string) => string; // Função watch para comparação de senhas
}

export default function ConfirmPasswordInput({
  label,
  name,
  control,
  rules,
  errors,
  watch,
}: ConfirmPasswordInputProps) {
  const error = errors[name]; // Obtém o erro específico do campo, se houver

  return (
    <div className="w-full">
      <label htmlFor={name} className="block text-sm font-medium text-gray-700 dark:text-gray-300">
        {label}
      </label>

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
              className={`w-full mt-2 p-3 border rounded-md focus:outline-none focus:ring-2 text-black ${
                error ? "border-red-500 focus:ring-red-500" : "border-gray-300 focus:ring-indigo-500"
              }`}
              placeholder="Confirme sua senha"
              aria-invalid={error ? "true" : "false"}
              aria-describedby={error ? `${name}-error` : undefined}
            />
          );
        }}
      />

      {/* Exibe erro apenas se existir */}
      {error && <ErrorMessage error={error} />}
    </div>
  );
}
