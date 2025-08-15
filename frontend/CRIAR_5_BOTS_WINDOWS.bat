@echo off
echo.
echo ===============================================
echo 🤖 CRIANDO 5 BOTS AUTOMATICAMENTE - WINDOWS 🤖
echo ===============================================
echo.

echo 🔍 Verificando se backend está rodando...
curl -s "http://localhost:8030/api/" >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Backend não está rodando em http://localhost:8030/api/
    echo ❌ Certifique-se de que o backend está ativo!
    pause
    exit /b 1
)
echo ✅ Backend está online!
echo.

echo 🤖 Criando Bot #1: CodeMaster_AI...
curl -X POST "http://localhost:8030/api/admin/bots/" ^
  -H "Content-Type: application/json" ^
  -H "Authorization: Bearer admin-token" ^
  -d "{\"username\": \"CodeMaster_AI\", \"email\": \"codemaster@bots.com\", \"bio\": \"Especialista em múltiplas linguagens de programação\", \"pc_points\": 1500, \"pcon_points\": 750, \"rank\": \"Especialista\", \"location\": \"São Paulo, Brasil\", \"skills\": [\"Python\", \"JavaScript\", \"Java\", \"C++\", \"Docker\"]}"
echo.
echo ✅ Bot #1 criado!
timeout /t 2 /nobreak >nul

echo 🤖 Criando Bot #2: WebDev_Expert...
curl -X POST "http://localhost:8030/api/admin/bots/" ^
  -H "Content-Type: application/json" ^
  -H "Authorization: Bearer admin-token" ^
  -d "{\"username\": \"WebDev_Expert\", \"email\": \"webdev@bots.com\", \"bio\": \"Desenvolvimento web full-stack com React e Node.js\", \"pc_points\": 1200, \"pcon_points\": 600, \"rank\": \"Avançado\", \"location\": \"Rio de Janeiro, Brasil\", \"skills\": [\"React\", \"Node.js\", \"TypeScript\", \"MongoDB\", \"AWS\"]}"
echo.
echo ✅ Bot #2 criado!
timeout /t 2 /nobreak >nul

echo 🤖 Criando Bot #3: DataScience_Bot...
curl -X POST "http://localhost:8030/api/admin/bots/" ^
  -H "Content-Type: application/json" ^
  -H "Authorization: Bearer admin-token" ^
  -d "{\"username\": \"DataScience_Bot\", \"email\": \"datascience@bots.com\", \"bio\": \"Análise de dados e machine learning com Python e R\", \"pc_points\": 1800, \"pcon_points\": 900, \"rank\": \"Mestre\", \"location\": \"Belo Horizonte, Brasil\", \"skills\": [\"Python\", \"R\", \"TensorFlow\", \"Pandas\", \"SQL\"]}"
echo.
echo ✅ Bot #3 criado!
timeout /t 2 /nobreak >nul

echo 🤖 Criando Bot #4: Mobile_Developer...
curl -X POST "http://localhost:8030/api/admin/bots/" ^
  -H "Content-Type: application/json" ^
  -H "Authorization: Bearer admin-token" ^
  -d "{\"username\": \"Mobile_Developer\", \"email\": \"mobile@bots.com\", \"bio\": \"Desenvolvimento mobile nativo e cross-platform\", \"pc_points\": 1000, \"pcon_points\": 500, \"rank\": \"Intermediário\", \"location\": \"Brasília, Brasil\", \"skills\": [\"Flutter\", \"React Native\", \"Android\", \"iOS\", \"Dart\"]}"
echo.
echo ✅ Bot #4 criado!
timeout /t 2 /nobreak >nul

echo 🤖 Criando Bot #5: DevOps_Guru...
curl -X POST "http://localhost:8030/api/admin/bots/" ^
  -H "Content-Type: application/json" ^
  -H "Authorization: Bearer admin-token" ^
  -d "{\"username\": \"DevOps_Guru\", \"email\": \"devops@bots.com\", \"bio\": \"Infraestrutura e automação com Docker e Kubernetes\", \"pc_points\": 2000, \"pcon_points\": 1000, \"rank\": \"Guru\", \"location\": \"Porto Alegre, Brasil\", \"skills\": [\"Docker\", \"Kubernetes\", \"AWS\", \"Azure\", \"Jenkins\"]}"
echo.
echo ✅ Bot #5 criado!

echo.
echo ===============================================
echo 🎉 TODOS OS 5 BOTS FORAM CRIADOS COM SUCESSO! 🎉
echo ===============================================
echo.

echo 📊 BOTS CRIADOS:
echo 1. 🤖 CodeMaster_AI (Especialista) - 1500 PC / 750 PCon
echo 2. 🌐 WebDev_Expert (Avançado) - 1200 PC / 600 PCon  
echo 3. 📊 DataScience_Bot (Mestre) - 1800 PC / 900 PCon
echo 4. 📱 Mobile_Developer (Intermediário) - 1000 PC / 500 PCon
echo 5. ⚙️ DevOps_Guru (Guru) - 2000 PC / 1000 PCon
echo.

echo ✅ Agora você pode ver os bots no frontend!
echo 🌐 Acesse: http://localhost:3001/admin
echo.

pause