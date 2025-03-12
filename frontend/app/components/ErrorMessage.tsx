interface ErrorMessageProps {
    error: any;
  }
  
  export default function ErrorMessage({ error }: ErrorMessageProps) {
    return error ? <p className="text-red-500 text-sm">{error.message}</p> : null;
  }
  