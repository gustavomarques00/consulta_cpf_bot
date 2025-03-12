import { FieldError, FieldErrorsImpl, Merge } from "react-hook-form";

interface ErrorMessageProps {
  error?: FieldError | Merge<FieldError, FieldErrorsImpl<any>>;
}

export default function ErrorMessage({ error }: ErrorMessageProps) {
  if (!error || typeof error.message !== "string") return null;

  return (
    <p className="text-red-500 text-sm mt-1" aria-live="assertive">
      {error.message}
    </p>
  );
}
