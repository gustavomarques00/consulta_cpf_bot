"use client";

import { FaFileUpload } from "react-icons/fa";

interface FileUploaderProps {
  onFileUpload: (event: React.ChangeEvent<HTMLInputElement>) => void;
}

export default function FileUploader({ onFileUpload }: FileUploaderProps) {
  return (
    <label className="w-full flex flex-col items-center p-4 border-2 border-dashed border-gray-300 dark:border-gray-600 rounded-lg cursor-pointer hover:border-indigo-500 transition">
      <FaFileUpload className="text-4xl text-gray-500 dark:text-gray-400 mb-2" />
      <span className="text-gray-600 dark:text-gray-300">Clique ou arraste um arquivo aqui</span>
      <input type="file" accept=".xlsx, .csv" className="hidden" onChange={onFileUpload} />
    </label>
  );
}
