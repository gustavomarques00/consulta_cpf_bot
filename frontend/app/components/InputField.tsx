import { Controller } from "react-hook-form";

interface InputFieldProps {
  label: string;
  name: string;
  type: string;
  control: any;
  rules?: any;
  placeholder?: string;
  errors: any; // A propriedade errors agora é obrigatória
}

export default function InputField({
  label,
  name,
  type,
  control,
  rules,
  placeholder,
  errors,
}: InputFieldProps) {
  return (
    <div>
      <label className="block text-sm font-medium text-gray-700">{label}</label>
      <Controller
        name={name}
        control={control}
        rules={rules}
        render={({ field }) => (
          <input
            type={type} // A propriedade type agora é passada
            {...field}
            className="w-full mt-2 p-3 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
            placeholder={placeholder}
          />
        )}
      />
      {errors[name] && <p className="text-red-500 text-sm">{errors[name]?.message}</p>}
    </div>
  );
}