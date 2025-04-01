import re

valid_user_types = ["Operador", "Chefe de Equipe", "Independente", "ADM"]


def is_valid_email(email: str) -> bool:
    regex = r"^\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b"
    return re.fullmatch(regex, email) is not None


def is_valid_phone(phone: str) -> bool:
    regex = r"^\(\d{2}\)\s?\d{4,5}-\d{4}$"
    return re.fullmatch(regex, phone) is not None


def verificar_cpf_existente(sheet_data, cpf):
    try:
        # Obtém todos os valores da aba 'Dados'
        dados = sheet_data.get_all_values()
        # Verifica se o CPF está na lista de CPFs processados
        cpfs_processados = [linha[0] for linha in dados[1:]]  # Ignora o cabeçalho
        return cpf in cpfs_processados
    except Exception as e:
        print(f"❌ Erro ao verificar se o CPF existe: {e}")
        return False


def is_valid_password(password: str) -> bool:
    return (
        len(password) >= 6
        and re.search(r"[A-Z]", password)
        and re.search(r"\d", password)
        and re.search(r"[\W_]", password)
    )


def validar_formato_cpf(cpf: str) -> bool:
    """Valida se o CPF tem formato correto e é matematicamente válido."""
    cpf = re.sub(r"\D", "", cpf)

    if len(cpf) != 11 or cpf == cpf[0] * 11:
        return False

    # Validação dos dígitos verificadores
    for i in range(9, 11):
        soma = sum(int(cpf[j]) * ((i + 1) - j) for j in range(i))
        digito = (soma * 10 % 11) % 10
        if digito != int(cpf[i]):
            return False

    return True


def traduzir_sexo(sexo):
    """Traduz o valor do campo SEXO para formato legível."""
    mapa = {"F": "Feminino", "M": "Masculino"}
    return mapa.get(sexo.upper(), "Indefinido")


def is_celular(numero):
    """Verifica se o número é um celular (9 no início do número local)."""
    numero = "".join(filter(str.isdigit, numero))  # Remove não-dígitos
    return len(numero) >= 10 and numero[-9] == "9"
