"use client";

import { Controller, Control, FieldErrors } from "react-hook-form";

interface InputFieldProps {
  label: string;
  name: string;
  type?: "text" | "email" | "password" | "number" | "textarea";
  control: Control<any>;
  rules?: any;
  placeholder?: string;
  errors: FieldErrors<any>;
}

export default function InputField({
  label,
  name,
  type = "text",
  control,
  rules,
  placeholder,
  errors,
}: InputFieldProps) {
  const isError = !!errors[name]; // Verifica se há erro

  return (
    <div className="w-full">
      <label htmlFor={name} className="block text-sm font-medium text-gray-700 dark:text-gray-300">
        {label}
      </label>

      <Controller
        name={name}
        control={control}
        rules={rules}
        render={({ field }) => {
          // Garantir que o valor seja definido. Se `field.value` for `undefined`, use uma string vazia
          const fieldValue = field.value ?? ""; // Usando o operador nullish coalescing (??) para garantir que o valor seja controlado

          return type === "textarea" ? (
            <textarea
              {...field}
              id={name}
              value={fieldValue} // Garantir que o valor seja controlado
              placeholder={placeholder}
              className={`w-full mt-2 p-3 border rounded-md focus:outline-none focus:ring-2 ${
                isError ? "border-red-500 focus:ring-red-500" : "border-gray-300 focus:ring-indigo-500"
              } text-black`} // Aqui, a classe `text-black` garante o texto preto
              rows={4}
              aria-invalid={isError ? "true" : "false"}
              aria-describedby={isError ? `${name}-error` : undefined}
            />
          ) : (
            <input
              {...field}
              id={name}
              type={type}
              value={fieldValue} // Garantir que o valor seja controlado
              placeholder={placeholder}
              className={`w-full mt-2 p-3 border rounded-md focus:outline-none focus:ring-2 ${
                isError ? "border-red-500 focus:ring-red-500" : "border-gray-300 focus:ring-indigo-500"
              } text-black`} // Aqui, a classe `text-black` garante o texto preto
              aria-invalid={isError ? "true" : "false"}
              aria-describedby={isError ? `${name}-error` : undefined}
            />
          );
        }}
      />

      {isError && (
        <p id={`${name}-error`} className="text-red-500 text-sm mt-1">
          {errors[name]?.message as string}
        </p>
      )}
    </div>
  );
}
