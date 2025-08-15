#!/bin/bash

echo "🔥🔥🔥 FORCE RESTART - ELIMINANDO CACHE 🔥🔥🔥"

# Matar todos os processos relacionados
echo "🚨 Matando processos..."
pkill -f "react-scripts" 2>/dev/null || true
pkill -f "npm start" 2>/dev/null || true
pkill -f "yarn start" 2>/dev/null || true
pkill -f "node.*3000" 2>/dev/null || true
pkill -f "node.*8050" 2>/dev/null || true

# Limpar todos os caches possíveis
echo "🧹 Limpando caches..."
rm -rf build/ 2>/dev/null || true
rm -rf dist/ 2>/dev/null || true
rm -rf .cache/ 2>/dev/null || true
rm -rf node_modules/.cache/ 2>/dev/null || true
rm -rf public/static/ 2>/dev/null || true

# Limpar npm cache
echo "📦 Limpando npm cache..."
npm cache clean --force 2>/dev/null || true

# Aguardar um pouco
echo "⏰ Aguardando..."
sleep 3

# Verificar se a URL está correta no código
echo "🔍 Verificando App.js..."
if grep -q "127.0.0.1:8001" src/App.js; then
    echo "✅ App.js contém URL correta (8001)"
else
    echo "❌ App.js não contém URL correta!"
    exit 1
fi

# Iniciar com porta específica
echo "🚀 Iniciando servidor na porta 3000..."
echo "📡 Backend deve estar em: http://127.0.0.1:8001/api"
echo "🌐 Frontend será: http://localhost:3000"
echo ""
echo "🔥 Se ainda aparecer 8050, é CACHE DO NAVEGADOR!"
echo "🔥 Use Ctrl+Shift+R para hard refresh!"
echo ""

# Iniciar servidor
PORT=3000 npm start