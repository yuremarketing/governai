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

**Status:** [ ]
**Descrição:**
Ajustar o script `scripts/metrics.py` para garantir idempotência. Deve evitar a duplicação de eventos `start` e `complete` (por exemplo, ignorar chamadas repetidas de `start` se a tarefa já estiver iniciada, e `complete` se já estiver concluída) e proteger os contadores de inconsistências.

**Critérios de aceite:**
- Comando `start` não deve reinicializar ou zerar dados de uma tarefa que já esteja em andamento (`in_progress`) ou concluída.
- Comando `complete` não deve recalcular a duração ou sobrescrever o timestamp final de uma tarefa que já esteja como `completed`.
- Proteção contra incrementos redundantes e tratamento robusto de leitura/escrita simultânea no JSON.

---

### TASK-013 — Implementar mecanismo anti-loop na sincronização

**Status:** [ ]
**Descrição:**
Implementar um mecanismo anti-loop na sincronização bidirecional entre o `TASKS.md` local e o board do GitHub Projects, utilizando uma flag de origem (metadata/tag) para identificar a origem das atualizações e evitar o reprocessamento infinito de eventos gerados pelo próprio sistema.

**Critérios de aceite:**
- Definição de uma convenção ou marcador de origem nas atualizações (ex: comentário HTML ou tag no corpo do card e no `TASKS.md`).
- Lógica no sincronizador para ignorar e descartar eventos de sincronização se o autor ou origem da mudança for o próprio agente do GovernAI.
- Teste de estresse simulando atualizações concorrentes para garantir que o fluxo de sincronização converge e encerra sem entrar em loop.

---

### TASK-014 — Adicionar status interno alinhado com o fluxo no metrics.json

**Status:** [ ]
**Descrição:**
Adicionar e gerenciar um campo de status interno estruturado no arquivo local `logs/metrics.json` para cada tarefa, suportando os estados `pending`, `in_progress`, `done` e `blocked` em total consistência com o ciclo de vida do GovernAI.

**Critérios de aceite:**
- Configuração do status padrão como `pending` ao inicializar o rastreamento da tarefa sem iniciá-la imediatamente.
- Suporte para comandos de transição de status em `scripts/metrics.py` (Ex: transição para `blocked` e retorno para `in_progress`).
- Sincronização automática das transições do `metrics.json` nas regras descritas em `.antigravityrules`.

---

### TASK-015 — Sincronizar e garantir consistência de estados entre sistemas

**Status:** [ ]
**Descrição:**
Garantir a consistência de estados e conteúdo de todas as tarefas entre o arquivo local `TASKS.md` (definido como fonte única de verdade), o board do GitHub Projects e o arquivo `logs/metrics.json`. Qualquer alteração no `TASKS.md` local deve sincronizar de forma atômica e consistente os estados dos outros dois sistemas.

**Critérios de aceite:**
- Mapeamento centralizado e unificado de estados entre `TASKS.md` (markdown), GitHub Projects (columns) e `metrics.json` (json).
- Execução encadeada e atômica onde a atualização do `TASKS.md` dispara a sincronização do GitHub Projects e a atualização correspondente no `metrics.json` sem desvios.
- Validação automática de integridade que impede estados inconsistentes (Ex: uma tarefa marcada como concluída `[x]` no markdown mas `in_progress` no metrics/board).

---

### TASK-016 — Implementar sistema de alertas no GovernAI

**Status:** [ ]
**Descrição:**
Implementar um sistema de alertas no GovernAI para identificar tasks travadas, excesso de revisões e tempos anormais de execução com base nas métricas coletadas.

**Critérios de aceite:**
- Definição de limiares configuráveis para revisões máximas, duração de execução e tempo de inatividade das tasks.
- Detecção e relatório de tarefas anômalas (com alertas) exibidos no comando `report` de métricas.
- Flag ou status visual de alerta impresso de maneira clara no console para tarefas que excedam os limiares.

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

---

---

## ✅ Concluídas

_(nenhuma ainda)_
