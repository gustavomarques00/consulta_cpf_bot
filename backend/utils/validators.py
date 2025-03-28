import re

valid_user_types = ["Operador", "Chefe de Equipe", "Independente", "ADM"]

def is_valid_email(email: str) -> bool:
    regex = r'^\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b'
    return re.fullmatch(regex, email) is not None

def is_valid_phone(phone: str) -> bool:
    regex = r'^\(\d{2}\)\s?\d{4,5}-\d{4}$'
    return re.fullmatch(regex, phone) is not None

def verificar_cpf_existente(sheet_data, cpf):
    return cpf in sheet_data.get("cpfs_processados", [])

def is_valid_password(password: str) -> bool:
    return (
        len(password) >= 6 and
        re.search(r'[A-Z]', password) and
        re.search(r'\d', password) and
        re.search(r'[\W_]', password)
    )
