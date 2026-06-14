import os
import sys
import json
import cli_colors

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(SCRIPT_DIR)
CONFIG_FILE = os.path.join(BASE_DIR, "governai.config.json")

def load_governance_rules():
    if not os.path.exists(CONFIG_FILE):
        print(cli_colors.red(f"[ERRO CRÍTICO] Arquivo de governança '{CONFIG_FILE}' não encontrado."), file=sys.stderr)
        print(cli_colors.red("O sistema falhou de forma segura. Execução abortada."), file=sys.stderr)
        sys.exit(1)
        
    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        print(cli_colors.red(f"[ERRO CRÍTICO] Falha ao ler ou analisar o arquivo JSON '{CONFIG_FILE}': {e}"), file=sys.stderr)
        print(cli_colors.red("O sistema falhou de forma segura. Execução abortada."), file=sys.stderr)
        sys.exit(1)
        
    if "governance" not in data:
        print(cli_colors.red(f"[ERRO CRÍTICO] Seção 'governance' ausente no arquivo '{CONFIG_FILE}'."), file=sys.stderr)
        print(cli_colors.red("O sistema falhou de forma segura. Execução abortada."), file=sys.stderr)
        sys.exit(1)
        
    return data["governance"]
