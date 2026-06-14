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

def load_env():
    env_file = os.path.join(BASE_DIR, ".env")
    if os.path.exists(env_file):
        with open(env_file, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#"):
                    if "=" in line:
                        key, val = line.split("=", 1)
                        os.environ[key.strip()] = val.strip()

load_env()

LIMIT_REVISIONS = int(os.environ.get("GOVERNAI_LIMIT_REVISIONS", 3))
LIMIT_DURATION_SECS = int(os.environ.get("GOVERNAI_LIMIT_DURATION", 1800))  # 30 minutos
LIMIT_INACTIVE_SECS = int(os.environ.get("GOVERNAI_LIMIT_INACTIVE", 900))   # 15 minutos


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

def parse_iso_datetime(dt_str):
    if not dt_str:
        return None
    try:
        dt = datetime.fromisoformat(dt_str)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt
    except Exception:
        return None

def check_alerts(task_id, task_data, now):
    alerts = {}
    status = task_data.get("status", "pending")
    if status in ["done", "completed"]:
        return alerts
        
    revisions = task_data.get("revisions", 0)
    if revisions > LIMIT_REVISIONS:
        alerts["revisions"] = f"Excesso de Revisões ({revisions}/{LIMIT_REVISIONS})"
        
    if status in ["in_progress", "blocked"]:
        start_time_str = task_data.get("start_time")
        if start_time_str:
            start_time = parse_iso_datetime(start_time_str)
            if start_time:
                duration = (now - start_time).total_seconds()
                if duration > LIMIT_DURATION_SECS:
                    alerts["duration"] = f"Tempo de Execução Excessivo ({format_duration(duration)} > {format_duration(LIMIT_DURATION_SECS)})"
                    
        last_activity_str = task_data.get("last_activity_time")
        if last_activity_str:
            last_activity = parse_iso_datetime(last_activity_str)
            if last_activity:
                inactivity = (now - last_activity).total_seconds()
                if inactivity > LIMIT_INACTIVE_SECS:
                    alerts["inactive"] = f"Task Travada/Inativa ({format_duration(inactivity)} sem atividade)"
                    
    return alerts

def dispatch_notifications(task_id, new_status, old_status, new_alerts, added_alerts):
    reasons = []
    if new_status == "blocked" and old_status != "blocked":
        reasons.append("Tarefa transicionou para o estado BLOQUEADO")
        
    for alert_key in sorted(added_alerts):
        reasons.append(new_alerts[alert_key])
        
    if not reasons:
        return
        
    message = "; ".join(reasons)
    
    import threading
    try:
        import notifier
        t = threading.Thread(target=notifier.send_notifications, args=(task_id, message), daemon=False)
        t.start()
    except Exception as e:
        print(f"[MÉTRICAS] [ERRO] Falha ao despachar notificacoes: {e}")

def update_activity_and_alerts(task_id, task_data, now, old_status, old_alerts_keys):
    new_status = task_data.get("status", "pending")
    new_alerts = check_alerts(task_id, task_data, now)
    
    now_str = now.isoformat()
    task_data["last_activity_time"] = now_str
    
    new_alerts_keys = set(new_alerts.keys())
    
    should_print = False
    
    added_alerts = new_alerts_keys - old_alerts_keys
    if added_alerts:
        should_print = True
        
    if old_status != new_status and new_alerts_keys:
        should_print = True
        
    if old_alerts_keys and not new_alerts_keys:
        print(f"✅ [MÉTRICAS] Alertas resolvidos para a tarefa {task_id}. A tarefa está em conformidade.")
        task_data["active_alerts"] = []
        return
        
    if should_print:
        print(f"⚠️ [ALERTA DE GOVERNANÇA] tarefa {task_id} ({new_status}):")
        for k in sorted(new_alerts_keys):
            print(f"   - {new_alerts[k]}")
            
    task_data["active_alerts"] = sorted(list(new_alerts_keys))
    
    dispatch_notifications(task_id, new_status, old_status, new_alerts, added_alerts)

def add_pending_task_raw(metrics, task_id):
    if task_id not in metrics:
        metrics[task_id] = {
            "status": "pending",
            "start_time": None,
            "end_time": None,
            "duration_seconds": None,
            "revisions": 0,
            "blocks": 0,
            "llm_calls": 0,
            "last_activity_time": None,
            "active_alerts": []
        }

def add_pending_task(task_id):
    now = datetime.now(timezone.utc)
    with metrics_transaction() as metrics:
        if task_id in metrics:
            print(f"[MÉTRICAS] Aviso: Tarefa {task_id} já registrada com status '{metrics[task_id].get('status')}'.")
            return
        add_pending_task_raw(metrics, task_id)
        metrics[task_id]["last_activity_time"] = now.isoformat()
        print(f"[MÉTRICAS] Tarefa {task_id} registrada como pendente.")

def start_task(task_id):
    now = datetime.now(timezone.utc)
    now_str = now.isoformat()
    with metrics_transaction() as metrics:
        add_pending_task_raw(metrics, task_id)
        
        task_data = metrics[task_id]
        old_status = task_data.get("status")
        old_alerts = set(task_data.get("active_alerts", []) if isinstance(task_data.get("active_alerts"), list) else [])
        
        status = task_data.get("status")
        if status in ["in_progress"]:
            print(f"[MÉTRICAS] Aviso: Tarefa {task_id} já está com status 'in_progress'. Ignorando inicialização.")
            return
        if status in ["done", "completed"]:
            print(f"[MÉTRICAS] Aviso: Tarefa {task_id} já está concluída ({status}). Ignorando inicialização.")
            return
            
        task_data["status"] = "in_progress"
        if not task_data.get("start_time"):
            task_data["start_time"] = now_str
        if task_data.get("llm_calls", 0) == 0:
            task_data["llm_calls"] = 1
            
        print(f"[MÉTRICAS] Tarefa {task_id} em progresso. Início/Retomada: {now_str}.")
        
        update_activity_and_alerts(task_id, task_data, now, old_status, old_alerts)

def increment_metric(task_id, metric_name):
    now = datetime.now(timezone.utc)
    with metrics_transaction() as metrics:
        add_pending_task_raw(metrics, task_id)
        
        task_data = metrics[task_id]
        old_status = task_data.get("status")
        old_alerts = set(task_data.get("active_alerts", []) if isinstance(task_data.get("active_alerts"), list) else [])
        
        task_data[metric_name] = task_data.get(metric_name, 0) + 1
        if metric_name != "llm_calls":
            task_data["llm_calls"] = task_data.get("llm_calls", 0) + 1
            
        if metric_name == "blocks":
            task_data["status"] = "blocked"
            print(f"[MÉTRICAS] Tarefa {task_id} BLOQUEADA. Total de bloqueios: {task_data['blocks']}.")
        else:
            if task_data.get("status") == "pending":
                now_str = now.isoformat()
                task_data["status"] = "in_progress"
                task_data["start_time"] = now_str
                print(f"[MÉTRICAS] Tarefa {task_id} iniciada implicitamente (trabalho ativo) em {now_str}.")
                
        print(f"[MÉTRICAS] Tarefa {task_id} atualizada: {metric_name} = {task_data[metric_name]}.")
        
        update_activity_and_alerts(task_id, task_data, now, old_status, old_alerts)

def complete_task(task_id):
    now = datetime.now(timezone.utc)
    now_str = now.isoformat()
    
    with metrics_transaction() as metrics:
        add_pending_task_raw(metrics, task_id)
        
        task_data = metrics[task_id]
        old_status = task_data.get("status")
        old_alerts = set(task_data.get("active_alerts", []) if isinstance(task_data.get("active_alerts"), list) else [])
        
        status = task_data.get("status")
        if status in ["done", "completed"]:
            print(f"[MÉTRICAS] Aviso: Tarefa {task_id} já está concluída ({status}). Ignorando conclusão.")
            return
            
        start_str = task_data.get("start_time")
        if not start_str:
            start_str = now_str
            task_data["start_time"] = start_str
            
        try:
            start_time = datetime.fromisoformat(start_str)
            duration = (now - start_time).total_seconds()
        except Exception as e:
            duration = 0
            
        task_data["status"] = "done"
        task_data["end_time"] = now_str
        task_data["duration_seconds"] = int(duration)
        task_data["llm_calls"] = task_data.get("llm_calls", 0) + 1
        
        print(f"[MÉTRICAS] Tarefa {task_id} concluída em {now_str}. Duração: {format_duration(duration)}.")
        
        update_activity_and_alerts(task_id, task_data, now, old_status, old_alerts)

def report_metrics():
    metrics = load_metrics()
    if not metrics:
        print("Nenhuma métrica registrada ainda.")
        return
        
    print("## 📊 Relatório de Métricas do GovernAI\n")
    print("| Tarefa | Status | Início (UTC) | Duração | Revisões (Commits) | Bloqueios | Invocações LLM | Alertas |")
    print("| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |")
    
    now = datetime.now(timezone.utc)
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
        
        alerts_dict = check_alerts(task_id, data, now)
        if alerts_dict:
            alerts_str = ", ".join(alerts_dict.values())
        else:
            alerts_str = "-"
            
        print(f"| {task_id} | {status} | {start_t} | {duration} | {revisions} | {blocks} | {llm_calls} | {alerts_str} |")
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
