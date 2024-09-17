import time
import os
import logging
import json
from selenium import webdriver
import pyperclip
import shutil
import subprocess
import random
from datetime import datetime
import glob
import re
import subprocess
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, ElementClickInterceptedException, TimeoutException
from avisaDP import verificar_login_sucesso, enviar_email_login_incorreto, registrar_login_incorreto




# log_file_path = r"C:\web\Python\Robo_Amil_completo\output.log" # Caminho do arquivo de log
log_file_path = r"output.log"
logging.basicConfig(filename=log_file_path, level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')



# Adicione um handler para também exibir logs no console
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
console_handler.setFormatter(formatter)
logging.getLogger('').addHandler(console_handler)

# Teste o logging
logging.info("Iniciando o programa...")

BASE_DIR = 'G:\\Drives compartilhados\\AUTOMAÇÕES\\DP\\AMIL'



# Carregar dados do JSON
def carregar_dados_json():
    with open('dados_planilha.json', 'r', encoding='utf-8') as file:
        return json.load(file)

def get_contratos_amil():
    dados = carregar_dados_json()
    contratos_amil = [
        item for item in dados
        if 'AMIL' in item['ColD'].upper()
    ]
    if not contratos_amil:
        logging.warning("Nenhum contrato AMIL encontrado nos dados.")
    return contratos_amil

# Obter dados do JSON apenas para contratos AMIL
contratos_amil = get_contratos_amil()

if contratos_amil:
    amil_login = contratos_amil[0]['ColI']
    amil_password = contratos_amil[0]['ColJ']
    amil_condominio = contratos_amil[0]['ColB']
    login = amil_login
    senha = amil_password
    condominio_amil = amil_condominio
else:
    logging.error("Nenhum contrato AMIL encontrado. Não é possível obter login e senha.")
    exit()

print('aqui é teste')
print(amil_login)
print(amil_password)
print(condominio_amil)



def verificar_login_sucesso(driver):
    try:
        # Verifica se o elemento de erro de login está presente
        erro_login = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="login"]/div/div/section/section/div/section/p'))
        )
        erro_mensagem = erro_login.text
        print(f"Mensagem de erro: {erro_mensagem}")
        logging.error(f"Login falhou. Mensagem de erro encontrada: {erro_mensagem}")
        
        # Aciona o script avisadp.py
        subprocess.run(["python", "avisadp.py"])
        
        return False
    except TimeoutException:
        # Se o elemento de erro não for encontrado, assume que o login foi bem-sucedido
        logging.info("Login bem-sucedido.")
        return True


def setup_driver():
    logging.info("Setting up the WebDriver.")
    chrome_options = webdriver.ChromeOptions()
    driver_path = r"C:\web\chromedriver-win64\chromedriver-win64 (1)\chromedriver-win64\chromedriver.exe"
    service = Service(driver_path)
    
    chrome_options.add_argument("--start-maximized")
    
    # Set up for multiple downloads
    prefs = {
        "download.default_directory": BASE_DIR,
        "profile.default_content_setting_values.automatic_downloads": 1,  
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        # "download.default_directory": r"G:\Drives compartilhados\AUTOMAÇÕES\DP\AMIL",
        "plugins.always_open_pdf_externally": True,
        "safebrowsing.enabled": True
    }
    chrome_options.add_experimental_option("prefs", prefs)
    
    driver = webdriver.Chrome(service=service, options=chrome_options)
    return driver


def login_amil(driver, login, senha):
    logging.info(f"Tentando login com: {login}")
    driver.get("https://www.amil.com.br/empresa/#/login")
    time.sleep(10)
    logging.info("Entering login credentials.")
    driver.find_element(By.XPATH, '//*[@id="login"]/div/div/section/section/form/div[1]/div/div/div[1]/div/input').send_keys(login)
    driver.find_element(By.XPATH, '//*[@id="login"]/div/div/section/section/form/div[2]/div[1]/div/div/div[1]/div/input').send_keys(senha)
    driver.find_element(By.XPATH, '//*[@id="login"]/div/div/section/section/form/div[3]/div/div/button').click()
    time.sleep(10)
    
    return verificar_login_sucesso(driver)
def poppup_inicial(driver):
    try:
        logging.info("Verificando se o popup inicial está presente.")
        banner_xpath = '/html/body/div[3]/div/div[1]/div/div/div[1]/h5'
        close_button_xpath = '/html/body/div[3]/div/div[1]/div/div/div[3]/button'
        
        # Aguardando a visibilidade do popup
        WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.XPATH, banner_xpath))
        )
        
        logging.info("Popup encontrado, tentando fechar.")
        close_button = driver.find_element(By.XPATH, close_button_xpath)
        close_button.click()
        
        # Aguardando a invisibilidade do popup
        WebDriverWait(driver, 10).until(
            EC.invisibility_of_element_located((By.XPATH, banner_xpath))
        )
        logging.info("Popup fechado com sucesso.")
    
    except TimeoutException:
        logging.warning("O popup não apareceu dentro do tempo limite.")
    except NoSuchElementException:
        logging.warning("O botão de fechar do popup não foi encontrado.")
    except Exception as e:
        logging.error(f"Erro ao fechar o popup: {e}")

def close_policy_text(driver):
    try:
        banner_xpath = '//*[@id="onetrust-banner-sdk"]/div/div[1]/div'
        accept_button_xpath = '//*[@id="onetrust-accept-btn-handler"]'
        
        logging.info("Checking for the presence of the policy banner.")
        
        banner_present = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, banner_xpath)))
        
        if banner_present:
            logging.info("Policy banner found. Attempting to click the accept button.")
            WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, accept_button_xpath))).click()
            logging.info("Closed the policy text.")
        else:
            logging.info("Policy banner is not present.")
    except TimeoutException:
        logging.info("Timeout while waiting for the policy banner or accept button.")
    except NoSuchElementException:
        logging.info("Policy text not found.")
    except ElementClickInterceptedException:
        logging.warning("Element click intercepted while trying to close policy text.")
    except Exception as e:
        logging.error(f"An error occurred: {str(e)}")

def allow_multiple_downloads(driver):
    try:
        # Implementar lógica para permitir downloads múltiplos, se necessário
        pass
    except TimeoutException as e:
        logging.warning(f"Timeout while waiting for the multiple downloads prompt: {str(e)}")
    except NoSuchElementException as e:
        logging.warning(f"Multiple downloads prompt not found: {str(e)}")
    except ElementClickInterceptedException as e:
        logging.warning(f"Element click intercepted while trying to allow multiple downloads: {str(e)}")
    except Exception as e:
        logging.error(f"An error occurred: {str(e)}")


def verificar_login_sucesso(driver):
    try:
        # Aguarda até 10 segundos para o elemento aparecer após o login
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="app"]/div[2]/div[1]/div/div[3]/div[2]/nav/div/ul/div[3]/div[1]'))
        )
        logging.info("Login bem-sucedido.")
        return True
    except TimeoutException:
        logging.error("Login falhou. Elemento esperado não encontrado após 10 segundos.")
        return False

def navigate_to_demonstrativos(driver):
    try:
        logging.info("Tentando navegar para 'Gestão Financeira e Demonstrativos'.")
        WebDriverWait(driver, 15).until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="app"]/div[2]/div[1]/div/div[3]/div[2]/nav/div/ul/div[3]/div[1]'))
        ).click()
        time.sleep(5)
        
        logging.info("Tentando navegar para 'Demonstrativos Analítico do Faturamento'.")
        WebDriverWait(driver, 15).until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="app"]/div[2]/div[1]/div/div[3]/div[2]/nav/div/ul/div[3]/div[2]/ul/div/div[3]/a'))
        ).click()
        time.sleep(10)
        
        logging.info("Navegação para demonstrativos concluída com sucesso.")
    except Exception as e:
        logging.error(f"Erro ao navegar para demonstrativos: {str(e)}")
        raise  # Re-lança a exceção para ser capturada no bloco principal

def select_contrato(driver, contrato_code, nome_condominio):
    logging.info(f"Acionando ensure_contrato_selected para {contrato_code}, {nome_condominio}")
    return ensure_contrato_selected(driver, contrato_code, nome_condominio)

#bloco já modificado
def ensure_contrato_selected(driver, contrato_code, nome_condominio):
    logging.info(f"Verificando a melhor forma de selecionar o contrato: {contrato_code}")
    with open('dados_planilha.json', 'r', encoding='utf-8') as json_file:
        dados = json.load(json_file)

    # Localiza o COD relacionado ao contrato_code
    cod_encontrado = next((item.get('COD') for item in dados if item.get('Contrato') == contrato_code), None)
    if cod_encontrado:
        logging.info(f"COD: {cod_encontrado} tem o contrato: {contrato_code}.")
        time.sleep(10)

        # Verifica se há outros contratos com o mesmo COD
        contratos_com_mesmo_cod = [item for item in dados if item.get('COD') == cod_encontrado]
        if len(contratos_com_mesmo_cod) > 1:
            contratos_list = ', '.join(item.get('Contrato') for item in contratos_com_mesmo_cod)
            logging.info(f"COD: {cod_encontrado} possui os contratos: {contratos_list}.")
            time.sleep(10)
            return opcao_filtrar_contrato(driver, contrato_code, nome_condominio)
        else:
            logging.info(f"Um contrato encontrado com o COD: {cod_encontrado}. Usando opcao_unica. {nome_condominio}")
            time.sleep(10)
            return opcao_unica(driver, contrato_code, nome_condominio)
    else:
        logging.info(f"Nenhum contrato encontrado com o COD relacionado ao contrato: {contrato_code}. Usando opcao_unica.")
        return opcao_unica(driver, contrato_code, nome_condominio)
  
def opcao_filtrar_contrato(driver, contrato_code, nome_condominio):
    attempts = 0
    max_attempts = 3

    while attempts < max_attempts:
        logging.info(f"Tentativa {attempts + 1} de selecionar o contrato {contrato_code}.")
        
        try:
            # Clica no campo de entrada
            input_button_xpath = '/html/body/div[1]/div/div[2]/div[2]/div/div/form/div/div/div/div/div/div[1]/div/div[1]/div/div[1]/span/button'
            WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, input_button_xpath))).click()
            logging.info("input_button_xpath acionado")
            time.sleep(2)

            # Prepara o contrato_code para colar
            contrato_code_tratado = ''.join(filter(str.isdigit, contrato_code.replace('-', '').replace('.', '')))
            pyperclip.copy(contrato_code_tratado)
            logging.info(f"Contrato tratado preparado: {contrato_code_tratado}")

            # Tenta diferentes IDs para o campo de entrada
            for i in range(1, 17):
                try:
                    input_field_xpath = f'//div[@id="rw_{i}_input"]/div[2]/div/div/div/input'
                    input_field = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.XPATH, input_field_xpath)))
                    input_field.click()
                    input_field.clear()
                    input_field.send_keys(Keys.CONTROL, 'v')
                    time.sleep(2)
                    input_field.send_keys(Keys.ENTER)
                    input_field.send_keys(Keys.RETURN)
                    time.sleep(2)
                    break
                except:
                    continue
            else:
                raise Exception("Não foi possível encontrar o campo de entrada.")

            # input_field.send_keys(Keys.ENTER)
            # time.sleep(2)
            
            # Verifica se o contrato foi selecionado corretamente
            input_value_xpath = f'//div[@id="rw_{i}_input"]/div[1]/div'
            input_value = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, input_value_xpath))).text
            
            if contrato_code_tratado in input_value:
                logging.info(f"Contrato {contrato_code} selecionado com sucesso.")
                time.sleep(2)
                search_button = WebDriverWait(driver, 10).until(
                 EC.element_to_be_clickable((By.XPATH, '//*[@id="app"]/div[2]/div[2]/div/div/form/div/div/div/div/div/div[2]/div/button')))
                search_button.click()
                logging.info(f"Botão de pesquisa clicado para o contrato {contrato_code}.")
                time.sleep(3)
                # Aciona a função download_invoices em caso de sucesso
                download_invoices(driver, [(contrato_code, nome_condominio)], nome_condominio)
                return True
            else:
                logging.error(f"Contrato {contrato_code} não foi selecionado corretamente. Encontrado: {input_value}")
                attempts += 1
                time.sleep(2)
        
        except Exception as e:
            logging.error(f"Erro ao tentar selecionar o contrato {contrato_code}: {str(e)}")
            attempts += 1
            time.sleep(3)
    
    logging.error(f"Falha ao selecionar o contrato {contrato_code} após {max_attempts} tentativas.")
    opcao_unica(driver, contrato_code, nome_condominio)  # Aciona opcao_unica se falhar após as tentativas
    logging.info("Tentando acionar o opcao_unica pra contornar.")
    return False


def opcao_unica(driver, contrato_code, nome_condominio):
    try:
        time.sleep(2)
        search_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="app"]/div[2]/div[2]/div/div/form/div/div/div/div/div/div[2]/div/button'))
        )
        search_button.click()
        logging.info(f"Botão de pesquisa clicado para o contrato {contrato_code}.")
        time.sleep(3)
        
        # Se tiver sucesso, chama a rotina download_invoices
        if download_invoices(driver, [(contrato_code, nome_condominio)], nome_condominio):
            logging.info(f"Relatórios de fatura baixados com sucesso para o contrato {contrato_code}.")
        else:
            logging.error(f"Falha ao baixar relatórios de fatura para o contrato {contrato_code}.")
        
        return True
    except Exception as e:
        logging.error(f"Erro ao executar opcao_unica para o contrato {contrato_code}: {str(e)}")
        return False

def download_invoices(driver, contratos, nome_condominio):
    for contrato, nome_condominio in contratos:
        if check_if_contract_downloaded(contrato):
            logging.info(f"Contrato {contrato} já foi baixado anteriormente. Pulando.")
            continue

        logging.info(f"Iniciando download de faturas para o contrato: {contrato}, condomínio: {nome_condominio}.")
        logging.info(f"Processando faturas para o contrato: {contrato}, condomínio: {nome_condominio}.")

        page_number = 1
        downloaded_count = 0
        while True:
            try:
                logging.info("Clicando no botão de extração.")
                extraction_button = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, '//*[@id="app"]/div[2]/div[2]/div/div/div/div/div[2]/div/div[3]/div/div/button[1]'))
                )
                extraction_button.click()
                time.sleep(5)

                row_index = 1
                while row_index <= 10:
                    try:
                        xpath = f'//*[@id="app"]/div[2]/div[2]/div/div/div/div/div[3]/div/div/div[1]/div/table/tbody/tr[{row_index + 1}]/td[1]/a'
                        print(f"Número da linha atual: {row_index}")
                        link = WebDriverWait(driver, 10).until(
                            EC.element_to_be_clickable((By.XPATH, xpath))
                        )
                        invoice_name = link.text

                        logging.info(f"Baixando fatura: {invoice_name}.")
                        try:
                            link.click()
                            time.sleep(10)

                            # Aciona a função para obter a última fatura
                            ultima_fatura = get_latest_invoice_file()
                            if ultima_fatura:
                                logging.info(f"Última fatura identificada: {ultima_fatura}")
                                nome_condominio = get_condominio_name(nome_condominio)

                                # Chamando o script da subrotina renameMove e passando as variáveis como argumentos
                                result = subprocess.run([
                                    'python', 'renameMove.py', ultima_fatura, invoice_name, nome_condominio
                                ], capture_output=True, text=True)

                                # Verificando o resultado do subprocesso
                                if result.returncode == 0:
                                    logging.info(f"Subprocesso renomeMove executado com sucesso: {result.stdout}")
                                else:
                                    logging.error(f"Erro ao executar o subprocesso: {result.stderr}")

                            # Removido o código de renomeação da fatura
                            logging.info(f"Fatura {invoice_name} baixada com sucesso, assim que for baixada será renomeada.")

                        except NoSuchElementException:
                            break
                    except ElementClickInterceptedException:
                        logging.warning(f"Clique do elemento interceptado na linha {row_index}. Tentando novamente.")
                    except Exception as e:
                        logging.error(f"Erro ao processar fatura na linha {row_index}: {str(e)}")
                    finally:
                        row_index += 1
                
                if row_index > 10:  # Se o número da linha atual chegar a 10, vai para o próximo contrato
                    logging.info("Número máximo de linhas processadas atingido. Indo para o próximo contrato.")
                    break
                
                max_pages = 15
                last_page_number = 0
                while page_number <= max_pages:
                    logging.info(f"Tentando mover para a página {page_number + 1}.")
                    try:
                        next_page_xpath = f'//*[@id="app"]/div[2]/div[2]/div/div/div/div/div[3]/div/div/div[2]/div[2]/button[{page_number + 1}]'
                        next_page_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, next_page_xpath)))
                        next_page_button.click()
                        logging.info(f"Clicado no botão da página {page_number + 1}.")
                    except Exception as e:
                        logging.error(f"Erro ao clicar no botão da página {page_number + 1}: {str(e)}")
                        break
                    
                    try:
                        if 'disabled' in next_page_button.get_attribute('class'):
                            logging.info("Chegou à última página. Finalizando o download de faturas.")
                            break
                        next_page_button.click()
                        logging.info(f"Movido para a página {page_number + 1}.")
                        time.sleep(5)

                        current_page_number = page_number + 1
                        if current_page_number == last_page_number:
                            logging.warning("Ainda está na mesma página. Tentando novamente.")
                            break
                        last_page_number = current_page_number
                        page_number += 1
                    except NoSuchElementException:
                        logging.info("Não há mais páginas para navegar.")
                        break
                    except ElementClickInterceptedException:
                        logging.warning("Clique do elemento interceptado ao navegar entre páginas. Tentando novamente.")
                    except Exception as e:
                        logging.error(f"Ocorreu um erro ao processar faturas: {str(e)}")
                        break
                
                if page_number > max_pages:
                    logging.info(f"Atingido o limite máximo de {max_pages} páginas.")
                    
            except Exception as e:
                logging.error(f"Erro geral ao processar faturas para o contrato {contrato}: {str(e)}")
                break
            
            logging.info(f"Download e organização das faturas concluídos para o contrato {contrato}.")
        else:
            logging.info(f"Faturas para o contrato {contrato} já existem. Pulando.")

    logging.info("Processo de download de faturas concluído para todos os contratos.")
    return True



def extract_datetime(filename):
    match = re.search(r'RelFat1001E_(\d{14})', filename)
    if match:
        date_str = match.group(1)
        return datetime.strptime(date_str, "%Y%m%d%H%M%S")
    return datetime.min

def get_latest_invoice_file(invoice_name=None):
    pattern = os.path.join(BASE_DIR, "RelFat1001E_*.pdf")
    if invoice_name:
        pattern = os.path.join(BASE_DIR, f"RelFat1001E_*{invoice_name}*.pdf")
    
    invoice_files = glob.glob(pattern)
    
    if not invoice_files:
        logging.warning("Nenhuma fatura encontrada.")
        return None
    
    latest_invoice = max(invoice_files, key=extract_datetime)
    return latest_invoice

# Executa a função e imprime o resultado
latest = get_latest_invoice_file()
if latest:
    print(f"A fatura mais recente é: {os.path.basename(latest)}")
    print(f"Caminho completo: {latest}")
else:
    print("Não foi possível encontrar faturas recentes.")
    
def get_condominio_name(nome_condominio):
    # Padrão para encontrar "edificio", "edif." ou "ed." (case insensitive)
    pattern = r'(?:edificio|edif\.|ed\.)\s+(.+)$'
    match = re.search(pattern, nome_condominio, re.IGNORECASE)
    if match:
        return match.group(1).strip()
    return nome_condominio  # Retorna o nome original se não encontrar o padrão

def rename_latest_invoice(condominio_name, nome_condominio, invoice_name):
    pattern = os.path.join(BASE_DIR, "RelFat1001E_*.pdf")
    invoice_files = glob.glob(pattern)
    
    if not invoice_files:
        logging.warning("Nenhuma fatura encontrada.")
        print("Nenhuma fatura encontrada.")
        return None
    
    latest_invoice = max(invoice_files, key=extract_datetime)
    
    logging.info(f"A fatura mais recente é: {os.path.basename(latest_invoice)}")
    print(f"A fatura mais recente é: {os.path.basename(latest_invoice)}")
    
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    new_invoice_name = f"RelFat_{invoice_name}_{condominio_name}_{timestamp}.pdf"
    
    new_path = os.path.join(BASE_DIR, new_invoice_name)
    
    try:
        shutil.move(latest_invoice, new_path)
        logging.info(f"Fatura renomeada com sucesso: {new_invoice_name}")
        print(f"Fatura renomeada com sucesso: {new_invoice_name}")
    except Exception as e:
        logging.error(f"Erro ao renomear a fatura: {str(e)}")
        print(f"Erro ao renomear a fatura: {str(e)}")


pause_flag = False

def check_pause():
    global pause_flag
    while pause_flag:
        logging.info("Execução pausada. Aguardando...")
        time.sleep(3)

def check_if_contract_downloaded(invoice_name):
    directory = 'G:\\Drives compartilhados\\AUTOMAÇÕES\\DP\\AMIL'
    for filename in os.listdir(directory):
        if invoice_name in filename:
            return True
    return False
def get_contratos_amil():
    dados = carregar_dados_json()
    contratos_amil = [
        item
        for item in dados
        if 'AMIL' in item['ColD'].upper()
    ]
    if not contratos_amil:
        logging.warning("Nenhum contrato AMIL encontrado nos dados.")
    return contratos_amil

def main():
    driver = setup_driver()

    try:
        contratos_amil = get_contratos_amil()
        if not contratos_amil:
            logging.error("Nenhum contrato AMIL encontrado. Encerrando o programa.")
            return

        for contrato in contratos_amil:
            contrato_code = contrato['Contrato']
            nome_condominio = contrato['ColB']
            login = contrato['ColI']
            senha = contrato['ColJ']

            logging.info(f"Tentando processar contrato AMIL: {contrato_code}, condomínio: {nome_condominio}")

            try:
                if login_amil(driver, login, senha):
                    if verificar_login_sucesso(driver):
                        try:
                            close_policy_text(driver)
                            poppup_inicial(driver)
                            allow_multiple_downloads(driver)
                            navigate_to_demonstrativos(driver)

                            logging.info(f"Tentando selecionar contrato: {contrato_code}, condomínio: {nome_condominio}")
                            if select_contrato(driver, contrato_code, nome_condominio):
                                logging.info(f"Iniciando download de faturas para: {contrato_code}, condomínio: {nome_condominio}")
                                download_invoices(driver, [(contrato_code, nome_condominio)], nome_condominio)
                            else:
                                logging.error(f"Não foi possível selecionar o contrato: {contrato_code}")
                        except Exception as e:
                            logging.error(f"Erro ao processar contrato {contrato_code}: {str(e)}")
                            registrar_login_incorreto(nome_condominio, login, senha)
                    else:
                        logging.error(f"Falha na verificação de login para o condomínio: {nome_condominio}")
                        registrar_login_incorreto(nome_condominio, login, senha)
                else:
                    logging.error(f"Falha no login para o condomínio: {nome_condominio}")
                    registrar_login_incorreto(nome_condominio, login, senha)
            except Exception as e:
                logging.error(f"Erro inesperado ao processar contrato {contrato_code}: {str(e)}")
                registrar_login_incorreto(nome_condominio, login, senha)
            finally:
                # Logout ou reiniciar o navegador para o próximo login
                try:
                    driver.delete_all_cookies()
                    driver.get("about:blank")
                except Exception as e:
                    logging.error(f"Erro ao reiniciar o navegador: {str(e)}")
                    # Se falhar ao reiniciar, tenta criar um novo driver
                    driver.quit()
                    driver = setup_driver()
                    
        check_pause()
        
    except Exception as e:
        logging.error(f"Um erro inesperado ocorreu: {str(e)}")

    finally:
        logging.info("Execução finalizada. Fechando o WebDriver.")
        driver.quit()
        
        # Enviar e-mail com os logins incorretos
        enviar_email_login_incorreto()

if __name__ == "__main__":
    logging.info('Iniciando o programa...')
    main()
    logging.info('Programa finalizado.')
    
