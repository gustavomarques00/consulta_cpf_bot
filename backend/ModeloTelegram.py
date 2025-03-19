import time
import os
import random
import re
import gspread
import requests
from oauth2client.service_account import ServiceAccountCredentials
from config import Config  # Importando a classe de configuração

# Funções auxiliares

def autenticar_google_sheets():
    """Autentica no Google Sheets e retorna a planilha."""
    try:
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        creds = ServiceAccountCredentials.from_json_keyfile_name(Config.CREDENTIALS_FILE, scope)
        client = gspread.authorize(creds)
        return client.open(Config.SHEET_NAME)
    except Exception as e:
        print(f"❌ Erro na autenticação do Google Sheets: {e}")
        return None

def obter_data_hora():
    """Retorna a data e hora atual no formato 'DD/MM/YYYY HH:MM:SS'."""
    return time.strftime("%d/%m/%Y %H:%M:%S")

def extrair_info(pattern, resposta):
    """Extrai informação da resposta usando regex de forma segura."""
    match = re.search(pattern, resposta)
    return match.group(1).strip() if match else "Não Informado"

def remover_linha_checker(sheet_checker, cpf_processo):
    """Remove apenas a linha correspondente ao CPF processado na aba 'Checker'."""
    try:
        dados_checker = sheet_checker.get_all_values()
        if len(dados_checker) <= 1:
            print("⚠️ Nenhum dado encontrado na aba 'Checker'.")
            return

        for i, linha in enumerate(dados_checker[1:], start=2):
            if linha[0] == cpf_processo:
                sheet_checker.delete_rows(i)
                print(f"✅ CPF {cpf_processo} removido da aba 'Checker'.")
                return
        print(f"⚠️ CPF {cpf_processo} não encontrado na aba 'Checker'.")
    except Exception as e:
        print(f"❌ Erro ao remover CPF {cpf_processo}: {e}")

def reagendar_cpf_checker(sheet_checker, cpf_falha):
    """Reinsere um CPF na aba 'Checker' em uma posição aleatória caso a resposta não tenha sido obtida."""
    try:
        dados_checker = sheet_checker.get_all_values()
        posicao_aleatoria = random.randint(2, max(len(dados_checker), 2))
        sheet_checker.insert_row([cpf_falha], posicao_aleatoria)
        print(f"🔄 CPF {cpf_falha} foi reagendado para a posição {posicao_aleatoria}.")
    except Exception as e:
        print(f"❌ Erro ao reagendar CPF {cpf_falha}: {e}")

def obter_cpfs_da_aba_checker(sheet_checker):
    """Obtém todos os CPFs da aba 'Checker' para processamento."""
    try:
        dados_checker = sheet_checker.get_all_values()
        if len(dados_checker) <= 1:
            print("⚠️ Nenhum dado encontrado na aba 'Checker'.")
            return []
        cpfs = [linha[0] for linha in dados_checker[1:]]  # Ignora o cabeçalho
        return cpfs
    except Exception as e:
        print(f"❌ Erro ao obter CPFs da aba 'Checker': {e}")
        return []

def consultar_api(cpf):
    """Consulta a API para obter os dados do CPF."""
    url = f"https://hashirosearch.xyz/cpf.php?token={Config.API_TOKEN}&cpf={cpf}"
    try:
        response = requests.get(url)
        response.raise_for_status()  # Lança um erro se a resposta não for OK
        return response.json()  # Retorna o JSON da resposta
    except requests.exceptions.RequestException as e:
        print(f"❌ Erro na consulta à API para o CPF {cpf}: {e}")
        return None

def processar_cpf(cpf, sheet_data, sheet_checker):
    """Processa o CPF e atualiza os dados na planilha."""
    dados_api = consultar_api(cpf)
    contagem = 0  # Contador de tentativas de consulta à API
    print(f"ℹ️ Processando CPF {cpf}...")

    while not dados_api and contagem < Config.MAX_RETRIES:
        print(f"⚠️ Tentativa {contagem + 1} de consulta à API para {cpf}...")
        dados_api = consultar_api(cpf)
        contagem += 1
        time.sleep(Config.RETRY_DELAY)  # Aguarda um tempo antes de tentar novamente
    
    # Se após as tentativas, não houver dados, reagenda o CPF
    if not dados_api:
        print(f"⚠️ Erro contínuo ao obter dados para {cpf}. Verificando a causa...")
        reagendar_cpf_checker(sheet_checker, cpf)
        return

    # Agora, acessamos a estrutura correta, com base no retorno da API
    pessoa = dados_api  # O retorno da API já tem os dados no nível raiz

    # Extrair as informações com base na estrutura fornecida
    nome_info = pessoa.get("NOME", "Não Informado")
    cpf_info = pessoa.get("CPF", "Não Informado")
    nascimento_info = pessoa.get("NASCIMENTO", "Não Informado")
    
    # Ajustando o campo sexo
    sexo_info = pessoa.get("SEXO", "Indefinido")
    if sexo_info == "F":
        sexo_info = "Feminino"
    elif sexo_info == "M":
        sexo_info = "Masculino"
    else:
        sexo_info = "Indefinido"
    
    # Renda e poder aquisitivo
    renda_info = pessoa.get("RENDA", "Não Informado")
    poder_aquisitivo_info = pessoa.get("PODER_AQUISITIVO", "Não Informado")

    # Verifica se o campo de poder aquisitivo contém as palavras "BAIXA" ou "BAIXO" para definir o status
    status_info = "Não Enviada" if "BAIXA" in poder_aquisitivo_info.upper() or "BAIXO" in poder_aquisitivo_info.upper() or "SEM INFORMAÇÃO" in poder_aquisitivo_info.upper()  else "Enviada"
    
    # Extração de Email
    email_info = pessoa.get("EMAIL", [{"EMAIL": "Não Informado"}])[0].get("EMAIL", "Não Informado")
    
    # Telefone: Pegando o primeiro número de celular da lista
    telefone_info = pessoa.get("TELEFONES", [])
    telefone_final = telefone_info[0]["NUMBER"] if telefone_info else "Não Informado"

    # Processo de limpeza e formatação dos dados
    nome_split = nome_info.split()
    nome = nome_split[0] if nome_split else "Não Informado"
    sobrenome = " ".join(nome_split[1:]) if len(nome_split) > 1 else "Não Informado"

    # Preencher dados no Google Sheets
    data_hora_extracao = obter_data_hora()
    
    sheet_data.append_row([
        cpf_info, 
        nascimento_info, 
        email_info, 
        nome, 
        sobrenome, 
        telefone_final, 
        sexo_info, 
        renda_info, 
        poder_aquisitivo_info, 
        status_info, 
        data_hora_extracao
    ])

    # Remover linha do checker após o processamento
    remover_linha_checker(sheet_checker, cpf)

# Função principal para executar o processo
def main():
    sheet = autenticar_google_sheets()
    if sheet is None:
        print("❌ Erro na autenticação do Google Sheets!")
        return

    sheet_checker = sheet.worksheet(Config.WORKSHEET_CHECKER)
    sheet_data = sheet.worksheet(Config.WORKSHEET_DATA)

    cpfs = obter_cpfs_da_aba_checker(sheet_checker)
    if not cpfs:
        print("⚠️ Nenhum CPF encontrado para processar!")
        return

    for cpf in cpfs:
        processar_cpf(cpf, sheet_data, sheet_checker)
    print("✅ Processamento concluído!")

if __name__ == "__main__":
    main()
