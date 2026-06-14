# Template Padrão de Task — GovernAI

Este é o modelo padrão de criação de tarefas (tasks) recomendado pelo **GovernAI**. Ele foi projetado em linguagem simples, servindo tanto para programadores experientes quanto para pessoas leigas ou não técnicas. Ele garante que qualquer pessoa entenda o que está sendo planejado, o impacto esperado no projeto e os passos de validação.

---

## 📋 Modelo Vazio (Copiável)

```markdown
### TASK-[ID] — [Título da Task]

**Status:** [ ]

**Objetivo:**
[Uma frase simples explicando a meta final desta tarefa no mundo real]

**Descrição:**
[Explicação detalhada do problema que estamos resolvendo e de qual alteração faremos]

**Critérios de Aceite:**
- [ ] [Critério 1: Condição clara de sucesso, ex: A tela deve abrir no celular]
- [ ] [Critério 2: ex: Os dados digitados devem ser salvos sem erros]
- [ ] [Critério 3: ex: Nenhuma senha ou credencial deve ser exposta]

**Passos de Execução (Checklist):**
- [ ] Iniciar a tarefa localmente (status `[/]` no TASKS.md)
- [ ] Criar o plano técnico de trabalho no painel de controle
- [ ] Executar as modificações de código necessárias
- [ ] Realizar testes de facilidade de leitura e segurança local
- [ ] Concluir a tarefa no arquivo local (status `[x]` no TASKS.md)
- [ ] Sincronizar as atualizações finais com o painel remoto
- [ ] Atualizar o relatório de walkthrough.md
- [ ] Salvar as modificações finais no servidor remoto (commit e push)

**Resultado Esperado:**
[O que deve mudar na prática no final da execução, ex: O usuário agora pode salvar cadastros com facilidade e segurança]
```

---

## 💡 Exemplo Preenchido (Caso de Uso Real)

Abaixo, veja um exemplo real de tarefa preenchida para o site do Pet Shop de Mariana:

```markdown
### TASK-PET-003 — Criar tela de escolha de horários de banho

**Status:** [ ]

**Objetivo:**
Permitir que o cliente escolha o melhor dia e hora para o banho do seu pet diretamente no site.

**Descrição:**
Criaremos um calendário interativo simples na página de agendamentos. O cliente selecionará uma data disponível e o sistema listará apenas os horários livres (ex: 09:00, 10:30, 14:00), evitando agendamentos duplicados.

**Critérios de Aceite:**
- [ ] O calendário deve exibir apenas datas futuras (dias que ainda não passaram).
- [ ] O sistema não deve permitir que duas pessoas escolham o mesmo horário no mesmo dia.
- [ ] A tela deve ser amigável e legível em celulares e computadores.
- [ ] O resumo da escolha deve ser exibido na tela antes da confirmação final do cliente.

**Passos de Execução (Checklist):**
- [ ] Iniciar a tarefa localmente (mudar status para `[/]` em TASKS.md)
- [ ] Escrever o plano técnico na pasta de trabalho e aguardar aceitação do usuário
- [ ] Programar a interface do calendário interativo no site
- [ ] Programar a lógica que impede horários repetidos no banco de dados
- [ ] Validar a visualização da tela no navegador do celular (responsividade)
- [ ] Marcar tarefa como concluída (`[x]`) em TASKS.md
- [ ] Sincronizar o andamento com o GitHub Projects
- [ ] Registrar histórico de entrega em walkthrough.md
- [ ] Finalizar o commit e enviar o código para o servidor remoto

**Resultado Esperado:**
Mariana não precisará mais controlar horários de banho manualmente no papel. Os clientes acessarão o site, escolherão os horários livres e a planilha de agendamentos será preenchida automaticamente e sem erros.
```
