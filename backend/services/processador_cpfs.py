from datetime import datetime
import time
from utils.validators import (
    validar_formato_cpf,
    traduzir_sexo,
    is_celular,
    verificar_cpf_existente,
)
from services.google_sheets_service import (
    autenticar_google_sheets,
    obter_cpfs_da_aba_checker,
    remover_linha_checker,
    reagendar_cpf_checker,
)
from services.extracao_api import consultar_api, tratar_valor
from utils.request_tracker import mostrar_resumo_requisicoes
from core.config import Config
import gspread  # type: ignore
from oauth2client.service_account import ServiceAccountCredentials  # type: ignore
from utils.emoji import EMOJI


def processar_cpf(cpf, sheet_data, sheet_checker):
    print(f"\n{EMOJI['step']} Iniciando processamento do CPF: {cpf}")

    if not validar_formato_cpf(cpf):
        print(f"{EMOJI['error']} CPF {cpf} é inválido no formato. Pulando...")
        return

    if verificar_cpf_existente(sheet_data, cpf):
        print(f"{EMOJI['info']} CPF {cpf} já foi processado anteriormente.")
        return

    dados = consultar_api(
        cpf, Config, sheet_checker=sheet_checker, reagendar_func=reagendar_cpf_checker
    )
    if not dados:
        print(f"{EMOJI['warn']} Nenhum dado retornado para CPF {cpf}")
        return

    nome_completo = tratar_valor(dados.get("NOME", ""))
    nome_partes = nome_completo.split()
    nome = nome_partes[0] if nome_partes else "Não Informado"
    sobrenome = " ".join(nome_partes[1:]) if len(nome_partes) > 1 else "Não Informado"
    nascimento = tratar_valor(dados.get("NASCIMENTO", ""))
    sexo = traduzir_sexo(tratar_valor(dados.get("SEXO", "")))
    renda = tratar_valor(dados.get("RENDA", ""))
    poder_aquisitivo = tratar_valor(dados.get("PODER_AQUISITIVO", ""))
    status = (
        "Não Enviada"
        if poder_aquisitivo == "Não Informado" or "BAIXO" in poder_aquisitivo.upper()
        else "Enviada"
    )

    telefone = "Não Informado"
    for tel in dados.get("TELEFONES", []):
        numero = tratar_valor(tel.get("NUMBER", ""))
        if is_celular(numero):
            telefone = numero
            break

    email = "Não Informado"
    for e in dados.get("EMAIL", []):
        email_raw = tratar_valor(e.get("EMAIL", ""))
        if email_raw != "Não Informado" and "@" in email_raw:
            email = email_raw
            break

    linha = [
        cpf,
        nascimento,
        email,
        nome,
        sobrenome,
        telefone,
        sexo,
        renda,
        poder_aquisitivo,
        status,
        time.strftime("%Y-%m-%d %H:%M:%S"),
    ]

    try:
        sheet_data.append_row(linha)
        remover_linha_checker(sheet_checker, cpf)
        print(f"{EMOJI['ok']} CPF {cpf} processado e salvo com sucesso.")
    except Exception as e:
        print(f"{EMOJI['error']} Erro ao salvar dados para CPF {cpf}: {e}")


def processar_lote_cpfs(cpfs, sheet_data, sheet_checker, batch_size=10):
    for i in range(0, len(cpfs), batch_size):
        lote = cpfs[i : i + batch_size]
        print(
            f"\n{EMOJI['batch']} Processando lote {i // batch_size + 1}: {len(lote)} CPFs"
        )
        for cpf in lote:
            processar_cpf(cpf, sheet_data, sheet_checker)
        print(
            f"{EMOJI['clock']} Aguardando {Config.RETRY_DELAY}s antes do próximo lote...\n"
        )
        time.sleep(Config.RETRY_DELAY)


def main():
    print(f"{EMOJI['info']} Iniciando automação via API")
    mostrar_resumo_requisicoes()

    sheet = autenticar_google_sheets(Config, gspread, ServiceAccountCredentials)
    if not sheet:
        return

    try:
        sheet_checker = sheet.open(Config.SHEET_NAME).worksheet(
            Config.WORKSHEET_CHECKER
        )
        sheet_data = sheet.open(Config.SHEET_NAME).worksheet(Config.WORKSHEET_DATA)
    except Exception as e:
        print(f"{EMOJI['error']} Erro ao abrir planilhas: {e}")
        return

    cpfs = obter_cpfs_da_aba_checker(sheet_checker)
    if not cpfs:
        print(f"{EMOJI['warn']} Nenhum CPF encontrado para processar.")
        return

    processar_lote_cpfs(cpfs, sheet_data, sheet_checker)
    print(f"{EMOJI['ok']} Todos os CPFs foram processados com sucesso.")


if __name__ == "__main__":
    main()
