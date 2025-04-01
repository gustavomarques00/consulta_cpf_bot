import random
from utils.emoji import EMOJI


def autenticar_google_sheets(Config, gspread, ServiceAccountCredentials):
    try:
        scope = [
            "https://spreadsheets.google.com/feeds",
            "https://www.googleapis.com/auth/drive",
        ]
        creds = ServiceAccountCredentials.from_json_keyfile_name(
            Config.CREDENTIALS_FILE, scope
        )
        return gspread.authorize(creds)
    except Exception as e:
        print(f"{EMOJI['error']} Erro ao autenticar no Google Sheets: {e}")
        return None


def obter_cpfs_da_aba_checker(sheet_checker):
    try:
        linhas = sheet_checker.get_all_values()
        if len(linhas) <= 1:
            return []
        return [linha[0] for linha in linhas[1:]]
    except Exception as e:
        print(f"{EMOJI['error']} Erro ao obter CPFs: {e}")
        return []


def remover_linha_checker(sheet_checker, cpf):
    try:
        linhas = sheet_checker.get_all_values()
        for idx, linha in enumerate(linhas[1:], start=2):
            if linha[0] == cpf:
                sheet_checker.delete_rows(idx)
                print(f"{EMOJI['remove']} CPF {cpf} removido da aba 'Checker'.")
                return
        print(f"{EMOJI['warn']} CPF {cpf} não encontrado na aba 'Checker'.")
    except Exception as e:
        print(f"{EMOJI['error']} Erro ao remover CPF {cpf}: {e}")


def reagendar_cpf_checker(sheet_checker, cpf):
    try:
        linhas = sheet_checker.get_all_values()
        posicao = random.randint(2, max(len(linhas), 2))
        sheet_checker.insert_row([cpf], posicao)
        print(f"{EMOJI['loop']} CPF {cpf} reagendado para posição {posicao}.")
    except Exception as e:
        print(f"{EMOJI['error']} Erro ao reagendar CPF {cpf}: {e}")
