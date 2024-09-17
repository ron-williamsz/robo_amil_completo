import json
import os
from datetime import datetime
from google.oauth2.service_account import Credentials
import gspread

def atualizar_dados_planilha():
    SERVICE_ACCOUNT_FILE = r"C:\web\Python\Robo_Amil_completo\service_account.json"
    SCOPES = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
    JSON_FILE = 'dados_planilha.json'

    # Autenticação
    credentials = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    gc = gspread.authorize(credentials)

    # Abre a planilha e a primeira aba (worksheet)
    spreadsheet = gc.open_by_key(os.getenv('APPSHEET_APP_ID'))
    worksheet = spreadsheet.get_worksheet(0)

    all_data = worksheet.get_all_values()
    
    # Carrega os dados existentes do JSON
    if os.path.exists(JSON_FILE):
        with open(JSON_FILE, 'r', encoding='utf-8') as json_file:
            existing_data = json.load(json_file)
    else:
        existing_data = []

    json_data = []
    atualizacoes = 0

    # Itera sobre as linhas, começando da segunda (ignorando o cabeçalho)
    for i, row in enumerate(all_data[1:], start=2):
        row_data = {
            'COD': row[0],
            'ColB': row[1],
            'ColD': row[3],
            'Contrato': row[7],
            'ColI': row[8],
            'ColJ': row[9],
        }
        
        # Regras para pular linhas
        if row_data['COD'] == '' or row_data['COD'] == 'master.zangari':
            continue

        # Verifica se o registro já existe e se foi modificado
        existing_row = next((item for item in existing_data if item['COD'] == row_data['COD']), None)
        if existing_row is None or existing_row != row_data:
            atualizacoes += 1

        json_data.append(row_data)

    # Atualiza o arquivo JSON apenas se houver mudanças
    if atualizacoes > 0:
        with open(JSON_FILE, 'w', encoding='utf-8') as json_file:
            json.dump(json_data, json_file, ensure_ascii=False, indent=2)
        print(f"Arquivo JSON atualizado com {atualizacoes} modificações: {JSON_FILE}")
    else:
        print("Planilha atualizada. Nenhuma modificação necessária.")

    # Registra o log da verificação
    with open('atualizacao_log.txt', 'a', encoding='utf-8') as log_file:
        log_file.write(f"{datetime.now()}: Verificação concluída. {atualizacoes} atualizações realizadas.\n")

# Exemplo de uso:
atualizar_dados_planilha()