import { Controller, Control, FieldErrors } from "react-hook-form";
import ErrorMessage from "./ErrorMessage";

interface EmailInputProps {
  label: string;
  name: string;
  control: Control<any>;
  rules?: any;
  errors: FieldErrors<any>;
}

export default function EmailInput({ label, name, control, rules, errors }: EmailInputProps) {
  const error = errors[name];

  return (
    <div className="w-full">
      <label htmlFor={name} className="block text-sm font-medium text-gray-700 dark:text-gray-300">
        {label}
      </label>

      <Controller
        name={name}
        control={control}
        rules={rules}
        render={({ field }) => (
          <input
            {...field}
            id={name}
            type="email"
            className={`w-full mt-2 p-3 border rounded-md focus:outline-none focus:ring-2 ${
              error ? "border-red-500 focus:ring-red-500" : "border-gray-300 focus:ring-indigo-500"
            }`}
            placeholder="Exemplo: email@dominio.com"
            aria-invalid={error ? "true" : "false"}
            aria-describedby={error ? `${name}-error` : undefined}
          />
        )}
      />

      <ErrorMessage error={error} />
    </div>
  );
}
