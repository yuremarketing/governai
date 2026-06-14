# Exemplo Prático de Uso do GovernAI

Esta é uma história simples baseada em um cenário real. Ela demonstra como o GovernAI protege e organiza um projeto, permitindo que uma pessoa sem conhecimento técnico crie seu próprio sistema com o auxílio de um assistente de inteligência artificial (IA) de forma totalmente segura e tranquila.

---

## Personagens e Cenário

*   **O Usuário:** Tiago, dono de um pequeno pet shop chamado "Pet Feliz". Ele não entende de programação de computadores, mas quer criar um sistema para gerenciar os banhos e tosas de seus cães.
*   **O Assistente de IA:** Um assistente virtual (como ChatGPT, Claude ou Claude no VS Code) utilizado para escrever o código do sistema.
*   **O GovernAI:** O framework de governança ativado na pasta do projeto para garantir que a IA não faça alterações inseguras, perca o controle ou quebre o que já está funcionando.

---

## O Fluxo Passo a Passo

### Passo 1: Tiago pede o sistema para a IA
Tiago abre o chat com o assistente de IA e digita sua necessidade em linguagem humana:
> **Tiago:** "Olá! Eu tenho um pet shop e quero criar um sistema simples. Preciso de uma tela onde eu digite o nome do pet, o nome do dono e o horário do banho, e salve isso em algum lugar para eu não esquecer."

---

### Passo 2: O GovernAI entra no projeto
A IA recebe o pedido e, antes de começar a criar os arquivos desordenadamente na pasta do projeto, o **GovernAI** é ativado. O framework cria um arquivo de regras de governança (`governai.config.json`) na pasta raiz e impede que a IA execute qualquer alteração sem antes passar por uma auditoria de segurança.

---

### Passo 3: O GovernAI faz uma auditoria inicial
A IA tenta rodar um script para criar a estrutura do site. O GovernAI intercepta e faz uma varredura completa da pasta do projeto para ver se o ambiente está seguro para trabalhar.
O GovernAI imprime a seguinte mensagem no console do terminal de Tiago:

```text
--------------------------------------------------
GovernAI — Auditoria de Segurança Inicial
--------------------------------------------------
Examinando pasta do projeto...

[ALERTA] Histórico de versões (Git) não inicializado.
[ALERTA] Arquivo de controle de tarefas (TASKS.md) não encontrado.
[ALERTA] Pasta de configuração de senhas (.env) não isolada no .gitignore.

Status da Auditoria: Bloqueado (Ações necessárias antes de programar).
--------------------------------------------------
```

---

### Passo 4: O GovernAI identifica o que falta
O GovernAI impede a IA de prosseguir com a escrita do código do Pet Shop até que as falhas de organização e segurança sejam resolvidas.
A IA percebe o bloqueio do GovernAI e avisa Tiago no chat:
> **Assistente de IA:** "Tiago, o GovernAI bloqueou a escrita de código por questões de segurança. Ele identificou que a pasta do seu projeto ainda não tem controle de versões (Git) e não possui um arquivo para organizarmos nossas tarefas. Vou criar esses arquivos de segurança primeiro."

---

### Passo 5: O GovernAI passa a controlar o fluxo
A IA cria os arquivos de segurança inicial:
1. Inicializa o Git (controle de versão para podermos voltar no tempo se algo der errado).
2. Cria o arquivo `.gitignore` (para garantir que nenhuma senha confidencial do pet shop seja enviada para a internet).
3. Cria o arquivo `TASKS.md` (o painel onde listamos as tarefas que faremos, como "Criar tela de cadastro de pets").

O GovernAI analisa os novos arquivos de segurança e valida que a pasta está pronta para o desenvolvimento. Ele libera o status para a IA começar a trabalhar.

---

### Passo 6: Como a IA trabalha COM o GovernAI (O Dia a Dia Seguro)
Agora que a pasta está segura, o assistente de IA propõe criar a primeira tarefa no painel de controle.

#### A. A Decisão da Tarefa
O assistente de IA tenta iniciar a tarefa de criação da tela. O GovernAI intercepta e pergunta a Tiago no terminal:

```text
--------------------------------------------------
GovernAI — Decisão de Execução de Tarefa
--------------------------------------------------
Código da Tarefa: TASK-001
Título: Criar tela de cadastro de pets e clientes

O que você deseja fazer?
Esta tarefa foi detectada pelo sistema. Escolha como prosseguir:

Opções disponíveis:
1) Começar a trabalhar nela agora (marcar como ativa e iniciar contagem de tempo de trabalho)
2) Apenas planejar para depois (guardar na lista de tarefas pendentes)

(Aguardando sua escolha no teclado...)
--------------------------------------------------
Escolha uma opção (digite 1 ou 2):
```
Tiago digita `1` no teclado e aperta Enter.

#### B. A Solicitação de Autorização de Trabalho (Aprovação de Plano)
A IA planeja como vai programar a tela do pet shop e cria o plano técnico. O GovernAI intercepta e exibe a solicitação de aprovação amigável na tela do chat de Tiago:

```text
--------------------------------------------------
GovernAI — Solicitação de aprovação
--------------------------------------------------

Tarefa: TASK-001
Título: Criar tela de cadastro de pets e clientes

O que vai acontecer na prática:
→ Criaremos uma tela bonita no navegador com campos para Tiago digitar o nome do animal, o dono e o horário, e salvaremos essas informações de forma organizada em um banco de dados local.

📄 Revise antes de aprovar (na barra de arquivos à direita):
- Plano Técnico de Trabalho (detalhes de programação do código)
- Checklist de Execução (lista detalhada das tarefas que serão feitas)
- Relatório de Resultados (histórico de entregas já feitas)

Para responder, escolha na janela da tela:
- Aceitar (Accept) → Autoriza o assistente a iniciar as alterações
- Rejeitar (Reject) → Pausa o andamento para fazermos ajustes antes

--------------------------------------------------
```
Tiago clica na aba lateral para revisar o "Plano Técnico de Trabalho". Ele vê que está tudo correto e clica em **Accept** no chat.

#### C. Confirmação de Ação no Terminal (O Executor)
Durante a programação, a IA precisa instalar uma biblioteca para rodar o banco de dados. Antes de rodar o comando, o GovernAI exibe a confirmação de ação no chat:

```text
--------------------------------------------------
GovernAI — Confirmação de ação
--------------------------------------------------

Tarefa: TASK-001

A ação a seguir será executada no terminal:
→ Instalar a biblioteca de banco de dados (SQLite)

O que vai acontecer na prática:
→ O sistema fará o download de um módulo leve e seguro para salvarmos os agendamentos na máquina de Tiago.

Deseja autorizar e permitir que o assistente realize essa ação?
--------------------------------------------------
```
Tiago clica em **Accept** para autorizar o comando. O sistema instala o SQLite de forma segura.

#### D. Entrega e Fechamento
A IA termina de programar a tela, testa o cadastro e exibe a mensagem de sucesso. 
O GovernAI encerra o cronômetro da tarefa nas métricas, atualiza o arquivo de tarefas local para concluído (`[x]`) e move automaticamente o card de "In Progress" para "Done" no painel visual do GitHub de Tiago.

---

## ➡️ Resultado: o projeto continua organizado, seguro e sob controle.

Sem o GovernAI, a IA poderia ter criado códigos confusos, perdido arquivos de backup ou instalado bibliotecas erradas sem Tiago saber. Com o GovernAI, Tiago — mesmo sem entender de programação — acompanhou cada passo, revisou os impactos em linguagem simples e manteve o controle total do seu sistema de Pet Shop!
