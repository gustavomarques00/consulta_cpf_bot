import { FC } from "react";
import Link from "next/link";
import { IconType } from "react-icons";

interface SidebarLinkProps {
  to?: string; // Tornando a propriedade `to` opcional
  icon: IconType; // Ícone do react-icons
  label: string; // Texto da categoria
  isSidebarOpen: boolean; // Se o menu está expandido ou não
}

const SidebarLink: FC<SidebarLinkProps> = ({ to, icon: Icon, label, isSidebarOpen }) => {
  const LinkContent = (
    <>
      <Icon size={40} />
      {/* Exibe o texto apenas se a sidebar estiver expandida ou se o hover estiver ativo */}
      <span
        className={`ml-4 text-2xl font-semibold text-white transition-all duration-300 group-hover:text-indigo-300 ${isSidebarOpen ? "block" : "hidden"}`}
      >
        {label}
      </span>
    </>
  );

  return (
    <li className="relative group">
      {/* Item de navegação com separação */}
      {to ? (
        <Link href={to} className="hover:text-indigo-200 block text-lg flex items-center py-2">
          {LinkContent}
        </Link>
      ) : (
        <div className="hover:text-indigo-200 block text-lg flex items-center py-2">
          {LinkContent}
        </div>
      )}
      {/* Divisória após cada item */}
      <div className="border-t border-indigo-500 mt-2"></div>

      {/* Tooltip (balão de texto) que aparece ao passar o mouse à direita do ícone */}
      <span className="absolute left-full ml-2 top-1/2 transform -translate-y-1/2 hidden group-hover:block bg-indigo-500 text-white text-sm rounded-lg py-1 px-3 shadow-lg">
        {label}
      </span>
    </li>
  );
};

export default SidebarLink;
