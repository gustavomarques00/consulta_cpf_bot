import { Controller } from "react-hook-form";

interface PasswordInputProps {
  label: string;
  name: string;
  control: any;
  rules: any;
  errors: any;
  watch: any; // Watch for password comparison
}

export default function PasswordInput({
  label,
  name,
  control,
  rules,
  errors,
  watch,
}: PasswordInputProps) {
  return (
    <div>
      <label className="block text-sm font-medium text-gray-700">{label}</label>
      <Controller
        name={name}
        control={control}
        rules={rules}
        render={({ field }) => (
          <input
            type="password"
            {...field}
            className="w-full mt-2 p-3 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
            placeholder="Sua senha"
          />
        )}
      />
      {errors[name] && (
        <p className="text-red-500 text-sm">{errors[name]?.message}</p>
      )}
    </div>
  );
}
