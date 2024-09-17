import smtplib
from email.mime.text import MIMEText
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException 
import logging
from dotenv import load_dotenv
import os


# Obter o diretório do script atual
script_dir = os.path.dirname(os.path.abspath(__file__))
# Construir o caminho para o arquivo .env
dotenv_path = os.path.join(script_dir, '.env')
# Carregar as variáveis de ambiente do arquivo .env
load_dotenv(dotenv_path)

# Lista para armazenar os condomínios com login/senha incorretos
condominios_incorretos = []

def registrar_login_incorreto(nome_condominio, login, senha):
    condominios_incorretos.append({
        'nome': nome_condominio,
        'login': login,
        'senha': senha
    })
    logging.warning(f"Login incorreto registrado para o condomínio: {nome_condominio}")

def send_email(subject, to_email, message, cc_emails):
    smtp_server = os.getenv('SMTP_SERVER')
    smtp_port = 587
    smtp_user = os.getenv('SMTP_USER')
    smtp_password = os.getenv('SMTP_PASSWORD')
    
    msg = MIMEText(message)
    msg['From'] = smtp_user
    msg['To'] = to_email
    msg['Cc'] = ', '.join(cc_emails)
    msg['Subject'] = subject

    to_addresses = [to_email] + cc_emails

    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.ehlo()
            server.starttls()
            server.ehlo()
            server.login(smtp_user, smtp_password)
            server.sendmail(smtp_user, to_addresses, msg.as_string())
            logging.info(f'Email enviado com sucesso para {to_addresses}')
    except smtplib.SMTPException as e:
        logging.error(f'Falha ao enviar email: {e}')

def enviar_email_login_incorreto():
    if not condominios_incorretos:
        logging.info("Nenhum login incorreto para reportar.")
        return

    message = "Relatório de Logins Incorretos:\n\n"
    for condominio in condominios_incorretos:
        message += f"Condomínio: {condominio['nome']}, Login: {condominio['login']}, Senha: {condominio['senha']}\n"

    to_email = os.getenv('EMAIL_DESTINATARIO')
    cc_emails = [os.getenv('EMAIL_CC', '')]  # Adicione um e-mail CC se necessário
    subject = "Relatório de Logins Incorretos - Amil"

    send_email(subject, to_email, message, cc_emails)

def verificar_login_sucesso(driver, nome_condominio, login, senha):
    try:
        # Verifica se o elemento de erro de login está presente
        erro_login = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="login"]/div/div/section/section/div/section/p'))
        )
        logging.error("Login falhou. Mensagem de erro encontrada.")
        registrar_login_incorreto(nome_condominio, login, senha)
        return False
    except TimeoutException:
        # Se o elemento de erro não for encontrado, assume que o login foi bem-sucedido
        logging.info("Login bem-sucedido.")
        return True