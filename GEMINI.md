## 🧠 GEMINI.md — Contexto do Projeto | GovernAI

### Identidade

**Nome:** GovernAI  
**Tipo:** Framework de governança para desenvolvimento assistido por agentes de IA  
**Objetivo:** Organizar, executar e auditar tarefas de desenvolvimento de forma estruturada e automatizada  

---

### 🎯 Problema que resolve

O uso de IA no desenvolvimento de software é frequentemente desorganizado, sem rastreabilidade e sem controle de qualidade.

Problemas comuns:
- Tasks sem padrão
- Execução sem validação
- Falta de histórico
- Uso excessivo de LLM
- Falta de governança

---

### 🚀 Solução proposta

O GovernAI implementa um sistema baseado em agentes que:

- Organiza tasks em fluxo estruturado
- Garante validação em todas as etapas
- Reduz uso desnecessário de IA
- Mantém histórico completo e auditável
- Integra com boards (GitHub Projects)

---

### 🧩 Arquitetura do sistema

GovernAI opera com três pilares:

#### 1. Governança (Regras)
- Definida no `.antigravityrules`
- Controla comportamento do agente
- Impede execução inválida
- **Camada de Decisão:** Classifica e roteia solicitações de forma autônoma (veja [decision_layer.md](file:///home/mark/Dev/governai/docs/decision_layer.md))

#### 2. Execução (Tasks)
- Definida no `TASKS.md`
- Representa backlog e progresso

#### 3. Contexto (Projeto)
- Definido neste arquivo (`GEMINI.md`)
- Contém identidade, regras e domínio

---

### 🔁 Fluxo padrão de execução

Toda task segue obrigatoriamente:

1. Criação da task
2. Aprovação da task
3. Geração do plano
4. Aprovação do plano
5. Execução
6. Revisão
7. Conclusão (Done)

---

### ✅ Regras fundamentais

- Nenhuma execução sem task aprovada
- Nenhuma task avança sem validação
- A descrição da task é a fonte de verdade
- Falhas devem ser registradas e bloqueiam progresso
- LLM deve ser usado apenas quando necessário

---

### 🧠 Estratégia de uso de IA

O sistema utiliza abordagem híbrida:

#### 🔹 Determinístico (prioritário)
- chamadas HTTP
- manipulação de dados
- lógica simples

#### 🔹 Inteligente (fallback)
- interpretação de texto
- análise complexa
- geração de conteúdo

---

### 📊 Integração com Board

O sistema utiliza GitHub Projects como fonte visual:

- Backlog → tasks criadas
- In Progress → execução iniciada
- In Review → aguardando aprovação
- Done → concluído
- Blocked → impedimento registrado

---

### 🔒 Regras críticas

- Nunca executar fora do fluxo
- Nunca ignorar validações
- Nunca omitir registro na descrição da task
- Nunca consumir LLM desnecessariamente

---

### 🚀 Futuro do GovernAI

- CLI para criação de projetos
- Dashboard visual
- Multi-agent system
- Marketplace de workflows

---

### 📌 Missão

Transformar o desenvolvimento com IA em algo:

- Estruturado
- Confiável
- Escalável
- Auditável
