import { dirname } from "path";
import { fileURLToPath } from "url";
import { FlatCompat } from "@eslint/eslintrc";

// Obtendo o nome do arquivo e diretório atual
const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

// Configuração do FlatCompat
const compat = new FlatCompat({
  baseDirectory: __dirname,
});

// Configurações ESLint padrão para Next.js com TypeScript
const eslintConfig = [
  ...compat.extends("next/core-web-vitals", "next/typescript"), // Configurações padrão para Next.js e TypeScript
  {
    rules: {
      "react/react-in-jsx-scope": "off", // O React não precisa ser importado no Next.js com a versão 12+
      "no-console": "warn", // Avisar sobre o uso de console.log
      "react/prop-types": "off", // Desabilitar validação de props, pois estamos usando TypeScript
      "import/no-anonymous-default-export": "off", // Desabilitar importações anônimas
      "@typescript-eslint/no-unused-vars": ["warn"], // Avisar sobre variáveis não usadas
    },
  },
];

export default eslintConfig;
