import time
import os
import random
import re
import gspread
import requests
from oauth2client.service_account import ServiceAccountCredentials
from config import Config  # Importando a classe de configuração

# Funções auxiliares

def autenticar_outra_planilha(sheet_name):
    """Autentica uma nova planilha do Google Sheets e retorna a referência à planilha especificada."""
    try:
        # Utiliza a mesma autenticação com o arquivo de credenciais já fornecido
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        creds = ServiceAccountCredentials.from_json_keyfile_name(Config.CREDENTIALS_FILE, scope)
        client = gspread.authorize(creds)
        
        # Abre a nova planilha pelo nome
        return client.open(sheet_name)
    except Exception as e:
        print(f"❌ Erro na autenticação da nova planilha {sheet_name}: {e}")
        return None

def obter_dados_outra_planilha(sheet_name, worksheet_name):
    """Obtém os CPFs da coluna H na aba 'Dados Twizzy' da planilha específica."""
    try:
        # Autentica e abre a planilha específica pelo ID
        client = autenticar_google_sheets()
        if not client:
            return []

        # Abre a planilha pelo ID e acessa a aba específica
        planilha = client.open_by_key(sheet_id)
        worksheet = planilha.worksheet(worksheet_name)
        
        # Obtém os dados da coluna H (CPF) na aba 'Dados Twizzy'
        dados = worksheet.col_values(8)  # Coluna H é a coluna 8 (começa em 1)
        
        # Filtra CPFs válidos (apenas números e com 11 dígitos)
        cpfs_validos = [cpf for cpf in dados if re.match(r'^\d{11}$', cpf)]
        return cpfs_validos
    except Exception as e:
        print(f"❌ Erro ao acessar os dados da planilha: {e}")
        return []

def processar_dados_de_outra_planilha(sheet_data, sheet_name, worksheet_name):
    """Processa os dados de outra planilha e os insere na planilha 'Data'."""
    dados_outra_planilha = obter_dados_outra_planilha(sheet_name, worksheet_name)
    
    if not dados_outra_planilha:
        print("⚠️ Nenhum dado encontrado na planilha de origem.")
        return

    # Aqui você pode implementar a lógica para processar os dados da outra planilha
    # Vamos supor que você queira apenas copiar para a planilha 'Data'.
    for linha in dados_outra_planilha:
        # Faça o processamento necessário (como transformar dados, validar, etc.)
        # Exemplo: Adicionando uma nova linha na planilha 'Data'
        sheet_data.append_row(linha)

    print("✅ Dados da outra planilha processados e adicionados na 'Data'.")

def autenticar_google_sheets():
    """Autentica no Google Sheets e retorna a planilha."""
    try:
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        creds = ServiceAccountCredentials.from_json_keyfile_name(Config.CREDENTIALS_FILE, scope)
        client = gspread.authorize(creds)
        return client
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
    """Obtém todos os CPFs da aba 'Checker' para processamento, filtrando valores vazios ou inválidos."""
    try:
        dados_checker = sheet_checker.get_all_values()
        if len(dados_checker) <= 1:
            print("⚠️ Nenhum dado encontrado na aba 'Checker'.")
            return []
        
        # Filtrando CPFs válidos e não vazios
        cpfs = [linha[0] for linha in dados_checker[1:] if linha[0] and re.match(r'^\d{11}$', linha[0])]  # Valida o CPF com 11 dígitos
        return cpfs
    except Exception as e:
        print(f"❌ Erro ao obter CPFs da aba 'Checker': {e}")
        return []

def verificar_cpf_existente(sheet_data, cpf):
    """Verifica se o CPF já existe na aba 'Dados'. Retorna True se existir, False caso contrário."""
    try:
        dados_data = sheet_data.get_all_values()
        for linha in dados_data[1:]:  # Ignora o cabeçalho
            if linha[0] == cpf:
                return True  # CPF já existe na aba 'Dados'
        return False  # CPF não existe na aba 'Dados'
    except Exception as e:
        print(f"❌ Erro ao verificar CPF na aba 'Dados': {e}")
        return False

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
    """Processa o CPF e atualiza os dados na planilha, com verificação de duplicidade."""
    # Verificar se o CPF já foi processado
    if verificar_cpf_existente(sheet_data, cpf):
        print(f"ℹ️ CPF {cpf} já foi processado anteriormente. Pulando...")
        return  # Se o CPF já foi processado, pula o processamento

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
    status_info = "Não Enviada" if "BAIXA" in poder_aquisitivo_info.upper() or "BAIXO" in poder_aquisitivo_info.upper() or "SEM INFORMAÇÃO" in poder_aquisitivo_info.upper() else "Enviada"
    
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
    # Autentica e abre a planilha principal pelo nome ou ID
    sheet = autenticar_google_sheets()
    if sheet is None:
        print("❌ Erro na autenticação do Google Sheets!")
        return

    # Agora vamos acessar as abas específicas dentro da planilha
    try:
        sheet_checker = sheet.open(Config.SHEET_NAME).worksheet(Config.WORKSHEET_CHECKER)
        sheet_data = sheet.open(Config.SHEET_NAME).worksheet(Config.WORKSHEET_DATA)
    except Exception as e:
        print(f"❌ Erro ao acessar as abas: {e}")
        return

    # Obter CPFs da aba 'Checker'
    cpfs = obter_cpfs_da_aba_checker(sheet_checker)
    if not cpfs:
        print("⚠️ Nenhum CPF encontrado para processar!")
        return

    # Processar CPFs da aba 'Checker'
    for cpf in cpfs:
        processar_cpf(cpf, sheet_data, sheet_checker)
    print("✅ Processamento dos CPFs concluído!")

    # ID da planilha de dados Twizzy (obtido do link compartilhado)
    sheet_id = "1u11Btk8RdNTZRnmbBYjs3gWE1rQYgXS8x3LLWpw4ils"
    worksheet_name = "Dados Twizzy"  # Nome da aba na planilha

    # Obter CPFs da coluna H da aba 'Dados Twizzy'
    cpfs_twizzy = obter_dados_outra_planilha(sheet_id, worksheet_name)
    if not cpfs_twizzy:
        print("⚠️ Nenhum CPF encontrado na planilha 'Dados Twizzy'.")
        return

    print(f"⚙️ CPFs encontrados na planilha 'Dados Twizzy': {cpfs_twizzy}")
    # Aqui você pode adicionar a lógica de processar esses CPFs como desejar.

if __name__ == "__main__":
    main()