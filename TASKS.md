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
