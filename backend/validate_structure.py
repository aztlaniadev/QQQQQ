#!/usr/bin/env python3
"""
Validação da estrutura do backend Acode Lab
Verifica se todos os arquivos essenciais foram criados corretamente
"""
import os
from pathlib import Path

def check_file_exists(filepath, description=""):
    """Verifica se um arquivo existe"""
    if os.path.exists(filepath):
        print(f"✅ {filepath} {description}")
        return True
    else:
        print(f"❌ {filepath} {description}")
        return False

def check_directory_exists(dirpath, description=""):
    """Verifica se um diretório existe"""
    if os.path.isdir(dirpath):
        print(f"✅ {dirpath}/ {description}")
        return True
    else:
        print(f"❌ {dirpath}/ {description}")
        return False

def main():
    """Executa validação completa"""
    print("🔍 VALIDANDO ESTRUTURA DA FINALIZAÇÃO 1")
    print("=" * 50)
    
    backend_path = Path(__file__).parent
    total_checks = 0
    passed_checks = 0
    
    # Estrutura de diretórios
    directories = [
        ("app", "Diretório principal da aplicação"),
        ("app/core", "Configurações core"),
        ("app/models", "Modelos Pydantic"),
        ("app/routers", "Rotas FastAPI"),
        ("app/services", "Lógica de negócio"),
        ("app/utils", "Utilitários"),
        ("tests", "Testes automatizados")
    ]
    
    print("\n📁 ESTRUTURA DE DIRETÓRIOS:")
    for dir_name, description in directories:
        total_checks += 1
        if check_directory_exists(backend_path / dir_name, description):
            passed_checks += 1
    
    # Arquivos core
    core_files = [
        ("app/__init__.py", "Módulo app"),
        ("app/main.py", "Aplicação FastAPI principal"),
        ("app/core/__init__.py", "Módulo core"),
        ("app/core/config.py", "Configurações"),
        ("app/core/security.py", "Segurança e JWT"),
        ("app/core/database.py", "Conexão MongoDB"),
    ]
    
    print("\n🔧 ARQUIVOS CORE:")
    for file_name, description in core_files:
        total_checks += 1
        if check_file_exists(backend_path / file_name, description):
            passed_checks += 1
    
    # Modelos
    model_files = [
        ("app/models/__init__.py", "Módulo models"),
        ("app/models/base.py", "Modelos base"),
        ("app/models/user.py", "Modelos de usuário"),
        ("app/models/qa.py", "Modelos Q&A"),
    ]
    
    print("\n📋 MODELOS:")
    for file_name, description in model_files:
        total_checks += 1
        if check_file_exists(backend_path / file_name, description):
            passed_checks += 1
    
    # Routers
    router_files = [
        ("app/routers/__init__.py", "Módulo routers"),
        ("app/routers/auth.py", "Rotas de autenticação"),
    ]
    
    print("\n🛣️  ROUTERS:")
    for file_name, description in router_files:
        total_checks += 1
        if check_file_exists(backend_path / file_name, description):
            passed_checks += 1
    
    # Services
    service_files = [
        ("app/services/__init__.py", "Módulo services"),
        ("app/services/auth_service.py", "Serviço de autenticação"),
        ("app/services/user_service.py", "Serviço de usuários"),
    ]
    
    print("\n⚙️  SERVICES:")
    for file_name, description in service_files:
        total_checks += 1
        if check_file_exists(backend_path / file_name, description):
            passed_checks += 1
    
    # Testes
    test_files = [
        ("tests/__init__.py", "Módulo tests"),
        ("tests/test_auth.py", "Testes de autenticação"),
    ]
    
    print("\n🧪 TESTES:")
    for file_name, description in test_files:
        total_checks += 1
        if check_file_exists(backend_path / file_name, description):
            passed_checks += 1
    
    # Configuração
    config_files = [
        ("requirements.txt", "Dependências Python"),
        (".env", "Variáveis de ambiente"),
        (".env.example", "Exemplo de variáveis"),
        ("start_server.py", "Script de inicialização"),
        ("pytest.ini", "Configuração de testes"),
        ("README.md", "Documentação")
    ]
    
    print("\n📄 CONFIGURAÇÃO:")
    for file_name, description in config_files:
        total_checks += 1
        if check_file_exists(backend_path / file_name, description):
            passed_checks += 1
    
    # Verificações de conteúdo
    print("\n🔍 VERIFICAÇÕES DE CONTEÚDO:")
    
    # Verificar se main.py tem conteúdo FastAPI
    main_py = backend_path / "app/main.py"
    if main_py.exists():
        with open(main_py, 'r') as f:
            content = f.read()
            if "FastAPI" in content and "app = FastAPI" in content:
                print("✅ app/main.py contém aplicação FastAPI")
                passed_checks += 1
            else:
                print("❌ app/main.py não contém aplicação FastAPI válida")
        total_checks += 1
    
    # Verificar se auth.py tem rotas
    auth_py = backend_path / "app/routers/auth.py"
    if auth_py.exists():
        with open(auth_py, 'r') as f:
            content = f.read()
            if "/register" in content and "/login" in content:
                print("✅ app/routers/auth.py contém rotas de autenticação")
                passed_checks += 1
            else:
                print("❌ app/routers/auth.py não contém rotas válidas")
        total_checks += 1
    
    # Verificar se requirements.txt tem dependências essenciais
    req_txt = backend_path / "requirements.txt"
    if req_txt.exists():
        with open(req_txt, 'r') as f:
            content = f.read()
            if "fastapi" in content and "motor" in content and "pyjwt" in content:
                print("✅ requirements.txt contém dependências essenciais")
                passed_checks += 1
            else:
                print("❌ requirements.txt não contém dependências essenciais")
        total_checks += 1
    
    # Resultado final
    print("\n" + "=" * 50)
    print(f"📊 RESULTADO: {passed_checks}/{total_checks} verificações passaram")
    
    percentage = (passed_checks / total_checks) * 100
    if percentage >= 90:
        print(f"🎉 EXCELENTE! {percentage:.1f}% - FINALIZAÇÃO 1 COMPLETA!")
    elif percentage >= 75:
        print(f"✅ MUITO BOM! {percentage:.1f}% - Quase pronto!")
    elif percentage >= 50:
        print(f"⚠️  PARCIAL: {percentage:.1f}% - Precisa de ajustes")
    else:
        print(f"❌ INCOMPLETO: {percentage:.1f}% - Muito trabalho ainda")
    
    print("\n🎯 PRÓXIMOS PASSOS:")
    print("1. pip install -r requirements.txt")
    print("2. cp .env.example .env (e configure)")
    print("3. python start_server.py")
    print("4. Acesse http://localhost:8000/docs")
    
    return passed_checks, total_checks

if __name__ == "__main__":
    main()