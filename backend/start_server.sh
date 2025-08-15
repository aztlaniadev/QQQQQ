#!/bin/bash

echo "🚀 Iniciando servidor Acode Lab API..."

# Navegar para o diretório do backend
cd "$(dirname "$0")"

# Ativar virtual environment
if [ ! -d "venv" ]; then
    echo "⚠️  Virtual environment não encontrado. Criando..."
    python3 -m venv venv
    source venv/bin/activate
    echo "📦 Instalando dependências..."
    pip install -r requirements.txt
else
    echo "✅ Ativando virtual environment..."
    source venv/bin/activate
fi

# Verificar se as dependências estão instaladas
echo "🔍 Verificando dependências..."
python -c "import fastapi, uvicorn; print('✅ Dependências OK')" 2>/dev/null || {
    echo "📦 Instalando dependências..."
    pip install -r requirements.txt
}

# Iniciar servidor
echo "🌐 Iniciando servidor na porta 8001..."
echo "📡 API URL: http://127.0.0.1:8001/api/"
echo "📖 Documentação: http://127.0.0.1:8001/docs"
echo ""
echo "Para parar o servidor, pressione Ctrl+C"
echo ""

python main.py