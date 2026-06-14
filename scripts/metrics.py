import os
import sys
import json
import time
import contextlib
from datetime import datetime, timezone

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(SCRIPT_DIR)
METRICS_FILE = os.path.join(BASE_DIR, "logs", "metrics.json")
LOCK_FILE = METRICS_FILE + ".lock"
LOCK_TIMEOUT = 5.0  # segundos

def acquire_lock():
    for _ in range(50):  # tenta por até 5 segundos (50 * 0.1)
        try:
            fd = os.open(LOCK_FILE, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
            os.close(fd)
            return True
        except FileExistsError:
            try:
                # Verifica a idade do lock
                mtime = os.path.getmtime(LOCK_FILE)
                if time.time() - mtime > LOCK_TIMEOUT:
                    # Remove lock expirado
                    try:
                        os.remove(LOCK_FILE)
                        print("[MÉTRICAS] Lock expirado removido automaticamente.")
                    except FileNotFoundError:
                        pass
            except Exception:
                pass
            time.sleep(0.1)
    return False

def release_lock():
    try:
        os.remove(LOCK_FILE)
    except FileNotFoundError:
        pass

@contextlib.contextmanager
def metrics_transaction():
    acquired = acquire_lock()
    if not acquired:
        raise RuntimeError("Não foi possível adquirir o lock das métricas dentro do tempo limite.")
    try:
        metrics = load_metrics()
        yield metrics
        save_metrics(metrics)
    finally:
        release_lock()

def load_metrics():
    # Ensure logs folder exists
    logs_dir = os.path.dirname(METRICS_FILE)
    if not os.path.exists(logs_dir):
        os.makedirs(logs_dir)
        
    if os.path.exists(METRICS_FILE):
        try:
            with open(METRICS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_metrics(metrics):
    with open(METRICS_FILE, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)

def format_duration(seconds):
    if seconds is None:
        return "-"
    seconds = int(seconds)
    h = seconds // 3600
    m = (seconds % 3600) // 60
    s = seconds % 60
    if h > 0:
        return f"{h}h {m}m {s}s"
    elif m > 0:
        return f"{m}m {s}s"
    else:
        return f"{s}s"

def add_pending_task_raw(metrics, task_id):
    if task_id not in metrics:
        metrics[task_id] = {
            "status": "pending",
            "start_time": None,
            "end_time": None,
            "duration_seconds": None,
            "revisions": 0,
            "blocks": 0,
            "llm_calls": 0
        }

def add_pending_task(task_id):
    with metrics_transaction() as metrics:
        if task_id in metrics:
            print(f"[MÉTRICAS] Aviso: Tarefa {task_id} já registrada com status '{metrics[task_id].get('status')}'.")
            return
        add_pending_task_raw(metrics, task_id)
        print(f"[MÉTRICAS] Tarefa {task_id} registrada como pendente.")

def start_task(task_id):
    now_str = datetime.now(timezone.utc).isoformat()
    with metrics_transaction() as metrics:
        # Auto-cria como pending caso não exista
        add_pending_task_raw(metrics, task_id)
        
        status = metrics[task_id].get("status")
        if status in ["in_progress"]:
            print(f"[MÉTRICAS] Aviso: Tarefa {task_id} já está com status 'in_progress'. Ignorando inicialização.")
            return
        if status in ["done", "completed"]:
            print(f"[MÉTRICAS] Aviso: Tarefa {task_id} já está concluída ({status}). Ignorando inicialização.")
            return
            
        metrics[task_id]["status"] = "in_progress"
        if not metrics[task_id].get("start_time"):
            metrics[task_id]["start_time"] = now_str
        if metrics[task_id].get("llm_calls", 0) == 0:
            metrics[task_id]["llm_calls"] = 1
            
        print(f"[MÉTRICAS] Tarefa {task_id} em progresso. Início/Retomada: {now_str}.")

def increment_metric(task_id, metric_name):
    with metrics_transaction() as metrics:
        # Auto-cria como pending caso não exista
        add_pending_task_raw(metrics, task_id)
        
        metrics[task_id][metric_name] = metrics[task_id].get(metric_name, 0) + 1
        if metric_name != "llm_calls":
            metrics[task_id]["llm_calls"] = metrics[task_id].get("llm_calls", 0) + 1
            
        if metric_name == "blocks":
            metrics[task_id]["status"] = "blocked"
            print(f"[MÉTRICAS] Tarefa {task_id} BLOQUEADA. Total de bloqueios: {metrics[task_id]['blocks']}.")
        else:
            if metrics[task_id].get("status") == "pending":
                now_str = datetime.now(timezone.utc).isoformat()
                metrics[task_id]["status"] = "in_progress"
                metrics[task_id]["start_time"] = now_str
                print(f"[MÉTRICAS] Tarefa {task_id} iniciada implicitamente (trabalho ativo) em {now_str}.")
                
        print(f"[MÉTRICAS] Tarefa {task_id} atualizada: {metric_name} = {metrics[task_id][metric_name]}.")

def complete_task(task_id):
    now = datetime.now(timezone.utc)
    now_str = now.isoformat()
    
    with metrics_transaction() as metrics:
        # Auto-cria como pending caso não exista
        add_pending_task_raw(metrics, task_id)
        
        status = metrics[task_id].get("status")
        if status in ["done", "completed"]:
            print(f"[MÉTRICAS] Aviso: Tarefa {task_id} já está concluída ({status}). Ignorando conclusão.")
            return
            
        start_str = metrics[task_id].get("start_time")
        if not start_str:
            start_str = now_str
            metrics[task_id]["start_time"] = start_str
            
        try:
            start_time = datetime.fromisoformat(start_str)
            duration = (now - start_time).total_seconds()
        except Exception as e:
            duration = 0
            
        metrics[task_id]["status"] = "done"
        metrics[task_id]["end_time"] = now_str
        metrics[task_id]["duration_seconds"] = int(duration)
        metrics[task_id]["llm_calls"] = metrics[task_id].get("llm_calls", 0) + 1
        
        print(f"[MÉTRICAS] Tarefa {task_id} concluída em {now_str}. Duração: {format_duration(duration)}.")

def report_metrics():
    metrics = load_metrics()
    if not metrics:
        print("Nenhuma métrica registrada ainda.")
        return
        
    print("## 📊 Relatório de Métricas do GovernAI\n")
    print("| Tarefa | Status | Início (UTC) | Duração | Revisões (Commits) | Bloqueios | Invocações LLM |")
    print("| :--- | :--- | :--- | :--- | :--- | :--- | :--- |")
    
    for task_id, data in sorted(metrics.items()):
        status_raw = data.get("status", "in_progress")
        if status_raw in ["done", "completed"]:
            status = "✅ Concluída"
        elif status_raw == "blocked":
            status = "❌ Bloqueada"
        elif status_raw == "pending":
            status = "⏳ Pendente"
        else:
            status = "🚧 Em Progresso"
            
        start_t = "-"
        if data.get("start_time"):
            try:
                start_t = data["start_time"].split("T")[0] + " " + data["start_time"].split("T")[1][:8]
            except:
                start_t = "-"
                
        duration = format_duration(data.get("duration_seconds"))
        revisions = data.get("revisions", 0)
        blocks = data.get("blocks", 0)
        llm_calls = data.get("llm_calls", 0)
        
        print(f"| {task_id} | {status} | {start_t} | {duration} | {revisions} | {blocks} | {llm_calls} |")
    print()

def print_usage():
    print("Uso: python3 scripts/metrics.py <comando> <task_id>")
    print("Comandos:")
    print("  pending <task_id>  : Registra a task no backlog local (status pending)")
    print("  start <task_id>    : Inicia o cronômetro da task (status in_progress)")
    print("  revision <task_id> : Incrementa contador de revisões (commits)")
    print("  block <task_id>    : Incrementa bloqueios e define status para blocked")
    print("  step <task_id>     : Incrementa contador de passos (LLM calls)")
    print("  complete <task_id> : Finaliza o cronômetro e conclui a task (status done)")
    print("  report             : Exibe o relatório de métricas em Markdown")

def main():
    if len(sys.argv) < 2:
        print_usage()
        sys.exit(1)
        
    cmd = sys.argv[1].lower()
    
    if cmd == "report":
        report_metrics()
        sys.exit(0)
        
    if len(sys.argv) < 3:
        print("[ERRO] Identificador da task (TASK-XXX) é obrigatório para este comando.")
        print_usage()
        sys.exit(1)
        
    task_id = sys.argv[2].upper()
    
    if cmd in ["pending", "add"]:
        add_pending_task(task_id)
    elif cmd == "start":
        start_task(task_id)
    elif cmd == "revision":
        increment_metric(task_id, "revisions")
    elif cmd == "block":
        increment_metric(task_id, "blocks")
    elif cmd == "step":
        increment_metric(task_id, "llm_calls")
    elif cmd == "complete":
        complete_task(task_id)
    else:
        print(f"[ERRO] Comando desconhecido: {cmd}")
        print_usage()
        sys.exit(1)

if __name__ == "__main__":
    main()
