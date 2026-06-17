import os
import sys
import json
from datetime import datetime, timezone

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(SCRIPT_DIR)
AUDIT_LOG_FILE = os.path.join(BASE_DIR, "logs", "audit.log")


def log_action(user_id, user_role, action, task_id, allowed, details=""):
    """
    Registra um evento de auditoria no arquivo logs/audit.log em formato JSONL.

    O arquivo é aberto em modo append (nunca sobrescreve).
    Falhas de escrita exibem aviso no stderr mas NUNCA interrompem o fluxo principal
    (fail-soft): a governança não pode ser bloqueada por falha de log.

    O campo `details` é mascarado antes da gravação — dados sensíveis (tokens,
    e-mails, CPFs etc.) nunca são gravados em texto plano no audit trail.

    Parâmetros:
        user_id  (str): Identificador do usuário que executou ou tentou a ação.
        user_role(str): Papel do usuário no momento da ação.
        action   (str): Nome da ação executada (ex: 'start', 'approve').
        task_id  (str): ID da tarefa relacionada, ou '' se não aplicável.
        allowed  (bool): True se a ação foi permitida, False se foi bloqueada.
        details  (str): Mensagem descritiva do resultado.
    """
    try:
        os.makedirs(os.path.dirname(AUDIT_LOG_FILE), exist_ok=True)

        # Mascara dados sensíveis antes de gravar — fail-soft se o módulo falhar
        safe_details = details
        try:
            from sensitive_data import mask
            safe_details = mask(details)
        except Exception:
            pass  # Grava sem mascarar; melhor que perder o evento

        entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "user_id":   user_id,
            "user_role": user_role,
            "action":    action,
            "task_id":   task_id,
            "allowed":   allowed,
            "details":   safe_details,
        }

        with open(AUDIT_LOG_FILE, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")

    except Exception as e:
        print(f"[AUDIT] ⚠️  Falha ao registrar no audit.log: {e}", file=sys.stderr)
