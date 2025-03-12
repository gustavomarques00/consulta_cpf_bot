import { Controller } from "react-hook-form";

interface EmailInputProps {
  label: string;
  name: string;
  control: any;
  rules?: any;
  errors: any;
}

export default function EmailInput({
  label,
  name,
  control,
  rules,
  errors,
}: EmailInputProps) {
  return (
    <div>
      <label className="block text-sm font-medium text-gray-700">{label}</label>
      <Controller
        name={name}
        control={control}
        rules={rules}
        render={({ field }) => (
          <input
            type="email"
            {...field}
            className="w-full mt-2 p-3 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
            placeholder="Exemplo: email@dominio.com"
          />
        )}
      />
      {errors[name] && (
        <p className="text-red-500 text-sm">{errors[name]?.message}</p>
      )}
    </div>
  );
}
