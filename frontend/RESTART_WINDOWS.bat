@echo off
echo.
echo ===============================================
echo 🔥 RESTART WINDOWS FRONTEND - PORTA 8030 🔥
echo ===============================================
echo.

echo 🚨 Matando processos Node.js...
taskkill /f /im node.exe 2>nul
taskkill /f /im yarn.exe 2>nul
taskkill /f /im npm.exe 2>nul

echo.
echo 🧹 Limpando cache...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
if exist .cache rmdir /s /q .cache
if exist node_modules\.cache rmdir /s /q node_modules\.cache

echo.
echo 📦 Limpando npm cache...
npm cache clean --force 2>nul

echo.
echo ⏰ Aguardando 3 segundos...
timeout /t 3 /nobreak >nul

echo.
echo 🔍 Verificando arquivo App.js...
findstr /c:"localhost:8030" src\App.js >nul
if %errorlevel%==0 (
    echo ✅ App.js contém URL correta (8030)
) else (
    echo ❌ App.js não contém URL correta!
    pause
    exit /b 1
)

echo.
echo 🔍 Verificando arquivo .env...
findstr /c:"localhost:8030" .env >nul
if %errorlevel%==0 (
    echo ✅ .env contém URL correta (8030)
) else (
    echo ❌ .env não contém URL correta!
    pause
    exit /b 1
)

echo.
echo 🚀 Configurando variáveis...
set REACT_APP_BACKEND_URL=http://localhost:8030/api
set PORT=3001

echo.
echo 📡 Backend esperado: http://localhost:8030/api
echo 🌐 Frontend será: http://localhost:3001
echo.
echo 🔥 Se ainda aparecer erro 422, verifique o console!
echo 🔥 Use F12 para ver logs detalhados!
echo.

echo 🚀 Iniciando servidor...
yarn start

pause