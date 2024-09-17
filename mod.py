import os
import glob

BASE_DIR = 'G:\\Drives compartilhados\\AUTOMAÇÕES\\DP\\AMIL'

def remove_duplicate_invoices():
    # Padrão para encontrar arquivos de fatura
    pattern = os.path.join(BASE_DIR, "RelFat_*_*.pdf")
    invoice_files = glob.glob(pattern)
    
    # Dicionário para armazenar os arquivos por número
    invoices_dict = {}
    
    for file in invoice_files:
        # Extrai o número do arquivo
        file_name = os.path.basename(file)
        number = file_name.split('_')[1]  # Pega o número entre "RelFat_" e o próximo "_"
        
        if number in invoices_dict:
            invoices_dict[number].append(file)
        else:
            invoices_dict[number] = [file]
    
    # Remove arquivos duplicados
    for files in invoices_dict.values():
        if len(files) > 1:
            # Mantém o primeiro arquivo e remove os demais
            for file_to_remove in files[1:]:
                try:
                    os.remove(file_to_remove)
                    print(f"Arquivo removido: {file_to_remove}")
                except Exception as e:
                    print(f"Erro ao remover o arquivo {file_to_remove}: {str(e)}")

# Chama a função para remover arquivos duplicados
remove_duplicate_invoices()
