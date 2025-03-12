import { Controller } from "react-hook-form";

// Componente de input de checkbox com o react-hook-form
export default function CheckboxInput({
  label,
  name,
  control,
  rules,
  errors,
}: {
  label: string;
  name: string;
  control: any;
  rules?: any;
  errors: any;
}) {
  return (
    <div>
      <label className="block text-sm font-medium text-gray-700">{label}</label>
      <Controller
        name={name}
        control={control}
        rules={rules}
        render={({ field }) => (
          <input
            type="checkbox"
            {...field}
            checked={field.value} // Aqui controlamos o estado do checkbox usando `field.value`
            onChange={(e) => field.onChange(e.target.checked)} // Passamos o valor correto de `checked`
            className="w-full mt-2 p-3 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
          />
        )}
      />
      {errors[name] && <p className="text-red-500 text-sm">{errors[name]?.message}</p>}
    </div>
  );
}
