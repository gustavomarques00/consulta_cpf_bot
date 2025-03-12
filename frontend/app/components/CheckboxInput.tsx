import { Controller, Control, FieldErrors } from "react-hook-form";
import ErrorMessage from "./ErrorMessage";

interface CheckboxInputProps {
  label: string;
  name: string;
  control: Control<any>;
  rules?: any;
  errors: FieldErrors<any>;
}

export default function CheckboxInput({ label, name, control, rules, errors }: CheckboxInputProps) {
  const error = errors[name];

  return (
    <div className="w-full flex items-center space-x-2">
      <Controller
        name={name}
        control={control}
        rules={rules}
        render={({ field }) => (
          <input
            {...field}
            type="checkbox"
            id={name}
            checked={field.value}
            onChange={(e) => field.onChange(e.target.checked)}
            className="h-5 w-5 text-indigo-600 focus:ring-indigo-500 border-gray-300 rounded"
            aria-checked={field.value}
            aria-describedby={error ? `${name}-error` : undefined}
          />
        )}
      />

      <label htmlFor={name} className="text-sm font-medium text-gray-700 dark:text-gray-300">
        {label}
      </label>

      <ErrorMessage error={error} />
    </div>
  );
}
