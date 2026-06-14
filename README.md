# 🚀 GovernAI

O **GovernAI** é um framework de governança leve e automatizado projetado para organizar, auditar e proteger o fluxo de desenvolvimento de software assistido por agentes de inteligência artificial (como Antigravity, Claude, Copilot e outros).

---

## 👥 Público-Alvo (Para quem é?)

O GovernAI foi criado para estruturar a colaboração entre humanos e IAs, atendendo a:
* **Desenvolvedores Solo:** Que desejam manter um histórico limpo e auditável das entregas da IA, evitando que ela desorganize o código ou cause regressões.
* **Times de Engenharia & Startups:** Que precisam integrar agentes de IA nos seus fluxos de trabalho com controle de qualidade rigoroso, proteção de dados e métricas de eficiência (LLM calls, duração e bloqueios).
* **Usuários Não Técnicos (Leigos):** Pessoas sem conhecimento de programação que usam assistentes de IA para criar sites ou automações e precisam de um "copiloto de segurança" para não quebrar o sistema atual e proteger suas chaves e senhas confidenciais.

---

## 🎯 Proposta de Valor (Qual problema resolve?)

Desenvolver software com IA sem supervisão frequentemente leva ao caos:
* **Desenvolvimento desorganizado:** A IA começa a programar de forma descontrolada e acaba quebrando funcionalidades estáveis tentando corrigir problemas simples.
* **Falta de segurança:** Riscos de vazamento público de chaves de API, senhas ou tokens confidenciais do `.env`.
* **Falta de controle e custos:** Loops infinitos de rede ou consumo excessivo e desnecessário de chamadas de LLM.

### O Diferencial do GovernAI
O GovernAI atua como um **filtro de segurança e governança atômico** entre a IA e o seu projeto:
1. **Decisão Obrigatória:** Toda alteração ou comando proposto pela IA exige a criação de uma tarefa no backlog (`TASKS.md`) e autorização consciente do usuário.
2. **Prevenção contra Regressões:** A IA trabalha em blocos isolados, impedindo alterações não autorizadas fora do escopo da tarefa ativa.
3. **Proteção Ativa de Dados e Loops:** Bloqueio e alertas para rajadas de requisições e isolamento preventivo de arquivos de ambiente (.env).

---

## 🧩 Principais Funcionalidades

* **📋 Gestão Automatizada de Backlog:** Sincronização automática entre o backlog local (`TASKS.md`) e boards do GitHub Projects.
* **🤖 Decisões e Aprovações Transparentes:** Tomada de decisão de tarefas no console (TTY/Ambiente não-interativo) e prompts explicativos antes do `Accept` no chat.
* **⚠️ Sistema de Alertas de Governança:** Detecção ativa de inatividade, excesso de revisões (commits) ou tempo excessivo de execução.
* **🔔 Notificações Ativas:** Adaptadores nativos para notificar anomalias e bloqueios via Slack, Discord ou E-mail (SMTP).
* **📊 Coleta Incremental de Métricas:** Estatísticas de duração de tarefas, custos de chamadas de LLM, revisões e bloqueios consolidadas no `metrics.json` e relatório Markdown.

---

## ⚙️ Como funciona o fluxo padrão

O ciclo de vida de qualquer alteração no projeto segue 7 etapas obrigatórias:
1. **Criação da Task:** A meta e critérios de aceite são registrados no backlog.
2. **Decisão:** O usuário decide iniciar a tarefa ou salvá-la para depois.
3. **Geração do Plano:** O assistente propõe o plano técnico de execução detalhando o que será alterado.
4. **Aprovação do Plano:** O usuário revisa o escopo e autoriza a execução.
5. **Execução:** O assistente realiza as alterações com contagem ativa de tempo de trabalho.
6. **Revisão:** Verificação com testes automatizados e aprovação de ações no terminal.
7. **Conclusão (Done):** O status é atualizado para concluído e sincronizado com o board.

---

## 📂 Recursos e Documentação

Explore nossos guias e templates para entender o GovernAI em detalhes:
* 💡 [Casos de Uso Reais](file:///home/mark/Dev/governai/GEMINI.md#caso-de-uso-1-o-site-de-agendamentos-do-pet-shop): Cenários práticos simulando a experiência no dia a dia.
* 🛠️ [Exemplo Prático](file:///home/mark/Dev/governai/docs/exemplo_pratico.md): História simulada passo a passo de um projeto com o GovernAI.
* 🔁 [Guia de Fluxo Completo](file:///home/mark/Dev/governai/docs/fluxo_completo.md): Detalhamento técnico de ponta a ponta do ciclo de vida das tarefas.
* 📋 [Template de Task](file:///home/mark/Dev/governai/docs/task_template.md): Modelo padrão e limpo para preenchimento de novas tarefas.
