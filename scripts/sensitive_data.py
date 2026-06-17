"""
GovernAI — Detecção e mascaramento de dados sensíveis.

Fluxo de uso (ordem obrigatória):
    findings = scan(text)          # 1. detecta — sem vazar o valor original
    if findings:
        pass                       # 2. warn / block — responsabilidade do chamador
    safe_text = mask(text)         # 3. mascara para log / exibição / sync

Módulo puro: sem dependências externas (apenas 're').
Falha silenciosamente em caso de erro — nunca interrompe o sistema.
"""

import re


# ---------------------------------------------------------------------------
# Fast-check
# Triagem de baixo custo antes de rodar qualquer regex.
# Todos os marcadores em minúsculo — checados contra text.lower().
# ---------------------------------------------------------------------------
_FAST_CHECK_MARKERS = (
    "@",        # e-mail
    "ghp_",     # GitHub Personal Access Token
    "token",    # API key genérica / Discord webhooks
    "key",      # API key genérica
    "http",     # Discord Webhook URL
    "password", # senha inline (EN)
    "passwd",   # senha inline (variante)
    "senha",    # senha inline (PT-BR)
    "begin",    # chave privada PEM (-----BEGIN PRIVATE KEY-----)
    "cpf",      # CPF acompanhado de rótulo (ex: "CPF: 123...")
    "9-",       # dígito-traço — presente em CPF formatado (NNN.NNN.NNN-NN)
)


# ---------------------------------------------------------------------------
# Regexes (compilados uma única vez no import do módulo)
# ---------------------------------------------------------------------------

# GitHub Personal Access Token: ghp_ + 10–255 caracteres alfanuméricos
_RE_GITHUB_TOKEN = re.compile(r"ghp_[A-Za-z0-9]{10,255}")

# Discord Webhook URL — aplicado ANTES do padrão de API key genérica
_RE_DISCORD = re.compile(
    r"https://discord(?:app)?\.com/api/webhooks/[^\s\"'<>]+",
    re.IGNORECASE,
)

# API Key / Token genérico inline (key=, token=, secret=, KEY=, GITHUB_TOKEN=, api_key=...)
# Lookbehind negativo: evita "monkey=banana" (letra imediatamente antes do padrão)
# Lookahead negativo no valor: evita casar com máscaras já aplicadas (ex: [API_KEY], ghp_****)
_RE_API_KEY = re.compile(
    r"(?<![A-Za-z])(?:key|token|secret)\s*[=:]\s*(?!\[)(?!ghp_\*+)\S{6,}",
    re.IGNORECASE,
)

# E-mail
_RE_EMAIL = re.compile(r"[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}")

# CPF formatado APENAS (123.456.789-00) — sem raw, para evitar falso positivo
_RE_CPF = re.compile(r"\b\d{3}\.\d{3}\.\d{3}-\d{2}\b")

# Senha inline: password=, passwd=, senha= + valor não-espaço de 3+ chars
# Lookahead negativo: evita casar com máscaras já aplicadas
_RE_SENHA = re.compile(
    r"(?<![A-Za-z])(?:password|passwd|senha)\s*[=:]\s*(?!\[)\S{3,}",
    re.IGNORECASE,
)

# Chave privada PEM
_RE_PEM = re.compile(
    r"-----BEGIN\s+(?:RSA\s+|EC\s+|DSA\s+)?PRIVATE\s+KEY-----",
    re.IGNORECASE,
)


# ---------------------------------------------------------------------------
# Funções de masked_preview
# NUNCA retornam o valor original completo — apenas representação parcial.
# ---------------------------------------------------------------------------

def _preview_github(_: str) -> str:
    return "ghp_****"


def _preview_discord(_: str) -> str:
    return "[DISCORD_WEBHOOK]"


def _preview_api_key(value: str) -> str:
    # Preserva o nome da chave, oculta o valor: "GITHUB_TOKEN=[API_KEY]"
    key_name = re.split(r"[=:\s]", value.strip(), maxsplit=1)[0]
    return f"{key_name}=[API_KEY]"


def _preview_email(value: str) -> str:
    # us***@dominio.com
    local, domain = value.split("@", 1)
    hidden = (local[:2] + "***") if len(local) > 2 else ("*" * len(local))
    return f"{hidden}@{domain}"


def _preview_cpf(_: str) -> str:
    return "***.***.***-**"


def _preview_senha(value: str) -> str:
    # Preserva o nome da chave, oculta o valor: "password=[SENHA]"
    key_name = re.split(r"[=:\s]", value.strip(), maxsplit=1)[0]
    return f"{key_name}=[SENHA]"


def _preview_pem(_: str) -> str:
    return "[CHAVE_PRIVADA]"


# ---------------------------------------------------------------------------
# Funções de substituição para mask()
# Usadas como callable no re.sub() — recebem o objeto match.
# ---------------------------------------------------------------------------

def _mask_github(_) -> str:
    return "ghp_****"


def _mask_discord(_) -> str:
    return "[DISCORD_WEBHOOK]"


def _mask_api_key(match) -> str:
    key_name = re.split(r"[=:\s]", match.group().strip(), maxsplit=1)[0]
    return f"{key_name}=[API_KEY]"


def _mask_email(_) -> str:
    return "[EMAIL]"


def _mask_cpf(_) -> str:
    return "[CPF]"


def _mask_senha(match) -> str:
    key_name = re.split(r"[=:\s]", match.group().strip(), maxsplit=1)[0]
    return f"{key_name}=[SENHA]"


def _mask_pem(_) -> str:
    return "[CHAVE_PRIVADA]"


# ---------------------------------------------------------------------------
# Registro de padrões
# Tupla: (tipo, regex, fn_preview, fn_mask)
# Ordem importa: mais específico primeiro (GitHub antes de API key genérica,
# Discord antes de http genérico).
# ---------------------------------------------------------------------------
_PATTERNS = (
    ("github_token",    _RE_GITHUB_TOKEN, _preview_github,   _mask_github),
    ("discord_webhook", _RE_DISCORD,      _preview_discord,  _mask_discord),
    ("api_key",         _RE_API_KEY,      _preview_api_key,  _mask_api_key),
    ("email",           _RE_EMAIL,        _preview_email,     _mask_email),
    ("cpf",             _RE_CPF,          _preview_cpf,       _mask_cpf),
    ("senha",           _RE_SENHA,        _preview_senha,     _mask_senha),
    ("chave_privada",   _RE_PEM,          _preview_pem,       _mask_pem),
)


# ---------------------------------------------------------------------------
# API pública
# ---------------------------------------------------------------------------

def scan(text: str) -> list:
    """
    Varre o texto em busca de dados sensíveis.

    Retorna lista de dicts:
        [{"type": str, "masked_preview": str}, ...]

    - "type": categoria do dado detectado (ex: "email", "github_token")
    - "masked_preview": representação parcialmente oculta — NUNCA o valor completo

    Retorna [] para texto vazio, não-string ou sem indícios.
    """
    if not isinstance(text, str) or not text:
        return []
    if not _needs_check(text):
        return []

    findings = []
    try:
        for pattern_type, regex, preview_fn, _ in _PATTERNS:
            for match in regex.finditer(text):
                findings.append({
                    "type":           pattern_type,
                    "masked_preview": preview_fn(match.group()),
                })
    except Exception:
        pass  # Fail silently

    return findings


def has_sensitive(text: str) -> bool:
    """
    Retorna True se o texto contiver qualquer dado sensível.
    Usa fast-check antes dos regex — eficiente para textos limpos.
    """
    if not isinstance(text, str) or not text:
        return False
    if not _needs_check(text):
        return False

    try:
        return any(regex.search(text) for _, regex, _, _ in _PATTERNS)
    except Exception:
        return False


def mask(text: str) -> str:
    """
    Retorna o texto com todos os dados sensíveis substituídos pelas máscaras.
    Seguro para gravar em logs, exibir no terminal ou sincronizar remotamente.

    Padrões aplicados do mais específico ao mais genérico.
    Em caso de erro, retorna o texto original sem modificação (fail-soft).
    """
    if not isinstance(text, str) or not text:
        return text
    if not _needs_check(text):
        return text

    result = text
    try:
        for _, regex, _, mask_fn in _PATTERNS:
            result = regex.sub(mask_fn, result)
    except Exception:
        return text  # Fail-soft: retorna original

    return result


# ---------------------------------------------------------------------------
# Interno
# ---------------------------------------------------------------------------

def _needs_check(text: str) -> bool:
    """
    Fast check: retorna False se nenhum marcador de risco estiver presente.
    Evita overhead de regex para o caso mais comum (texto sem dados sensíveis).
    """
    lower = text.lower()
    return any(marker in lower for marker in _FAST_CHECK_MARKERS)
