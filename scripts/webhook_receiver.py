import os
import sys
import json
import hmac
import hashlib
import re
import queue
import threading
import subprocess
from http.server import HTTPServer, BaseHTTPRequestHandler
from datetime import datetime, timezone

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(SCRIPT_DIR)
TASKS_FILE = os.path.join(BASE_DIR, "TASKS.md")
ENV_FILE = os.path.join(BASE_DIR, ".env")

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
# Add scripts directory to path to allow importing sync_tasks
sys.path.append(SCRIPT_DIR)
import sync_tasks
import audit_logger

# Identidade do sistema para o audit trail.
# O webhook opera como processo automático — não há usuário humano interativo.
# ⚠ï¸  Isso é autorização, não autenticação: garantimos rastreabilidade da origem da ação.
WEBHOOK_USER_ID = "system/webhook"
WEBHOOK_ROLE = "system"

PORT = int(env.get("GOVERNAI_WEBHOOK_PORT") or os.environ.get("GOVERNAI_WEBHOOK_PORT", 8080))
SECRET = env.get("GOVERNAI_WEBHOOK_SECRET") or os.environ.get("GOVERNAI_WEBHOOK_SECRET")

# Thread-safe queue for execution
sync_queue = queue.Queue()

def sync_worker():
    while True:
        task = sync_queue.get()
        if task is None:
            break
        try:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] [WORKER] Iniciando subprocesso sync_tasks.py...")
            audit_logger.log_action(
                user_id=WEBHOOK_USER_ID,
                user_role=WEBHOOK_ROLE,
                action="sync",
                task_id="",
                allowed=True,
                details="Sincronização disparada via webhook do GitHub",
            )
            cmd = [sys.executable, os.path.join(SCRIPT_DIR, "sync_tasks.py")]
            res = subprocess.run(cmd, capture_output=True, text=True)
            if res.returncode == 0:
                print(f"[{datetime.now().strftime('%H:%M:%S')}] [WORKER] sync_tasks.py executado com sucesso.")
                if res.stdout:
                    for line in res.stdout.strip().split("\n"):
                        print(f"   [SYNC] {line}")
                audit_logger.log_action(
                    user_id=WEBHOOK_USER_ID,
                    user_role=WEBHOOK_ROLE,
                    action="sync",
                    task_id="",
                    allowed=True,
                    details="sync_tasks.py concluído com sucesso",
                )
            else:
                print(f"[{datetime.now().strftime('%H:%M:%S')}] [WORKER] [ERRO] sync_tasks.py falhou com código {res.returncode}.")
                if res.stderr:
                    print(res.stderr)
                audit_logger.log_action(
                    user_id=WEBHOOK_USER_ID,
                    user_role=WEBHOOK_ROLE,
                    action="sync",
                    task_id="",
                    allowed=False,
                    details=f"sync_tasks.py falhou com código {res.returncode}: {res.stderr[:200] if res.stderr else ''}",
                )
        except Exception as e:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] [WORKER] [ERRO] Exceção na execução de sync_tasks.py: {e}")
            audit_logger.log_action(
                user_id=WEBHOOK_USER_ID,
                user_role=WEBHOOK_ROLE,
                action="sync",
                task_id="",
                allowed=False,
                details=f"Exceção em sync_tasks.py: {e}",
            )
        finally:
            sync_queue.task_done()

# Start background thread
worker_thread = threading.Thread(target=sync_worker, daemon=True)
worker_thread.start()

debounce_timer = None
debounce_lock = threading.Lock()

def trigger_sync():
    global debounce_timer
    with debounce_lock:
        if debounce_timer is not None:
            debounce_timer.cancel()
            
        debounce_timer = threading.Timer(2.0, enqueue_sync)
        debounce_timer.start()
        print(f"[{datetime.now().strftime('%H:%M:%S')}] [DEBOUNCE] Sincronização reagendada para daqui a 2 segundos.")

def enqueue_sync():
    sync_queue.put(True)
    print(f"[{datetime.now().strftime('%H:%M:%S')}] [DEBOUNCE] Sinal de sincronização adicionado à fila.")

def update_local_task_status(task_id, status_tag):
    if not os.path.exists(TASKS_FILE):
        print(f"[RECEPTOR] [ERRO] {TASKS_FILE} não encontrado.")
        return False
        
    with open(TASKS_FILE, "r", encoding="utf-8") as f:
        content = f.read()
        
    sections = content.split("---")
    modified = False
    
    bracket_val = " "
    if status_tag == "in_progress":
        bracket_val = "/"
    elif status_tag == "done":
        bracket_val = "x"
        
    header_re = re.compile(rf"###\s+{task_id}\b")
    status_pattern = re.compile(r"(\*\*Status:\*\*\s*\[).*?(\])")
    
    for i, section in enumerate(sections):
        if header_re.search(section):
            if status_pattern.search(section):
                new_section = status_pattern.sub(rf"\g<1>{bracket_val}\g<2>", section)
                if new_section != section:
                    sections[i] = new_section
                    modified = True
                    print(f"[RECEPTOR] Status local da {task_id} alterado no TASKS.md para [{bracket_val}].")
            break
            
    if modified:
        with open(TASKS_FILE, "w", encoding="utf-8") as f:
            f.write("---".join(sections))
        return True
    return False

def append_local_task(task_id, title, status_tag):
    if not os.path.exists(TASKS_FILE):
        return False
        
    with open(TASKS_FILE, "r", encoding="utf-8") as f:
        content = f.read()
        
    if f"### {task_id}" in content:
        return False
        
    bracket_val = " "
    if status_tag == "in_progress":
        bracket_val = "/"
    elif status_tag == "done":
        bracket_val = "x"
        
    new_task_str = f"""

### {title}

**Status:** [{bracket_val}]
**Descrição:**
Tarefa importada automaticamente do board do GitHub Projects via webhook.

**Critérios de aceite:**
- Validar sincronização reversa para tarefas criadas via board.
"""
    if "## ✅ Concluídas" in content:
        parts = content.split("## ✅ Concluídas", 1)
        new_section_str = f"\n---\n{new_task_str.strip()}\n\n---\n\n## ✅ Concluídas" + parts[1]
        with open(TASKS_FILE, "w", encoding="utf-8") as f:
            f.write(parts[0] + new_section_str)
        print(f"[RECEPTOR] Nova tarefa {task_id} adicionada ao TASKS.md.")
        return True
    else:
        with open(TASKS_FILE, "a", encoding="utf-8") as f:
            f.write(f"\n\n---\n{new_task_str.strip()}\n")
        print(f"[RECEPTOR] Nova tarefa {task_id} apensada ao fim do TASKS.md.")
        return True

class WebhookHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        print(f"[{datetime.now().strftime('%H:%M:%S')}] [HTTP] " + (format % args))

    def do_POST(self):
        if self.path not in ["/", "/webhook"]:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b"Not Found")
            return
            
        event = self.headers.get("X-GitHub-Event")
        if event not in ["project_v2_item", "projects_v2_item"]:
            print(f"[RECEPTOR] Evento ignorado: {event}")
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"Evento ignorado")
            return
            
        content_length = int(self.headers.get("Content-Length", 0))
        payload = self.rfile.read(content_length)
        
        if SECRET:
            signature_header = self.headers.get("X-Hub-Signature-256")
            if not signature_header:
                print("[RECEPTOR] [ERRO] Assinatura X-Hub-Signature-256 ausente.")
                self.send_response(401)
                self.end_headers()
                self.wfile.write(b"Assinatura ausente")
                return
                
            if not signature_header.startswith("sha256="):
                print("[RECEPTOR] [ERRO] Formato de assinatura invalido.")
                self.send_response(401)
                self.end_headers()
                self.wfile.write(b"Formato de assinatura invalido")
                return
                
            expected_signature = hmac.new(
                SECRET.encode("utf-8"),
                payload,
                hashlib.sha256
            ).hexdigest()
            received_signature = signature_header[7:]
            
            if not hmac.compare_digest(expected_signature, received_signature):
                print("[RECEPTOR] [ERRO] Assinatura invalida.")
                self.send_response(401)
                self.end_headers()
                self.wfile.write(b"Assinatura invalida")
                return
                
        try:
            data = json.loads(payload.decode("utf-8"))
        except Exception as e:
            print(f"[RECEPTOR] [ERRO] Erro ao decodificar JSON: {e}")
            self.send_response(400)
            self.end_headers()
            self.wfile.write(b"JSON invalido")
            return
            
        action = data.get("action")
        item_data = data.get("projects_v2_item") or data.get("project_v2_item")
        
        if not item_data:
            print("[RECEPTOR] Payload sem dados do item do project.")
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"Sem dados do item")
            return
            
        item_node_id = item_data.get("node_id") or item_data.get("id")
        print(f"[RECEPTOR] Recebido evento '{action}' para o item {item_node_id}.")
        
        threading.Thread(target=self.reconcile_and_trigger, args=(item_node_id, action, data), daemon=True).start()
        
        self.send_response(202)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        res_body = json.dumps({"status": "accepted", "message": "Sincronizacao em andamento"})
        self.wfile.write(res_body.encode("utf-8"))
        
    def reconcile_and_trigger(self, item_node_id, action, payload_data):
        try:
            print("[RECEPTOR] Buscando dados do board no GitHub para reconciliacao...")
            project_id, status_field_id, status_options = sync_tasks.get_project_metadata()
            existing_items = sync_tasks.get_current_items(project_id)
            
            matched_title = None
            matched_info = None
            for title, info in existing_items.items():
                if str(info["id"]) == str(item_node_id):
                    matched_title = title
                    matched_info = info
                    break
                    
            if not matched_title:
                print(f"[RECEPTOR] Item {item_node_id} nao encontrado no board atual. Ignorando.")
                return
                
            match = re.search(r"^(TASK-\d+)\b", matched_title)
            if not match:
                print(f"[RECEPTOR] Item '{matched_title}' nao possui um ID de tarefa valido (TASK-XXX). Ignorando.")
                return
                
            task_id = match.group(1)
            remote_status = matched_info["status"]
            remote_body = matched_info["body"]
            
            status_tag = sync_tasks.normalize_status_tag(remote_status)
            
            local_tasks = sync_tasks.parse_tasks()
            task_ids = [t["id"] for t in local_tasks]
            
            local_changed = False
            
            if task_id in task_ids:
                if sync_tasks.should_sync_reverse(task_id, remote_status, remote_body):
                    print(f"[RECEPTOR] Divergencia detectada para {task_id}. Sincronizando reverso para status '{status_tag}'.")
                    local_changed = update_local_task_status(task_id, status_tag)
                else:
                    print(f"[RECEPTOR] Item {task_id} esta em conformidade. Nenhuma acao necessaria.")
            else:
                if action != "deleted":
                    print(f"[RECEPTOR] Tarefa {task_id} nao encontrada localmente. Criando no TASKS.md com status '{status_tag}'.")
                    local_changed = append_local_task(task_id, matched_title, status_tag)
                    
            if local_changed:
                trigger_sync()
                
        except Exception as e:
            print(f"[RECEPTOR] [ERRO] Falha ao processar reconciliacao: {e}")

def main():
    import governance_loader
    governance_loader.load_governance_rules()

    server_address = ("", PORT)
    httpd = HTTPServer(server_address, WebhookHandler)
    print(f"[{datetime.now().strftime('%H:%M:%S')}] [RECEPTOR] Servidor ativo na porta {PORT}...")
    if SECRET:
        print(f"[{datetime.now().strftime('%H:%M:%S')}] [RECEPTOR] Validacao de assinatura HMAC-SHA256 ativada.")
    else:
        print(f"[{datetime.now().strftime('%H:%M:%S')}] [RECEPTOR] [AVISO] GOVERNAI_WEBHOOK_SECRET nao configurado. Validacao de assinatura desativada.")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n[RECEPTOR] Servidor encerrado.")
        sys.exit(0)

if __name__ == "__main__":
    main()
