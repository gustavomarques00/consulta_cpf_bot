"use client";

interface CpfListProps {
  cpfList: string[];
}

export default function CpfList({ cpfList }: CpfListProps) {
  return (
    <div className="mt-6 overflow-y-auto max-h-40 bg-gray-100 dark:bg-gray-700 p-4 rounded-lg">
      <h3 className="text-lg font-semibold text-gray-800 dark:text-white">CPFs Válidos:</h3>
      <ul className="text-gray-700 dark:text-gray-300 text-sm">
        {cpfList.map((cpf, index) => (
          <li key={index} className="border-b border-gray-300 dark:border-gray-600 py-1">{cpf}</li>
        ))}
      </ul>
    </div>
  );
}
