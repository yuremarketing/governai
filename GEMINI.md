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

### 💡 Casos de uso reais (Exemplos Práticos)

Veja como o GovernAI funciona na prática:

#### Caso de Uso 1: O Site de Agendamentos do Pet Shop
- **A Usuária:** Mariana, dona de um pequeno pet shop de bairro.
- **O que ela quer criar:** Um site simples para os clientes agendarem banhos e tosas para seus animais de estimação.
- **Como ela usa a IA:** Mariana abre o assistente de IA e digita: *"Crie uma página onde meu cliente escolhe o dia, o horário e o porte do cachorro para agendar o banho."*
- **Onde o GovernAI entra:** Sempre que a IA propõe uma nova alteração para criar ou mudar o site, o GovernAI intercepta a ação e exibe uma orientação amigável: *"Mariana, a IA quer criar a tela de escolha de horários. Para garantir que nada quebre no seu site atual, leia nosso Plano de Trabalho à direita antes de autorizar."*
- **O que muda com o GovernAI:**
  - **Sem GovernAI:** A IA começa a programar de forma descontrolada. Na tentativa de corrigir um erro simples na listagem de horários, ela acaba bagunçando a tela de preços que já estava pronta. O site para de funcionar de repente, deixando Mariana frustrada e sem saber como voltar à versão anterior.
  - **Com GovernAI:** A IA só altera o site com a autorização consciente de Mariana. O GovernAI mantém um diário de bordo (histórico) de cada entrega. Se algo der errado, Mariana sabe exatamente o que causou o problema e consegue reverter a mudança com um clique.
- ➡️ Resultado: o projeto continua organizado, seguro e sob controle.

#### Caso de Uso 2: O Assistente de Vendas no WhatsApp
- **O Usuário:** Carlos, corretor de seguros autônomo.
- **O que ele quer criar:** Um sistema automático que responde mensagens de clientes no WhatsApp, tirando dúvidas sobre planos de saúde.
- **Como ele usa a IA:** Carlos diz para a IA: *"Crie um robô que se conecta ao meu WhatsApp Business e responde aos clientes enviando a tabela de preços em PDF."*
- **Onde o GovernAI entra:** Quando a IA tenta configurar os arquivos de conexão e pede a senha de acesso (token) da API do WhatsApp de Carlos, o GovernAI intercepta e garante que esses dados confidenciais fiquem salvos em uma pasta oculta e segura, impedindo que a IA envie suas senhas para a internet pública.
- **O que muda com o GovernAI:**
  - **Sem GovernAI:** A IA cria o robô e, sem que Carlos perceba, salva as chaves de acesso dele em um arquivo que é enviado para a internet pública. Além disso, por conta de uma falha lógica, o robô entra em um loop infinito, disparando centenas de mensagens repetidas e travando o celular dos clientes.
  - **Com GovernAI:** O GovernAI protege as chaves confidenciais do corretor de forma automática. Antes de iniciar qualquer envio de mensagens, o sistema exige uma confirmação clara e amigável na tela. Carlos vê o que está acontecendo e autoriza o robô a funcionar sabendo que seus dados estão 100% protegidos.
- ➡️ Resultado: o projeto continua organizado, seguro e sob controle.

#### Caso de Uso 3: A Planilha Financeira Inteligente
- **A Usuária:** Juliana, artesã que vende velas aromáticas na internet.
- **O que ela quer criar:** Uma planilha de vendas automática que calcula o lucro mensal e envia um e-mail com o resumo de faturamento todo dia às 18h.
- **Como ela usa a IA:** Juliana pede ao assistente: *"Crie um script que soma minhas vendas diárias e me envia um e-mail automático com o total diário."*
- **Onde o GovernAI entra:** O GovernAI acompanha a criação do script de envio. Antes de o script enviar qualquer e-mail real de teste na internet, o GovernAI exige que Juliana dê autorização explícita e mostra na tela o contexto: *"A ação a seguir enviará um e-mail de teste simulado para juliana@email.com contendo as vendas do dia. Deseja permitir?"*
- **O que muda com o GovernAI:**
  - **Sem GovernAI:** A IA ativa o script de envio imediatamente. Por causa de um erro na lógica de repetição, a IA começa a disparar centenas de e-mails vazios e repetidos para a caixa de entrada de Juliana em poucos minutos, bloqueando o e-mail dela por suspeita de spam.
  - **Com GovernAI:** O envio em lote descontrolado é bloqueado preventivamente. O GovernAI intercepta a tentativa de disparo repetitivo e pede autorização a Juliana. Ela percebe o comportamento estranho no teste inicial simulado e corrige a IA antes que ela envie spams reais.
- ➡️ Resultado: o projeto continua organizado, seguro e sob controle.

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
