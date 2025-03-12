import { Controller } from "react-hook-form";

interface ConfirmPasswordInputProps {
  label: string;
  name: string;
  control: any;
  rules: any;
  errors: any;
  watch: any; // watch será passado como função
}

export default function ConfirmPasswordInput({
  label,
  name,
  control,
  rules,
  errors,
  watch,
}: ConfirmPasswordInputProps) {
  return (
    <div>
      <label className="block text-sm font-medium text-gray-700">{label}</label>
      <Controller
        name={name}
        control={control}
        rules={{
          ...rules,
          validate: (value: string) => value === watch("password") || "As senhas não coincidem", // Aqui usaremos o watch corretamente
        }}
        render={({ field }) => (
          <input
            type="password"
            {...field}
            className="w-full mt-2 p-3 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
            placeholder="Confirme sua senha"
          />
        )}
      />
      {errors[name] && <p className="text-red-500 text-sm">{errors[name]?.message}</p>}
    </div>
  );
}
