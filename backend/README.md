# Acode Lab Backend API

## 🚀 Como Iniciar o Servidor

### Método 1: Script Automático (Recomendado)
```bash
cd backend
./start_server.sh
```

### Método 2: Manual
```bash
cd backend

# Criar virtual environment (apenas na primeira vez)
python3 -m venv venv

# Ativar virtual environment
source venv/bin/activate

# Instalar dependências (apenas na primeira vez)
pip install -r requirements.txt

# Iniciar servidor
python main.py
```

## 🌐 URLs Importantes

- **API Base**: http://127.0.0.1:8001/api/
- **Documentação Automática**: http://127.0.0.1:8001/docs
- **Health Check**: http://127.0.0.1:8001/api/

## 📋 Endpoints Principais

### Perguntas
- `GET /api/questions/` - Lista perguntas
- `GET /api/questions/{id}` - Busca pergunta específica

### Autenticação
- `POST /api/auth/login` - Login do usuário
- `POST /api/auth/register` - Registro de novo usuário
- `GET /api/auth/me` - Informações do usuário atual

### Admin (Requer autenticação de admin)
- `POST /api/admin/bots/` - Criar bot usuário
- `GET /api/admin/stats` - Estatísticas do sistema
- `GET /api/admin/answers/pending` - Respostas pendentes de validação

## 🔑 Autenticação de Teste

Para testar como admin, use qualquer email que contenha "admin":
```bash
# Login como admin
curl -X POST "http://127.0.0.1:8001/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email": "admin@teste.com", "password": "qualquersenha"}'

# Login como usuário normal  
curl -X POST "http://127.0.0.1:8001/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email": "user@teste.com", "password": "qualquersenha"}'
```

## 🤖 Exemplo de Criação de Bot

```bash
curl -X POST "http://127.0.0.1:8001/api/admin/bots/" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer admin-token" \
  -d '{
    "username": "meu_bot",
    "email": "bot@exemplo.com",
    "pc_points": 100,
    "pcon_points": 50,
    "bio": "Bot para teste"
  }'
```

## 🔧 Configuração

O servidor utiliza as seguintes configurações do arquivo `.env`:

```env
MONGO_URL="mongodb://localhost:27017"
DB_NAME="test_database"
CORS_ORIGINS="*"
```

## 🛠️ Tecnologias

- **FastAPI** - Framework web
- **Uvicorn** - Servidor ASGI
- **Motor** - Driver assíncrono do MongoDB
- **Pydantic** - Validação de dados

## 📝 Notas

- O servidor roda na porta 8001
- CORS está habilitado para todas as origens (desenvolvimento)
- Atualmente usando dados mock para desenvolvimento
- Para produção, substituir por dados reais do MongoDB