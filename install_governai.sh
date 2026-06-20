#!/usr/bin/env bash

# Configuração de cores
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}=================================================${NC}"
echo -e "${BLUE}      🚀 Bem-vindo ao Instalador do GovernAI      ${NC}"
echo -e "${BLUE}=================================================${NC}"
echo ""

# 1. Verificar dependências
echo -e "${YELLOW}[1/4] Verificando dependências do sistema...${NC}"

if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Erro: Python 3 não encontrado. Instale o Python 3 para usar o GovernAI.${NC}"
    exit 1
fi
echo -e "${GREEN}✔ Python 3 encontrado.${NC}"

if ! command -v git &> /dev/null; then
    echo -e "${RED}Erro: Git não encontrado. Instale o Git para usar o GovernAI.${NC}"
    exit 1
fi
echo -e "${GREEN}✔ Git encontrado.${NC}"

# 2. Permissões de execução
echo -e "\n${YELLOW}[2/4] Configurando permissões de execução...${NC}"
chmod +x governai
if ls scripts/*.py 1> /dev/null 2>&1; then
    chmod +x scripts/*.py
fi
echo -e "${GREEN}✔ Permissões concedidas.${NC}"

# 3. Configuração Inicial (Safe Defaults)
echo -e "\n${YELLOW}[3/4] Preparando arquivos de configuração...${NC}"
BASE_DIR=$(pwd)

if [ ! -f "$BASE_DIR/.env" ]; then
    echo -e "${BLUE}Criando arquivo base .env...${NC}"
    cat > "$BASE_DIR/.env" << EOL
GITHUB_TOKEN=
PROJECT_NUMBER=
GITHUB_USER=
DISCORD_WEBHOOK_URL=
# GOVERNAI_USER_ID=your_id
EOL
    echo -e "${GREEN}✔ .env criado. (Lembre-se de preenchê-lo depois)${NC}"
else
    echo -e "${GREEN}✔ .env já existe, ignorando criação.${NC}"
fi

if [ ! -f "$BASE_DIR/governai.config.json" ]; then
    echo -e "${BLUE}Criando governai.config.json padrão...${NC}"
    cat > "$BASE_DIR/governai.config.json" << EOL
{
  "governance": {
    "require_approval": true,
    "fallback_user": "dev_local",
    "log_level": "info",
    "strict_mode": true
  },
  "rbac": {
    "enabled": false
  },
  "sensitive_data": {
    "enabled": true,
    "mode": "warn"
  }
}
EOL
    echo -e "${GREEN}✔ governai.config.json criado com regras seguras.${NC}"
else
    echo -e "${GREEN}✔ governai.config.json já existe, ignorando criação.${NC}"
fi

# 4. Instalação no PATH
echo -e "\n${YELLOW}[4/4] Instalando GovernAI no seu PATH...${NC}"
LOCAL_BIN="$HOME/.local/bin"

if [ ! -d "$LOCAL_BIN" ]; then
    mkdir -p "$LOCAL_BIN"
fi

# Criar o symlink apontando para o binário original
ln -sf "$BASE_DIR/governai" "$LOCAL_BIN/governai"

echo -e "${GREEN}✔ Link simbólico criado em $LOCAL_BIN/governai.${NC}"

# Verificar se ~/.local/bin está no PATH do usuário
if [[ ":$PATH:" != *":$LOCAL_BIN:"* ]]; then
    echo -e "${YELLOW}Atenção: O diretório $LOCAL_BIN não parece estar no seu PATH.${NC}"
    echo -e "Para usar o comando 'governai' de qualquer lugar, adicione a seguinte linha ao seu ~/.bashrc ou ~/.zshrc:"
    echo -e "  export PATH=\"\$HOME/.local/bin:\$PATH\""
fi

echo -e "\n${BLUE}=================================================${NC}"
echo -e "${GREEN}🎉 Instalação concluída com sucesso!${NC}"
echo -e "Você pode usar o comando ${YELLOW}governai run${NC} de qualquer lugar para iniciar."
echo -e "${BLUE}=================================================${NC}"
