import os
import sys
import re
import json
import cli_colors
from governance_loader import load_governance_rules

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(SCRIPT_DIR)

def find_task_title(task_id):
    tasks_file = os.path.join(BASE_DIR, "TASKS.md")
    if not os.path.exists(tasks_file):
        return "Título não encontrado (TASKS.md inexistente)"
        
    try:
        with open(tasks_file, "r", encoding="utf-8") as f:
            content = f.read()
            
        # Match header line like: ### TASK-GOV-001 — Implementar...
        pattern = rf"###\s+{re.escape(task_id)}\s*[-—]\s*(.+)"
        match = re.search(pattern, content)
        if match:
            return match.group(1).strip()
    except Exception:
        pass
        
    return "Título não encontrado"

def find_task_description(task_id):
    tasks_file = os.path.join(BASE_DIR, "TASKS.md")
    if not os.path.exists(tasks_file):
        return "Descrição não encontrada (TASKS.md inexistente)"
        
    try:
        with open(tasks_file, "r", encoding="utf-8") as f:
            content = f.read()
            
        sections = content.split("---")
        header_re = re.compile(rf"###\s+{re.escape(task_id)}")
        
        for section in sections:
            section = section.strip()
            if header_re.search(section):
                desc_match = re.search(r"\*\*Descrição:\*\*(.*?)(?=\*\*Critérios de aceite:\*\*|$)", section, re.DOTALL)
                if desc_match:
                    return desc_match.group(1).strip()
    except Exception:
        pass
        
    return "Descrição não encontrada no TASKS.md"

def print_approval_context(task_id, title=None, summary=None):
    if not title:
        title = find_task_title(task_id)
    if not summary:
        summary = find_task_description(task_id)
        
    print(cli_colors.blue("-" * 50))
    print(cli_colors.bold(cli_colors.blue("GovernAI — Solicitação de aprovação")))
    print(cli_colors.blue("-" * 50))
    print()
    print(f"Tarefa: {cli_colors.bold(cli_colors.cyan(task_id))}")
    print(f"Título: {cli_colors.bold(title)}")
    print()
    print("O que vai acontecer na prática:")
    print(summary)
    print()
    print(f"📄 {cli_colors.bold('Revise antes de aprovar (na barra de arquivos à direita):')}")
    print("- Plano Técnico de Trabalho (detalhes de programação do código)")
    print("- Checklist de Execução (lista detalhada das tarefas que serão feitas)")
    print("- Relatório de Resultados (histórico de entregas já feitas)")
    print()
    print("Após ler e revisar, escolha na tela do chat:")
    print(f"- {cli_colors.green('Aceitar (Accept)')} → Autoriza o assistente a iniciar as alterações")
    print(f"- {cli_colors.yellow('Rejeitar (Reject)')} → Pausa o andamento para fazermos ajustes antes")
    print()
    print(cli_colors.blue("-" * 50))

def update_local_task_status(task_id, status_tag):
    status_char = "/" if status_tag == "in_progress" else ("x" if status_tag == "done" else " ")
    tasks_file = os.path.join(BASE_DIR, "TASKS.md")
    if not os.path.exists(tasks_file):
        return False
        
    try:
        with open(tasks_file, "r", encoding="utf-8") as f:
            content = f.read()
            
        # Regex to locate the task header and its **Status:** [ ] line
        pattern = rf"(###\s+{re.escape(task_id)}\s*[-—]\s*[^\n]+\n+?\*\*Status:\*\*\s*\[)(.*?)(\])"
        match = re.search(pattern, content)
        if not match:
            # Fallback regex without the dash in title match
            pattern = rf"(###\s+{re.escape(task_id)}[^\n]+\n+?\*\*Status:\*\*\s*\[)(.*?)(\])"
            match = re.search(pattern, content)
            
        if match:
            new_content = re.sub(pattern, rf"\g<1>{status_char}\g<3>", content)
            with open(tasks_file, "w", encoding="utf-8") as f:
                f.write(new_content)
            return True
    except Exception as e:
        print(cli_colors.red(f"[ERRO] Falha ao atualizar TASKS.md para a tarefa {task_id}: {e}"))
        
    return False

def print_decision_context(task_id, title):
    print(cli_colors.blue("-" * 50))
    print(cli_colors.bold(cli_colors.blue("GovernAI — Decisão de Execução de Tarefa")))
    print(cli_colors.blue("-" * 50))
    print(f"Código da Tarefa: {cli_colors.bold(task_id)}")
    print(f"Título: {cli_colors.bold(title)}")
    print()
    print("O que você deseja fazer?")
    print("Esta tarefa foi detectada pelo sistema. Escolha como prosseguir:")
    print()
    print("Opções disponíveis:")
    print(f"1) {cli_colors.green('Começar a trabalhar nela agora')} (marcar como ativa e iniciar contagem de tempo)")
    print(f"2) {cli_colors.yellow('Apenas planejar para depois')} (guardar na lista de tarefas pendentes)")
    print()
    print("(Aguardando sua escolha no teclado...)")
    print(cli_colors.blue("-" * 50))

def ensure_task_decision(task_id):
    # Load existing metrics database to check if already registered
    metrics_file = os.path.join(BASE_DIR, "logs", "metrics.json")
    metrics_data = {}
    if os.path.exists(metrics_file):
        try:
            with open(metrics_file, "r", encoding="utf-8") as f:
                metrics_data = json.load(f)
        except Exception:
            pass
            
    # If task is already registered, return its status to prevent repeated prompts
    if task_id in metrics_data:
        return metrics_data[task_id].get("status", "pending")
        
    # Task is new/detected. Load governance rules.
    rules = load_governance_rules()
    
    if not rules.get("always_prompt_on_new_task", True):
        # If prompt is disabled, return default "pending" as fail-safe
        print(f"[DECISION] {task_id} → pending (configuração always_prompt_on_new_task desativada)")
        return "pending"
        
    task_title = find_task_title(task_id)
    
    # ALWAYS print the decision context to stdout before any prompt or logic
    print_decision_context(task_id, task_title)
    
    # Check if terminal is interactive (TTY)
    if not sys.stdin.isatty():
        print(cli_colors.yellow(f"[INFO] Tela não-interativa detectada. Guardando automaticamente a tarefa {task_id} na lista de pendentes para segurança do fluxo."))
        # Explicit decision log in requested format
        print(f"[DECISION] {task_id} → pending (modo não-interativo)")
        update_local_task_status(task_id, "pending")
        return "pending"
        
    # Interactive prompt with validation
    choice = ""
    while choice not in ["1", "2"]:
        try:
            choice = input(cli_colors.bold("Escolha uma opção (digite 1 ou 2): ")).strip()
            if choice not in ["1", "2"]:
                print(cli_colors.red("[OPÇÃO INVÁLIDA] Por favor, digite apenas o número 1 ou o número 2 no seu teclado."))
        except (KeyboardInterrupt, EOFError):
            print()
            print(cli_colors.yellow("[AVISO] Seleção interrompida. Guardando a tarefa de forma segura na lista de tarefas pendentes."))
            # Explicit decision log in requested format
            print(f"[DECISION] {task_id} → pending (entrada interrompida)")
            update_local_task_status(task_id, "pending")
            return "pending"
            
    if choice == "1":
        # Explicit decision log in requested format
        print(f"[DECISION] {task_id} → in_progress (input do usuário)")
        update_local_task_status(task_id, "in_progress")
        print(cli_colors.green(f"[SUCESSO] Tarefa {task_id} ativada! Iniciamos o trabalho e o registro de progresso."))
        return "in_progress"
    else:
        # Explicit decision log in requested format
        print(f"[DECISION] {task_id} → pending (input do usuário)")
        update_local_task_status(task_id, "pending")
        print(cli_colors.yellow(f"[INFO] Tarefa {task_id} salva na lista de pendentes para ser realizada no futuro."))
        return "pending"

def print_action_confirmation(task_id, action, input_val, impact):
    print(cli_colors.blue("-" * 50))
    print(cli_colors.bold(cli_colors.blue("GovernAI — Confirmação de ação")))
    print(cli_colors.blue("-" * 50))
    print()
    print(f"Tarefa: {cli_colors.bold(cli_colors.cyan(task_id))}")
    print()
    print("A ação a seguir será executada no terminal:")
    print(f"→ {action} (enviando o valor '{input_val}')")
    print()
    print("O que vai acontecer na prática:")
    print(f"→ {impact}")
    print()
    print("Deseja autorizar e permitir que o assistente realize essa ação?")
    print(cli_colors.blue("-" * 50))
