import os
import glob
import re
from datetime import datetime
import shutil
import logging
import sys

BASE_DIR = 'G:\\Drives compartilhados\\AUTOMAÇÕES\\DP\\AMIL'

def get_condominio_name(nome_condominio):
    # Implemente esta função se ainda não estiver definida
    pass
def get_latest_invoice():
    # Padrão para os arquivos de fatura
    pattern = os.path.join(BASE_DIR, "RelFat1001E_*.pdf")
    
    # Lista todos os arquivos que correspondem ao padrão
    invoice_files = glob.glob(pattern)
    
    if not invoice_files:
        logging.warning("Nenhuma fatura encontrada.")
        return None
    
    # Função para extrair a data e hora do nome do arquivo
    def extract_datetime(filename):
        match = re.search(r'RelFat1001E_(\d{14})', filename)
        if match:
            date_str = match.group(1)
            return datetime.strptime(date_str, "%Y%m%d%H%M%S")
        return datetime.min
    
    # Encontra o arquivo mais recente baseado na data no nome do arquivo
    latest_invoice = max(invoice_files, key=extract_datetime)
    
    return latest_invoice

def get_condominio_name(nome_condominio):
    # Padrão para encontrar "edificio", "edif." ou "ed." (case insensitive)
    pattern = r'(?:edificio|edif\.|ed\.)\s+(.+)$'
    match = re.search(pattern, nome_condominio, re.IGNORECASE)
    if match:
        return match.group(1).strip()
    return nome_condominio  # Retorna o nome original se não encontrar o padrão

def renameMove(ultima_fatura, invoice_name, nome_condominio):
    logging.info(f"{invoice_name}, aqui: {ultima_fatura}, {nome_condominio}")
    logging.info(f"Renomeando {ultima_fatura} para {invoice_name} do condomínio {nome_condominio}")
    new_invoice_name = f"RelFat_{invoice_name}_{get_condominio_name(nome_condominio)}_{datetime.now().strftime('%Y%m%d%H%M%S')}.pdf"
    new_path = os.path.join(BASE_DIR, new_invoice_name)
    
    try:
        shutil.move(ultima_fatura, new_path)
        logging.info(f"Fatura renomeada com sucesso: {new_invoice_name}")
    except Exception as e:
        logging.error(f"Erro ao renomear a fatura: {str(e)}")

if __name__ == "__main__":
    # Configuração do logging
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    # Verifica se há argumentos suficientes
    if len(sys.argv) != 4:
        logging.error(f"Erro: Número incorreto de argumentos. Fornecidos {len(sys.argv) - 1}, esperados 3.")
        logging.error("Uso correto: python renameMove.py <ultima_fatura> <invoice_name> <nome_condominio>")
        sys.exit(1)

    ultima_fatura = sys.argv[1]
    invoice_name = sys.argv[2]
    nome_condominio = sys.argv[3]

    # Verifica se o arquivo da última fatura existe
    if not os.path.exists(ultima_fatura):
        logging.error(f"Erro: O arquivo da última fatura '{ultima_fatura}' não existe.")
        sys.exit(1)

    # Chama a função com os parâmetros
    renameMove(ultima_fatura, invoice_name, nome_condominio)


