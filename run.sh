# Encerra o script se ocorrer erro
set -e

# Caminho da venv
VENV_DIR=".venv"

# Verifica se a venv existe
if [ ! -d "$VENV_DIR" ]; then
    echo "❌ Ambiente virtual não encontrado (.venv)"
    echo "👉 Crie com: python3 -m venv .venv"
    exit 1
fi

# Ativa a venv
source "$VENV_DIR/bin/activate"

# Variáveis de ambiente (opcional)
export PYTHONPATH=.

# Sobe a aplicação
echo "🚀 Iniciando Academic Flow API..."
uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000