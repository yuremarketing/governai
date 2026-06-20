import os
import re
import sys
import requests
import json

# Resolve absolute paths relative to this script's directory
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(SCRIPT_DIR)
TASKS_FILE = os.path.join(BASE_DIR, "TASKS.md")
ENV_FILE = os.path.join(BASE_DIR, ".env")

sys.path.append(SCRIPT_DIR)
from metrics import start_task, complete_task, load_metrics, metrics_transaction, add_pending_task_raw
import cli_colors
from governance_loader import load_governance_rules
import audit_logger


def _sensitive_mode():
    """Lê modo do scanner de dados sensíveis: 'warn' | 'block' | 'mask' | None (desativado)."""
    try:
        config_file = os.path.join(BASE_DIR, "governai.config.json")
        with open(config_file, "r", encoding="utf-8") as f:
            config = json.load(f)
        cfg = config.get("sensitive_data", {})
        if not cfg.get("enabled", True):
            return None
        return cfg.get("mode", "warn")
    except Exception:
        return "warn"  # fail-safe


def _scan_task_body(task_id, body):
    """
    Verifica o corpo da task por dados sensíveis antes de enviar ao GitHub.

    Retorna (safe_body: str | None):
        - str  → corpo a ser enviado (original ou mascarado)
        - None → modo block: não sincronizar esta task
    """
    mode = _sensitive_mode()
    if mode is None:
        return body  # scanner desativado

    try:
        from sensitive_data import scan, mask
    except Exception:
        return body  # fail-soft

    findings = scan(body)
    if not findings:
        return body  # sem achados

    # Exibe alerta
    types_found = ", ".join(sorted({f['type'] for f in findings}))
    print(cli_colors.yellow(f"\n⚠️  [DADO SENSÍVEL] Task {task_id}: detectado [{types_found}] no conteúdo."))
    for f in findings:
        print(cli_colors.yellow(f"   {f['type']:20s} → {f['masked_preview']}"))

    if mode == "block":
        print(cli_colors.red(f"   Ação: sincronização de '{task_id}' ABORTADA (modo block)."))
        print(cli_colors.red("   Remova o dado sensível da task antes de sincronizar.\n"))
        audit_logger.log_action(
            "system/sync", "system", "sync", task_id, False,
            f"Sync bloqueado: dado sensível detectado no corpo da task [{types_found}]"
        )
        return None  # sinaliza para pular esta task

    # warn ou mask: mascara o corpo silenciosamente
    masked = mask(body)
    print(cli_colors.yellow(f"   Ação: conteúdo mascarado antes do envio ao GitHub.\n"))
    audit_logger.log_action(
        "system/sync", "system", "sync", task_id, True,
        f"Corpo mascarado antes do sync: [{types_found}]"
    )
    return masked

def load_env():
    env = {}
    if os.path.exists(ENV_FILE):
        with open(ENV_FILE, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#"):
                    if "=" in line:
                        key, val = line.split("=", 1)
                        env[key.strip()] = val.strip()
    return env

env = load_env()
GITHUB_TOKEN = env.get("GITHUB_TOKEN") or os.environ.get("GITHUB_TOKEN")
PROJECT_NUMBER = env.get("PROJECT_NUMBER") or os.environ.get("PROJECT_NUMBER")
GITHUB_USER = env.get("GITHUB_USER") or os.environ.get("GITHUB_USER")

if not GITHUB_TOKEN or not PROJECT_NUMBER or not GITHUB_USER:
    print(cli_colors.red("[ERRO] Variáveis GITHUB_TOKEN, PROJECT_NUMBER ou GITHUB_USER não encontradas no .env ou no ambiente."), file=sys.stderr)
    sys.exit(1)

PROJECT_NUMBER = int(PROJECT_NUMBER)


def normalize_text(text):
    if not text:
        return ""
    text = text.replace("\r\n", "\n")
    # Split by lines, strip each line
    lines = [line.strip() for line in text.split("\n")]
    # Filter out empty lines from comparison to make it robust against spacing changes
    lines = [line for line in lines if line]
    return "\n".join(lines).strip()

def normalize_status_tag(status_name):
    if not status_name:
        return "todo"
    status_clean = status_name.strip().lower()
    status_clean = status_clean.replace(" ", "_")
    if status_clean in ["todo", "a_fazer", "backlog"]:
        return "todo"
    if status_clean in ["in_progress", "em_progresso", "doing"]:
        return "in_progress"
    if status_clean in ["done", "concluido", "concluída"]:
        return "done"
    if status_clean in ["blocked", "bloqueado", "impedimento"]:
        return "blocked"
    return status_clean

def parse_sync_tag(body_text):
    if not body_text:
        return None
    match = re.search(r"<!--\s*governai-sync:\s*([\w_]+)\s*-->", body_text)
    if match:
        return normalize_status_tag(match.group(1))
    return None

def should_sync_reverse(task_id, github_status, github_body):
    normalized_github_status = normalize_status_tag(github_status)
    tag_status = parse_sync_tag(github_body)
    
    if tag_status is None:
        return True
        
    if normalized_github_status == tag_status:
        return False
        
    return True

def parse_tasks():
    if not os.path.exists(TASKS_FILE):
        print(f"[ERRO] Arquivo {TASKS_FILE} não encontrado.")
        return []
    
    with open(TASKS_FILE, "r", encoding="utf-8") as f:
        content = f.read()
    
    sections = content.split("---")
    tasks = []
    
    header_re = re.compile(r"###\s+(TASK-[A-Z0-9_-]+)\s*[-—]\s*(.+)")
    category_re = re.compile(r"##\s+([^\n]+)")
    
    current_category = "Sem Categoria"
    
    for section in sections:
        section = section.strip()
        
        # Verifica se esta seção define uma nova categoria
        category_match = category_re.search(section)
        if category_match:
            cat_candidate = category_match.group(1).strip()
            # Ignora cabeçalhos que não sejam categorias reais
            if not cat_candidate.startswith("###") and not cat_candidate.startswith("📋") and not cat_candidate.startswith("✅"):
                current_category = cat_candidate
        
        header_match = header_re.search(section)
        if not header_match:
            continue
        
        task_id = header_match.group(1)
        title = header_match.group(2).strip()
        full_title = f"{task_id} — {title}"
        
        status_match = re.search(r"\*\*Status:\*\*\s*\[(.*?)\]", section)
        status_val = status_match.group(1).strip() if status_match else ""
        
        is_done = False
        is_in_progress = False
        
        # Tarefas canceladas ou superadas devem ir diretamente para 'done'
        is_canceled = "CANCELADA" in section or "CANCELADA" in status_val or "SUPERADA" in status_val
        
        if status_val.lower() == 'x' or is_canceled:
            is_done = True
        elif status_val == '/':
            is_in_progress = True
            
        desc_match = re.search(r"\*\*Descrição:\*\*(.*?)(?=\*\*Critérios de aceite:\*\*|$)", section, re.DOTALL)
        description = desc_match.group(1).strip() if desc_match else ""
        
        criteria_match = re.search(r"\*\*Critérios de aceite:\*\*(.*)$", section, re.DOTALL)
        criteria = criteria_match.group(1).strip() if criteria_match else ""
        
        status_tag = "done" if is_done else ("in_progress" if is_in_progress else "todo")
        body = f"### Descrição\n{description}\n\n### Critérios de aceite\n{criteria}\n\n<!-- governai-sync: {status_tag} -->"
        
        tasks.append({
            "id": task_id,
            "title": full_title,
            "body": body,
            "is_done": is_done,
            "is_in_progress": is_in_progress,
            "category": current_category
        })
        
    return tasks

def query_github(query, variables=None):
    url = "https://api.github.com/graphql"
    headers = {"Authorization": f"Bearer {GITHUB_TOKEN}"}
    try:
        r = requests.post(url, json={"query": query, "variables": variables}, headers=headers)
        if r.status_code != 200:
            handle_connection_error(f"HTTP {r.status_code}: {r.text}")
        res = r.json()
        if "errors" in res:
            handle_connection_error(f"GraphQL returned errors: {res['errors']}")
        return res["data"]
    except requests.exceptions.RequestException as e:
        handle_connection_error(f"RequestException: {e}")

def create_category_field(project_id):
    query = """
    mutation($projectId: ID!, $name: String!, $options: [ProjectV2SingleSelectFieldOptionInput!]!) {
      createProjectV2Field(input: {
        projectId: $projectId,
        name: $name,
        dataType: SINGLE_SELECT,
        singleSelectOptions: $options
      }) {
        projectV2Field {
          ... on ProjectV2SingleSelectField {
            id
            options {
              id
              name
            }
          }
        }
      }
    }
    """
    options_input = [
        {"name": "🛡️ Segurança & Privacidade", "color": "RED", "description": ""},
        {"name": "🤖 Governança & CLI Core", "color": "BLUE", "description": ""},
        {"name": "📊 Métricas, Monitoramento & Alertas", "color": "ORANGE", "description": ""},
        {"name": "🔄 Integração com Board", "color": "GREEN", "description": ""},
        {"name": "🎨 Experiência do Usuário (UX) & Documentação", "color": "PINK", "description": ""}
    ]
    
    res = query_github(query, {
        "projectId": project_id,
        "name": "Categoria",
        "options": options_input
    })
    
    field = res["createProjectV2Field"]["projectV2Field"]
    field_id = field["id"]
    options = {}
    for opt in field["options"]:
        options[opt["name"]] = opt["id"]
        
    return field_id, options

def get_project_metadata():
    query = """
    query($login: String!, $number: Int!) {
      user(login: $login) {
        projectV2(number: $number) {
          id
          title
          fields(first: 50) {
            nodes {
              ... on ProjectV2SingleSelectField {
                id
                name
                options {
                  id
                  name
                }
              }
            }
          }
        }
      }
    }
    """
    data = query_github(query, {"login": GITHUB_USER, "number": PROJECT_NUMBER})
    project = data["user"]["projectV2"]
    if not project:
        raise Exception(f"Projeto #{PROJECT_NUMBER} não encontrado para o usuário {GITHUB_USER}.")
    
    project_id = project["id"]
    status_field_id = None
    status_options = {}
    
    category_field_id = None
    category_options = {}
    
    for field in project["fields"]["nodes"]:
        name = field.get("name")
        if name == "Status":
            status_field_id = field["id"]
            for option in field["options"]:
                status_options[option["name"].lower()] = option["id"]
        elif name == "Categoria":
            category_field_id = field["id"]
            for option in field["options"]:
                category_options[option["name"]] = option["id"]
                
    if not status_field_id:
        raise Exception("Campo 'Status' não encontrado no projeto.")
        
    # Se o campo Categoria não existe, tenta criá-lo automaticamente
    if not category_field_id:
        print(cli_colors.blue("Campo 'Categoria' não encontrado no projeto. Tentando criar automaticamente..."))
        try:
            category_field_id, category_options = create_category_field(project_id)
            print(cli_colors.green("Campo 'Categoria' criado com sucesso no GitHub Projects!"))
        except Exception as e:
            print(cli_colors.yellow(f"\n⚠️  Aviso: Não foi possível criar o campo 'Categoria' automaticamente: {e}"))
            print(cli_colors.yellow("Para ver as tarefas agrupadas por categoria no GitHub, crie um campo 'Single Select' chamado 'Categoria' manualmente no seu Projects com as opções:"))
            print(cli_colors.yellow(" - 🛡️ Segurança & Privacidade"))
            print(cli_colors.yellow(" - 🤖 Governança & CLI Core"))
            print(cli_colors.yellow(" - 📊 Métricas, Monitoramento & Alertas"))
            print(cli_colors.yellow(" - 🔄 Integração com Board"))
            print(cli_colors.yellow(" - 🎨 Experiência do Usuário (UX) & Documentação\n"))
            
    return project_id, status_field_id, status_options, category_field_id, category_options

def get_current_items(project_id):
    query = """
    query($projectId: ID!) {
      node(id: $projectId) {
        ... on ProjectV2 {
          items(first: 100) {
            nodes {
              id
              content {
                ... on DraftIssue {
                  id
                  title
                  body
                }
                ... on Issue {
                  id
                  title
                  body
                }
              }
              fieldValues(first: 20) {
                nodes {
                  ... on ProjectV2ItemFieldSingleSelectValue {
                    name
                    field {
                      ... on ProjectV2FieldCommon {
                        name
                      }
                    }
                  }
                }
              }
            }
          }
        }
      }
    }
    """
    data = query_github(query, {"projectId": project_id})
    items = data["node"]["items"]["nodes"]
    existing = {}
    
    task_id_re = re.compile(r"^(TASK-[A-Z0-9_-]+)")
    
    for item in items:
        title = ""
        draft_issue_id = None
        body_content = ""
        
        content = item.get("content")
        if content:
            title = content.get("title", "")
            draft_issue_id = content.get("id")
            body_content = content.get("body", "")
        
        status_name = ""
        category_name = ""
        for val in item.get("fieldValues", {}).get("nodes", []):
            field_name = val.get("field", {}).get("name")
            if field_name == "Status":
                status_name = val.get("name", "")
            elif field_name == "Categoria":
                category_name = val.get("name", "")
                
        if title:
            # Tenta extrair o Task ID
            id_match = task_id_re.match(title)
            key = id_match.group(1) if id_match else title
            
            existing[key] = {
                "id": item["id"],
                "draft_issue_id": draft_issue_id,
                "title": title,
                "status": status_name.lower(),
                "category": category_name,
                "body": body_content
            }
    return existing

def add_draft_issue(project_id, title, body):
    query = """
    mutation($projectId: ID!, $title: String!, $body: String!) {
      addProjectV2DraftIssue(input: {projectId: $projectId, title: $title, body: $body}) {
        projectItem {
          id
          content {
            ... on DraftIssue {
              id
            }
          }
        }
      }
    }
    """
    data = query_github(query, {"projectId": project_id, "title": title, "body": body})
    item = data["addProjectV2DraftIssue"]["projectItem"]
    item_id = item["id"]
    draft_issue_id = item.get("content", {}).get("id") if item.get("content") else None
    return item_id, draft_issue_id

def update_draft_issue(draft_issue_id, title, body):
    query = """
    mutation($draftIssueId: ID!, $title: String!, $body: String!) {
      updateProjectV2DraftIssue(input: {
        draftIssueId: $draftIssueId
        title: $title
        body: $body
      }) {
        draftIssue {
          id
        }
      }
    }
    """
    query_github(query, {
        "draftIssueId": draft_issue_id,
        "title": title,
        "body": body
    })

def update_item_status(project_id, item_id, field_id, option_id):
    query = """
    mutation($projectId: ID!, $itemId: ID!, $fieldId: ID!, $optionId: String!) {
      updateProjectV2ItemFieldValue(input: {
        projectId: $projectId
        itemId: $itemId
        fieldId: $fieldId
        value: {singleSelectOptionId: $optionId}
      }) {
        projectV2Item {
          id
        }
      }
    }
    """
    query_github(query, {
        "projectId": project_id,
        "itemId": item_id,
        "fieldId": field_id,
        "optionId": option_id
    })

def handle_connection_error(e):
    from metrics import set_global_alert
    import cli_colors
    print(cli_colors.red(f"\n[ERRO DE CONEXÃO] Falha ao comunicar com a API do GitHub."))
    print(cli_colors.yellow("Verifique suas credenciais no arquivo .env:"))
    print(cli_colors.yellow("  - O GITHUB_TOKEN é válido e não expirou?"))
    print(cli_colors.yellow("  - O PROJECT_NUMBER está correto?"))
    print(cli_colors.yellow("  - O GITHUB_USER corresponde ao dono do projeto?"))
    print(cli_colors.red(f"Detalhes técnicos: {e}\n"))
    set_global_alert("conexao_github", "Falha de comunicação com GitHub API. Verifique suas credenciais no .env.")
    sys.exit(1)

def main():
    # Load governance rules first (fail-safe check)
    load_governance_rules()
    
    print(cli_colors.cyan("Sincronizando tarefas com o GitHub Projects (com atualização de corpo)..."))
    tasks = parse_tasks()
    print(cli_colors.blue(f"Lidas {len(tasks)} tarefas de TASKS.md."))
    
    print(cli_colors.blue("Buscando metadados do projeto..."))
    project_id, status_field_id, status_options, category_field_id, category_options = get_project_metadata()
    print(cli_colors.blue(f"Opções de Status detectadas: {list(status_options.keys())}"))
    
    print(cli_colors.blue("Buscando itens atuais do board..."))
    existing_items = get_current_items(project_id)
    
    for t in tasks:
        title = t["title"]
        body = t["body"]
        is_done = t["is_done"]
        is_in_progress = t["is_in_progress"]
        task_id = t["id"]
        task_category = t.get("category", "Sem Categoria")
        
        try:
            m_data = load_metrics()
            current_metrics_status = m_data.get(task_id, {}).get("status", "pending") if task_id in m_data else None
        except Exception:
            current_metrics_status = None
            
        if current_metrics_status is None:
            # INTERCEPT new/detected tasks for decision
            import decision_pipeline
            decision = decision_pipeline.ensure_task_decision(task_id)
            if decision == "in_progress":
                is_in_progress = True
                is_done = False
                t["is_in_progress"] = True
                t["is_done"] = False
                target_metrics_status = "in_progress"
            else:
                is_in_progress = False
                is_done = False
                t["is_in_progress"] = False
                t["is_done"] = False
                target_metrics_status = "pending"
                
            status_tag = "in_progress" if is_in_progress else "todo"
            # Replace sync tag in body
            body = re.sub(r"<!--\s*governai-sync:\s*([\w_]+)\s*-->", f"<!-- governai-sync: {status_tag} -->", body)
            t["body"] = body
            
            print(cli_colors.green(f"Inicializando '{task_id}' como {target_metrics_status} no metrics.json..."))
            with metrics_transaction() as m:
                add_pending_task_raw(m, task_id)
                m[task_id]["status"] = target_metrics_status
                if target_metrics_status == "in_progress":
                    from datetime import datetime, timezone
                    m[task_id]["start_time"] = datetime.now(timezone.utc).isoformat()
                    m[task_id]["llm_calls"] = 1
            current_metrics_status = target_metrics_status
        else:
            target_metrics_status = "done" if is_done else ("in_progress" if is_in_progress else "pending")
            
        if current_metrics_status != target_metrics_status:
            # Exceção de Bloqueio (Regra da TASK-015):
            # Se target_metrics_status for 'pending' mas no metrics for 'blocked', preservamos o 'blocked' e avisamos.
            if target_metrics_status == "pending" and current_metrics_status == "blocked":
                print(cli_colors.yellow(f"\n[AVISO DE DIVERGÊNCIA] A tarefa {task_id} está marcada como 'blocked' no metrics.json, "
                      f"mas o TASKS.md indica backlog '[ ]' (pending). Preservando o estado 'blocked' para investigação manual.\n"))
            else:
                print(cli_colors.blue(f"Consistência: Sincronizando status de '{task_id}' no metrics.json: {current_metrics_status} -> {target_metrics_status}"))
                if target_metrics_status == "in_progress":
                    start_task(task_id)
                elif target_metrics_status == "done":
                    complete_task(task_id)
                elif target_metrics_status == "pending":
                    # Força volta para pending resetando tempos
                    with metrics_transaction() as m:
                        add_pending_task_raw(m, task_id)
                        m[task_id]["status"] = "pending"
                        m[task_id]["start_time"] = None
                        m[task_id]["end_time"] = None
                        m[task_id]["duration_seconds"] = None
        
        # Determine target status name
        if is_done:
            target_status_name = "done"
        elif is_in_progress:
            target_status_name = "in progress"
        else:
            target_status_name = "todo"
            
        # Get target option ID
        option_id = status_options.get(target_status_name)
        if not option_id:
            option_id = status_options.get("todo") or list(status_options.values())[0]

        # Verifica dados sensíveis no corpo antes de qualquer chamada à API do GitHub
        safe_body = _scan_task_body(task_id, body)
        if safe_body is None:
            # Modo block: pula somente esta task, continua o sync das demais
            continue
        body = safe_body
            
        # Busca no board baseada no task_id para evitar duplicação por mudança de título
        if task_id in existing_items:
            item_info = existing_items[task_id]
            item_id = item_info["id"]
            draft_issue_id = item_info["draft_issue_id"]
            current_status = item_info["status"]
            current_body = item_info["body"]
            current_title = item_info.get("title", "")
            current_category_val = item_info.get("category", "")
            
            # Check if the body or title needs update
            if draft_issue_id and (normalize_text(current_body) != normalize_text(body) or current_title != title):
                print(cli_colors.blue(f"Atualizando corpo/título de '{title}'..."))
                update_draft_issue(draft_issue_id, title, body)
            
            if current_status != target_status_name:
                print(cli_colors.cyan(f"Atualizando status de '{title}': {current_status} -> {target_status_name}"))
                update_item_status(project_id, item_id, status_field_id, option_id)
                
            # Sincroniza o valor da Categoria no item
            if category_field_id and task_category in category_options:
                target_cat_option_id = category_options[task_category]
                if current_category_val != task_category:
                    print(cli_colors.cyan(f"Atualizando categoria de '{title}': '{current_category_val}' -> '{task_category}'"))
                    update_item_status(project_id, item_id, category_field_id, target_cat_option_id)
        else:
            print(cli_colors.green(f"Criando nova task '{title}' no status {target_status_name}..."))
            item_id, draft_issue_id = add_draft_issue(project_id, title, body)
            update_item_status(project_id, item_id, status_field_id, option_id)
            
            # Sincroniza categoria na criação
            if category_field_id and task_category in category_options:
                target_cat_option_id = category_options[task_category]
                print(cli_colors.cyan(f"Definindo categoria de '{title}' para '{task_category}'"))
                update_item_status(project_id, item_id, category_field_id, target_cat_option_id)
            
    print(cli_colors.green("Sincronização concluída com sucesso!"))
    
    try:
        from metrics import clear_global_alert
        clear_global_alert("conexao_github")
    except Exception:
        pass

if __name__ == "__main__":
    main()
