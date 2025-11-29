# smb-attack
Simulação de ataque em cadeia - enumeração smb + password spraying 
# DevSecOps Lab: Ataque de Força Bruta em Serviço de Arquivos (SMB)

Este repositório documenta um projeto prático de auditoria de segurança realizado em um ambiente de laboratório isolado (Kali Linux e Metasploitable 2), focando na metodologia **"Shift-Left"** (mover a segurança para a esquerda) do DevSecOps.

## Objetivo Educacional

O principal objetivo deste projeto é **compreender, simular e propor defesas** contra ataques de **Enumeração e Força Bruta** no serviço de compartilhamento de arquivos **SMB** (Server Message Block). O foco está em:

1.  **Uso Ético de Ferramentas:** Utilizar o **enum4linux** para coleta de informações e o **Medusa** para automação de *password spraying* em ambientes controlados.
2.  **Desenvolvimento Seguro:** Entender as vulnerabilidades do SMB que permitem a enumeração de usuários e a quebra de senhas.
3.  **Mitigação Prática:** Documentar e implementar os controles de segurança mais eficazes para prevenir ataques SMB.

## Arquitetura do Laboratório

Todos os testes foram realizados em um ambiente de máquinas virtuais (VMs) isolado usando o VirtualBox, configurado com uma rede **Host-Only** para garantir que nenhuma atividade de teste afetasse redes externas ou sistemas de terceiros.

* **Máquina Atacante:** Kali Linux (Contém o Medusa, enum4linux, Python, e Bash scripts)
* **Máquina Alvo:** Metasploitable 2 (Serviços SMB vulneráveis)
* **Rede:** Host-Only (Ex: 192.168.15.0/24)

## Scripts Implementados

Foram criados e utilizados scripts interativos em **Bash** e **Python** para automatizar o processo de teste, garantindo a criação de *wordlists* de senhas e usuários personalizadas.

| Script | Serviço Alvo | Linguagem | Ação Principal |
| :--- | :--- | :--- | :--- |
| `smb_attack.py` | SMB (Módulos `enum4linux` e `smbnt` do Medusa) | Python | Executa enumeração de usuários, cria listas e tenta *password spraying* contra a porta 445/139. |
| `smb_attack.sh` | SMB (Módulos `enum4linux` e `smbnt` do Medusa) | Bash | Executa enumeração de usuários, cria listas e tenta *password spraying* contra a porta 445/139. |

---

## Detalhamento dos Comandos de Teste (Enumeração e Força Bruta SMB)

Esta seção documenta a preparação, enumeração e a sintaxe de ataque utilizada para simular a Força Bruta SMB no ambiente de laboratório.

### 1. Enumeração de Usuários (Reconhecimento)

A ferramenta **`enum4linux`** é usada para tentar extrair listas de usuários, grupos e informações de compartilhamento do serviço SMB.

| Comando de Exemplo | Descrição |
| :--- | :--- |
| `enum4linux -a <ip-do-alvo> | tee enum4-output.txt` | Executa todas as opções de enumeração (`-a`) e salva a saída no arquivo `enum4-output.txt` para análise e extração de usuários. |

### 2. Criação da Lista de Usuários e Senhas (*Wordlists*)

As listas são criadas com usuários padrão e senhas comuns, sendo a lista de usuários aprimorada com dados da etapa de enumeração.

| Comando de Exemplo | Descrição |
| :--- | :--- |
| `echo -e "user\nmsfadmin\nservice" > smb-users.txt` | Cria a lista de usuários baseada em suposições iniciais ou usuários enumerados. |
| `echo -e "password\n123456\nWelcome123\nmsfadmin" > smb-pass-spray.txt` | Cria uma lista de senhas curtas para o ataque de *password spraying*. |

### 3. Execução do Ataque de Força Bruta (Medusa)

O Medusa é usado no modo de *password spraying* (`-T` alto, `-t` baixo) para testar uma pequena lista de senhas contra uma grande lista de usuários.

#### Comando de Exemplo (Módulo SMB)

| Comando de Exemplo | Descrição da Sintaxe |
| :--- | :--- |
| `medusa -h <ip-do-alvo> -U smb-users.txt -P smb-pass-spray.txt -M smbnt -t 2 -T 50` | Usa o módulo **smbnt**, atacando o alvo com listas de usuários/senhas. `-t 2` (threads por host) e `-T 50` (threads globais) são usados para um *spray* rápido e menos agressivo por conta. |

### Objetivo e Ação do Ataque

O objetivo neste caso é automatizar a descoberta de **credenciais de *login* válidas** (usuário/senha) no serviço SMB, seguindo a sequência lógica:

1.  **Reconhecimento:** O `enum4linux` coleta nomes de usuários válidos.
2.  **Ataque:** O Medusa executa um **Password Spraying**, tentando cada senha comum em `smb-pass-spray.txt` contra *todos* os usuários em `smb-users.txt`.
3.  **Resultado:** Se uma combinação for bem-sucedida, o Medusa exibirá as credenciais encontradas, comprovando a vulnerabilidade.

---

## Principais Recomendações de Mitigação

As credenciais foram descobertas devido à enumeração de usuários e à falta de políticas de senhas fortes. As seguintes medidas são essenciais para mitigar o risco de ataques SMB em qualquer ambiente de produção:

### Mitigação para SMB (Serviço de Arquivos)
* **Desativar enumeração:** Desativar a capacidade do servidor de enumerar nomes de contas/usuários e compartilhamentos para usuários não autenticados (Ex: configurar `restrict anonymous` no Samba).
* **Política de Senhas:** Impor políticas de senhas complexas e que **impeçam o reuso de senhas comuns** (*password spraying*).
* **Bloqueio de Tentativas:** Implementar **Fail2Ban** ou ferramentas nativas do sistema operacional para bloquear IPs que falharem em autenticações no SMB (portas 445/139) após **3-5 tentativas**.
* **Controle de Acesso:** Aplicar o **Princípio do Menor Privilégio** estritamente aos compartilhamentos.
* **Monitoramento:** Monitorar ativamente falhas de *login* no SIEM para identificar picos incomuns de tráfego na porta 445/139.

## Aviso Legal

**ESTE MATERIAL É APENAS PARA FINS EDUCACIONAIS E DE ESTUDO ÉTICO.** O teste de segurança e a Força Bruta só devem ser realizados em sistemas para os quais você possui **permissão explícita por escrito**. O uso deste código em ambientes não autorizados é ilegal e antiético.
