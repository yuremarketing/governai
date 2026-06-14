## 📋 TASKS — GovernAI

**Instrução para o agente:** Execute as tarefas em ordem. Uma por vez. Marque [x] ao concluir e faça commit antes de passar para a próxima.

---

## 🔴 Prioridade Alta

### TASK-001 — Refinar identidade do GovernAI

**Status:** [ ]
**Descrição:**
Detalhar melhor o posicionamento do GovernAI como framework de governança para desenvolvimento com IA, incluindo definição clara de público-alvo e proposta de valor.

**Critérios de aceite:**
- Definição de público-alvo (dev solo, times, startups)
- Proposta de valor clara
- Atualização do README.md

---

### TASK-002 — Definir casos de uso principais

**Status:** [ ]
**Descrição:**
Mapear os principais cenários onde o GovernAI pode ser utilizado.

**Critérios de aceite:**
- Pelo menos 3 casos de uso definidos
- Documentação clara no README ou GEMINI.md

---

### TASK-003 — Criar template padrão de task

**Status:** [ ]
**Descrição:**
Definir um modelo padrão de task para garantir consistência e facilidade de uso.

**Critérios de aceite:**
- Template com seções obrigatórias
- Exemplo de task preenchida

---

### TASK-008 — Definir camada de decisão do GovernAI

**Status:** [x]
**Descrição:**
Especificar e estruturar a camada de decisão do GovernAI com uma matriz de decisão explícita, ordem de prioridade (determinístico → LLM → humano), critérios detalhados de bloqueio e fallback seguro baseado em nível de confiança.

**Critérios de aceite:**
- Matriz de decisão explícita com regras determinísticas mapeadas.
- Definição da ordem de prioridade de classificação (Determinístico → LLM → Humano).
- Detalhar critérios de bloqueio (impedimento).
- Fallback seguro baseado em nível de confiança (limiar de classificação da LLM).
- Documentação completa em docs/decision_layer.md.

---

### TASK-009 — Integrar agente com script de sincronização do board

**Status:** [x]
**Descrição:**
Integrar o agente do GovernAI com o script/lógica de sincronização do board. O agente deve atualizar automaticamente o GitHub Projects durante as transições de status das tasks (criação no Backlog, início em In Progress, revisão em In Review, bloqueio em Blocked e conclusão em Done) sem a necessidade de acionamento manual externo.

**Critérios de aceite:**
- Integração da lógica de sincronização nas instruções/regras do agente do GovernAI (ex: no fluxo padrão ou `.antigravityrules`).
- Atualização em tempo real do status do card no GitHub Projects correspondente à mudança de estado local.
- Tratamento automático de erros de comunicação com a API do GitHub.

---

### TASK-010 — Estender sincronização para atualizar corpo das tasks no board

**Status:** [x]
**Descrição:**
Estender o script de sincronização para atualizar também o corpo (body) dos cards no GitHub Projects, garantindo que o board reflita com precisão o conteúdo atualizado da task, incluindo sua descrição detalhada, critérios de aceite, checklist de execução e relatórios de progresso ou conclusão.

**Critérios de aceite:**
- Sincronização e atualização automática do corpo do card correspondente a qualquer modificação em sua seção do `TASKS.md` local.
- Preservação de toda a formatação markdown no corpo dos cards do GitHub.
- Comparação e validação de diferenças do conteúdo local vs remoto antes de enviar mutações desnecessárias (otimização de chamadas de API).

---

### TASK-012 — Garantir idempotência no metrics.py

**Status:** [x]
**Descrição:**
Ajustar o script `scripts/metrics.py` para garantir idempotência. Deve evitar a duplicação de eventos `start` e `complete` (por exemplo, ignorar chamadas repetidas de `start` se a tarefa já estiver iniciada, e `complete` se já estiver concluída) e proteger os contadores de inconsistências.

**Critérios de aceite:**
- Comando `start` não deve reinicializar ou zerar dados de uma tarefa que já esteja em andamento (`in_progress`) ou concluída.
- Comando `complete` não deve recalcular a duração ou sobrescrever o timestamp final de uma tarefa que já esteja como `completed`.
- Proteção contra incrementos redundantes e tratamento robusto de leitura/escrita simultânea no JSON.

---

### TASK-013 — Implementar mecanismo anti-loop na sincronização

**Status:** [x]
**Descrição:**
Implementar um mecanismo anti-loop na sincronização bidirecional entre o `TASKS.md` local e o board do GitHub Projects, utilizando uma flag de origem (metadata/tag) para identificar a origem das atualizações e evitar o reprocessamento infinito de eventos gerados pelo próprio sistema.

**Critérios de aceite:**
- Definição de uma convenção ou marcador de origem nas atualizações (ex: comentário HTML ou tag no corpo do card e no `TASKS.md`).
- Lógica no sincronizador para ignorar e descartar eventos de sincronização se o autor ou origem da mudança for o próprio agente do GovernAI.
- Teste de estresse simulando atualizações concorrentes para garantir que o fluxo de sincronização converge e encerra sem entrar em loop.

---

### TASK-014 — Adicionar status interno alinhado com o fluxo no metrics.json

**Status:** [x]
**Descrição:**
Adicionar e gerenciar um campo de status interno estruturado no arquivo local `logs/metrics.json` para cada tarefa, suportando os estados `pending`, `in_progress`, `done` e `blocked` em total consistência com o ciclo de vida do GovernAI.

**Critérios de aceite:**
- Configuração do status padrão como `pending` ao inicializar o rastreamento da tarefa sem iniciá-la imediatamente.
- Suporte para comandos de transição de status em `scripts/metrics.py` (Ex: transição para `blocked` e retorno para `in_progress`).
- Sincronização automática das transições do `metrics.json` nas regras descritas em `.antigravityrules`.

---

### TASK-015 — Sincronizar e garantir consistência de estados entre sistemas

**Status:** [x]
**Descrição:**
Garantir a consistência de estados e conteúdo de todas as tarefas entre o arquivo local `TASKS.md` (definido como fonte única de verdade), o board do GitHub Projects e o arquivo `logs/metrics.json`. Qualquer alteração no `TASKS.md` local deve sincronizar de forma atômica e consistente os estados dos outros dois sistemas.

**Critérios de aceite:**
- Mapeamento centralizado e unificado de estados entre `TASKS.md` (markdown), GitHub Projects (columns) e `metrics.json` (json).
- Execução encadeada e atômica onde a atualização do `TASKS.md` dispara a sincronização do GitHub Projects e a atualização correspondente no `metrics.json` sem desvios.
- Validação automática de integridade que impede estados inconsistentes (Ex: uma tarefa marcada como concluída `[x]` no markdown mas `in_progress` no metrics/board).

---

### TASK-016 — Implementar sistema de alertas no GovernAI

**Status:** [x]
**Descrição:**
Implementar um sistema de alertas no GovernAI para identificar tasks travadas, excesso de revisões e tempos anormais de execução com base nas métricas coletadas.

**Critérios de aceite:**
- Definição de limiares configuráveis para revisões máximas, duração de execução e tempo de inatividade das tasks.
- Detecção e relatório de tarefas anômalas (com alertas) exibidos no comando `report` de métricas.
- Flag ou status visual de alerta impresso de maneira clara no console para tarefas que excedam os limiares.

---

### TASK-017 — Implementar integração via GitHub Webhooks

**Status:** [x]
**Descrição:**
Implementar um mecanismo de recepção de eventos via GitHub Webhooks para disparar automaticamente as ações e sincronizações do GovernAI quando houver movimentações ou alterações nos cards do board do GitHub Projects.

**Critérios de aceite:**
- Criação de um endpoint básico capaz de receber e validar payloads de webhooks do GitHub (com Webhook Secret).
- Tratamento de eventos de Project V2 (`project_v2_item` criado, editado, movido).
- Execução automatizada da sincronização e validações locais decorrentes de mudanças remotas no board.

---

### TASK-018 — Implementar envio ativo de alertas do GovernAI

**Status:** [x]
**Descrição:**
Implementar um mecanismo de envio ativo e automatizado de notificações/alertas do GovernAI (por exemplo, via Slack, Discord ou e-mail) quando anomalias críticas forem identificadas pelas métricas (tasks bloqueadas, alta taxa de revisão e tempo excessivo de execução).

**Critérios de aceite:**
- Integração de adaptadores de notificação extensíveis (Ex: Webhooks do Slack/Discord ou SMTP para e-mail).
- Configuração de credenciais de notificação seguras via variáveis de ambiente no `.env` (ex: `SLACK_WEBHOOK_URL`).
- Disparo automático de alertas no momento em que uma anomalia for detectada (ex: transição para `blocked` ou quando uma tarefa exceder os limiares durante a sincronização).

---

### TASK-019 — Aplicar hardening no sistema de notificações

**Status:** [ ]
**Descrição:**
Aplicar hardening e aumentar a robustez do sistema de notificações ativas (notifier), incluindo a configuração explícita de timeout HTTP, tratamento estruturado de exceções em todas as chamadas de rede, padronização estruturada de payloads e logging detalhado de envio de alertas.

**Critérios de aceite:**
- Timeout HTTP explícito configurado em todas as chamadas de rede/urllib (ex: 5 segundos).
- Tratamento de exceções (try/except) em todos os adaptadores (Slack, Discord, SMTP) para evitar que falhas individuais abortem a execução do worker.
- Padronização de payloads utilizando um modelo de dados comum ou função geradora.
- Registro detalhado de envio (sucesso, falha, timeout) em arquivo de log específico (ex: `logs/notifications.log`) ou saída padrão com timestamp.

---

### TASK-GOV-001 — Implementar pipeline de decisão obrigatório no GovernAI

**Status:** [x]
**Descrição:**
Garantir que o GovernAI controle o fluxo de decisão do usuário ao interagir com tasks, exigindo confirmação explícita antes de qualquer execução.

**Critérios de aceite:**
- Sempre que uma task for criada ou detectada, o sistema deve apresentar opções ao usuário:
  1) Executar tarefa
  2) Apenas registrar no backlog/kanban
- O sistema NUNCA deve executar automaticamente sem escolha explícita do usuário.
- A lógica deve funcionar independentemente do agente (Copilot, Gemini, etc.).
- O fluxo deve ser automático e não depender de instruções no prompt.
- O comportamento deve ser padronizado para todo o projeto.

---

### TASK-GOV-002 — Persistir regras de governança automaticamente no projeto

**Status:** [x]
**Descrição:**
Garantir que as regras de comportamento do GovernAI sejam persistidas dentro do projeto e aplicadas automaticamente em qualquer nova interação, sem depender de prompts manuais do usuário.

**Critérios de aceite:**
- Criar um arquivo de governança no projeto (ex: GOVERNANCE.md ou governai.config.json)
- Armazenar regras padrão como:
  - sempre perguntar antes de executar tasks
  - nunca executar automaticamente sem confirmação
  - oferecer opções (executar ou apenas registrar)
- Garantir que essas regras sejam carregadas automaticamente pelos scripts (sync_tasks.py, metrics.py, etc.)
- As regras devem ser aplicadas independentemente do agente (Copilot, Gemini, etc.)
- O sistema deve falhar de forma segura (não executar) caso as regras não possam ser carregadas

---

### TASK-GOV-003 — Transformar GovernAI em CLI executável (governai run)

**Status:** [x]
**Descrição:**
Transformar o GovernAI em uma interface de linha de comando (CLI) padronizada, permitindo executar, gerenciar e controlar o sistema de governança sem depender diretamente de scripts individuais.

**Critérios de aceite:**
- Criar comando principal:
  - `governai run` → executa o sincronizador + decision pipeline
- Criar subcomandos:
  - `governai start TASK-XXX`
  - `governai block TASK-XXX`
  - `governai complete TASK-XXX`
  - `governai sync`
  - `governai report`
- A CLI deve:
  - carregar automaticamente governai.config.json
  - respeitar o decision pipeline (TASK-GOV-001)
  - usar as métricas (metrics.py)
- Exibir mensagens amigáveis no terminal (UX melhorada)
- Funcionar localmente sem dependências externas

Requisitos técnicos:
- Criar arquivo `governai.py` ou `cli.py` na raiz ou em scripts/
- Usar argparse (ou similar) para parsing de comandos
- Encapsular chamadas existentes (sync_tasks, metrics, notifier)
- Garantir compatibilidade com ambientes não interativos
- Opcional: tornar executável (chmod +x governai)

---

### TASK-GOV-004 — Melhorar experiência CLI (cores, ajuda, mensagens)

**Status:** [x]
**Descrição:**
Melhorar a experiência do usuário (UX) na CLI `governai` adicionando cores (usando códigos ANSI para compatibilidade simples), formatação aprimorada nas mensagens de ajuda e status de execução detalhados.

**Critérios de aceite:**
- Adicionar suporte a cores ANSI no console (verde para sucesso, amarelo para avisos, vermelho para erros/bloqueios, azul para informações).
- A ajuda de comando (`--help`) deve ser limpa, formatada com cores e conter explicações concisas de cada subcomando.
- O prompt de decisão obrigatório (TASK-GOV-001) deve ser visualmente destacado utilizando cores.
- Mensagens de erro de governança e falha segura devem ser impressas em vermelho (`[ERRO]`).
- O suporte a cores deve respeitar `sys.stdout.isatty()` ou a variável de ambiente `NO_COLOR` para evitar sujeira nos logs em CI/CD.

---

### TASK-GOV-006 — Ajustar decision pipeline para ambientes não-interativos (executor/agent)

**Status:** [x]
**Descrição:**
Garantir que o GovernAI exiba claramente o contexto de decisão das tarefas e funcione corretamente em ambientes onde a entrada interativa (stdin) não é visível ou é controlada por um executor/agent.

**Critérios de aceite:**
- O sistema deve SEMPRE imprimir no stdout, ANTES de qualquer solicitação de decisão:
  - ID da task (TASK-XXX)
  - título da task
  - descrição do que está sendo decidido
  - opções disponíveis (executar ou backlog)
- O output do contexto deve ser claro e legível com separadores e cabeçalho explícito.
- Em ambientes NÃO interativos (detectar via `sys.stdin.isatty()` ou equivalente), NÃO utilizar input() e retornar automaticamente a opção segura "pending" (backlog).
- Em ambientes interativos, usar input() apenas após exibir claramente o contexto, validar a entrada (aceitar somente 1 ou 2), e repetir em caso de erro.
- Nunca solicitar input invisível ou sem contexto.
- Registrar explicitamente no stdout a decisão tomada no formato:
  `[DECISION] TASK-XXX → <status> (<motivo>)`
  (onde motivo pode ser "input do usuário" ou "ambiente não-interativo").

---





## 🟡 Prioridade Média

### TASK-004 — Criar exemplo prático de uso

**Status:** [ ]
**Descrição:**
Criar um cenário simulado mostrando o uso do GovernAI em um projeto real.

**Critérios de aceite:**
- Fluxo completo demonstrado
- Documentação clara

---

### TASK-005 — Documentar fluxo completo

**Status:** [ ]
**Descrição:**
Explicar detalhadamente todo o ciclo de vida de uma task.

**Critérios de aceite:**
- Documentação clara
- Exemplo passo a passo

---

### TASK-011 — Implementar coleta de métricas do sistema GovernAI

**Status:** [x]
**Descrição:**
Implementar um mecanismo de coleta de métricas para o GovernAI que registre o tempo total de execução de tasks, o número de revisões efetuadas, a quantidade de bloqueios encontrados e o volume/custo de uso de LLM (tokens consumidos).

**Critérios de aceite:**
- Script ou módulo para rastrear tempo decorrido de tasks (início a conclusão).
- Contador de transições de status (revisões e bloqueios).
- Registro de logs ou banco de dados local consolidando o uso de tokens da LLM.
- Relatório de métricas consolidadas acessível via CLI ou arquivo Markdown.

---

---

## 🟢 Prioridade Baixa

### TASK-006 — Planejar CLI do GovernAI

**Status:** [ ]
**Descrição:**
Definir como será uma CLI para criação de projetos com GovernAI.

**Critérios de aceite:**
- Estrutura inicial definida
- Comandos principais descritos

---

### TASK-007 — Planejar dashboard web

**Status:** [ ]
**Descrição:**
Definir arquitetura de uma interface visual para gestão do GovernAI.

**Critérios de aceite:**
- Ideia de telas
- Fluxo de navegação


### TASK-GOV-007 — Implementar fail-safe de governança no Webhook Receiver

**Status:** [ ]
**Descrição:**
Garantir que o script `webhook_receiver.py` falhe de forma segura na inicialização caso as regras de governança em `governai.config.json` não possam ser carregadas.

**Critérios de aceite:**
- Importar e invocar `load_governance_rules()` no `main()` do `webhook_receiver.py` antes de iniciar o servidor HTTP.
- Garantir que erros de configuração abortem a inicialização com exit code 1.

---

### TASK-GOV-009 — Melhorar UX de aprovação (explicar artifacts antes do Accept)

**Status:** [x]
**Descrição:**
Garantir que o usuário entenda claramente o que está aprovando antes de interagir com botões de Accept/Reject, exibindo de forma explícita o contexto da task, impacto esperado e onde revisar os artefatos no console (stdout) e chat do agente.

**Critérios de aceite:**
- Sempre que uma task exigir aprovação, exibir contexto no stdout/chat antes do Accept.
- Nunca solicitar Accept sem esse bloco explicativo.
- Sempre indicar explicitamente a aba/artifact correto.
- Se o resumo (summary) não for fornecido, buscar automaticamente a descrição no TASKS.md (sem exibir conteúdo genérico).
- Manter compatibilidade com CLI, ambiente de agente e stdout (terminal).

---

### TASK-TEST-UX — Testar fluxo de aprovação com contexto

**Status:** [/]
**Descrição:**
Validar se o GovernAI exibe corretamente o bloco de aprovação com contexto antes de solicitar Accept/Reject.

**Critérios de aceite:**
- O bloco de aprovação deve ser exibido com sucesso no chat.
- O bloco de aprovação deve ser exibido com sucesso no terminal (stdout).
- O fallback de descrição deve buscar automaticamente os dados corretos no TASKS.md.

---

### TASK-GOV-011 — Explicar ações antes da aprovação do executor

**Status:** [x]
**Descrição:**
Garantir que o usuário entenda claramente o que está sendo enviado ao terminal antes de clicar em Accept, exibindo o contexto e impacto esperados de qualquer envio de input.

**Critérios de aceite:**
- Nunca exibir "Approve?" sem contexto explicativo detalhado.
- Sempre vincular a ação à task correspondente.
- Explicar detalhadamente o impacto esperado da ação.
- Funcionar perfeitamente no ambiente do agente (chat) e na CLI.

---

### TASK-GOV-012 — Melhorar linguagem das mensagens para usuários leigos

**Status:** [x]
**Descrição:**
Tornar a comunicação do GovernAI mais amigável, clara e compreensível para usuários não técnicos, traduzindo termos técnicos e impactos em linguagem simples e acolhedora.

**Critérios de aceite:**
- Evitar termos técnicos isolados (ex: "input", "in_progress").
- Traduzir impacto em linguagem simples.
- Manter clareza e simplicidade em todas as interações.

---

## ✅ Concluídas

_(nenhuma ainda)_
