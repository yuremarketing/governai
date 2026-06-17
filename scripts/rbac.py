import os
import sys
import json

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(SCRIPT_DIR)
USERS_FILE = os.path.join(BASE_DIR, "users.json")
CONFIG_FILE = os.path.join(BASE_DIR, "governai.config.json")

# ---------------------------------------------------------------------------
# Mapeamento estático: papel → conjunto de ações permitidas
# ---------------------------------------------------------------------------
ROLES_PERMISSIONS = {
    "admin":     {"start", "approve", "complete", "block", "sync", "confirm", "report"},
    "reviewer":  {"approve", "report", "sync"},
    "developer": {"start", "complete", "block", "report", "sync", "confirm"},
    "viewer":    {"report"},
    # Papel interno do sistema — usado por processos automáticos (ex: webhook)
    "system":    {"sync"},
}

# Nomes amigáveis das ações para mensagens ao usuário
ACTION_LABELS = {
    "start":    "iniciar tarefa",
    "approve":  "aprovar plano",
    "complete": "concluir tarefa",
    "block":    "bloquear tarefa",
    "sync":     "sincronizar tarefas",
    "confirm":  "executar comando no terminal",
    "report":   "visualizar relatório",
}

# Nomes amigáveis dos papéis
ROLE_LABELS = {
    "admin":     "Administrador",
    "reviewer":  "Revisor",
    "developer": "Desenvolvedor",
    "viewer":    "Observador",
    "system":    "Sistema",
}


# ---------------------------------------------------------------------------
# Funções de carregamento
# ---------------------------------------------------------------------------

def _load_config():
    """Carrega governai.config.json. Retorna {} em caso de falha."""
    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def load_users():
    """Lê users.json e retorna a lista de usuários. Retorna [] se ausente ou inválido."""
    if not os.path.exists(USERS_FILE):
        return []
    try:
        with open(USERS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data.get("users", [])
    except Exception:
        return []


def is_rbac_enabled():
    """Retorna True se o RBAC está ativo no governai.config.json."""
    config = _load_config()
    return config.get("rbac", {}).get("enabled", False)


# ---------------------------------------------------------------------------
# Resolução do usuário ativo
# ---------------------------------------------------------------------------

def get_current_user():
    """
    Resolve a identidade do usuário ativo. Retorna (user_id: str, role: str).

    Prioridade de resolução (quando rbac.enabled = true):
      1. Variável de ambiente GOVERNAI_USER_ID
      2. Variável de ambiente USER / USERNAME (Unix/Windows)
      3. default_role definido em governai.config.json → rbac.default_role

    Quando rbac.enabled = false: retorna ("solo", default_role) sem consultar users.json.

    ⚠️  Limitação conhecida (v1): o sistema implementa AUTORIZAÇÃO, não AUTENTICAÇÃO.
         Qualquer processo pode definir GOVERNAI_USER_ID livremente. A responsabilidade
         de autenticar o usuário (ex: via login, SSO) fica para versões futuras do GovernAI.
    """
    config = _load_config()
    rbac_cfg = config.get("rbac", {})
    default_role = rbac_cfg.get("default_role", "admin")

    # Modo solo: RBAC desativado — nenhuma validação de permissão será executada
    if not rbac_cfg.get("enabled", False):
        return ("solo", default_role)

    users = load_users()

    def find_user_by_id(uid):
        for u in users:
            if u.get("id") == uid:
                return (u["id"], u.get("role", default_role))
        return None

    # Prioridade 1: GOVERNAI_USER_ID
    env_uid = os.environ.get("GOVERNAI_USER_ID", "").strip()
    if env_uid:
        found = find_user_by_id(env_uid)
        if found:
            return found
        # Definido mas não encontrado em users.json → usa default_role como segurança
        return (env_uid, default_role)

    # Prioridade 2: USER / USERNAME do sistema operacional
    system_user = (os.environ.get("USER") or os.environ.get("USERNAME") or "").strip()
    if system_user:
        found = find_user_by_id(system_user)
        if found:
            return found
        # Não coincide com nenhum id cadastrado → cai para default_role

    # Prioridade 3: default_role do config
    return ("default", default_role)


# ---------------------------------------------------------------------------
# Verificação e exigência de permissão
# ---------------------------------------------------------------------------

def check_permission(user_id, role, action):
    """
    Verifica se o papel tem permissão para a ação.

    Retorna (allowed: bool, message: str).
    Quando RBAC está desativado, sempre retorna (True, "RBAC desativado").
    """
    if not is_rbac_enabled():
        return (True, "RBAC desativado — acesso permitido.")

    allowed_actions = ROLES_PERMISSIONS.get(role, set())
    action_label = ACTION_LABELS.get(action, f"'{action}'")
    role_label = ROLE_LABELS.get(role, role)

    if action in allowed_actions:
        return (True, f"Acesso permitido: {role_label} pode {action_label}.")

    # Constrói mensagem útil: quais papéis têm permissão
    roles_that_can = [r for r, perms in ROLES_PERMISSIONS.items()
                      if action in perms and r != "system"]
    roles_str = ", ".join(ROLE_LABELS.get(r, r) for r in roles_that_can)

    message = (
        f"Você não tem permissão para {action_label}.\n"
        f"   Seu papel atual: {role_label} ({user_id})\n"
        f"   Papéis autorizados: {roles_str}\n"
        f"   → Solicite a um usuário com papel '{roles_that_can[0] if roles_that_can else 'admin'}' que execute esta ação."
    )
    return (False, message)


def require_permission(user_id, role, action, task_id=""):
    """
    Exige permissão para executar uma ação. Se negada:
      1. Registra a tentativa negada no audit.log (ANTES de sair)
      2. Exibe mensagem clara ao usuário
      3. Chama sys.exit(1)

    Quando RBAC está desativado, retorna True imediatamente.
    """
    if not is_rbac_enabled():
        return True

    allowed, message = check_permission(user_id, role, action)

    # Registra no audit log ANTES de qualquer sys.exit (ações negadas também são auditadas)
    try:
        import audit_logger
        audit_logger.log_action(
            user_id=user_id,
            user_role=role,
            action=action,
            task_id=task_id,
            allowed=allowed,
            details=message,
        )
    except Exception as audit_err:
        print(f"[AUDIT] ⚠️  Não foi possível registrar no audit.log: {audit_err}", file=sys.stderr)

    if not allowed:
        try:
            import cli_colors
            print()
            print(cli_colors.red("=" * 52))
            print(cli_colors.bold(cli_colors.red("  GovernAI — Acesso Negado")))
            print(cli_colors.red("=" * 52))
            for line in message.split("\n"):
                print(cli_colors.red(f"  {line}"))
            print(cli_colors.red("=" * 52))
            print()
        except ImportError:
            print(f"\n[ACESSO NEGADO] {message}\n", file=sys.stderr)
        sys.exit(1)

    return True
