#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import json
import time

# Configuração
BACKEND_URL = "http://localhost:8030/api"
ADMIN_TOKEN = "admin-token"  # Token mock do admin

# Lista de 5 bots para criar
BOTS_DATA = [
    {
        "username": "CodeMaster_AI",
        "email": "codemaster@bots.com",
        "bio": "Especialista em múltiplas linguagens de programação. Focado em otimização de código e melhores práticas.",
        "pc_points": 1500,
        "pcon_points": 750,
        "rank": "Especialista",
        "location": "São Paulo, Brasil",
        "skills": ["Python", "JavaScript", "Java", "C++", "Docker"]
    },
    {
        "username": "WebDev_Expert",
        "email": "webdev@bots.com", 
        "bio": "Desenvolvimento web full-stack. React, Node.js, e tecnologias modernas.",
        "pc_points": 1200,
        "pcon_points": 600,
        "rank": "Avançado",
        "location": "Rio de Janeiro, Brasil",
        "skills": ["React", "Node.js", "TypeScript", "MongoDB", "AWS"]
    },
    {
        "username": "DataScience_Bot",
        "email": "datascience@bots.com",
        "bio": "Análise de dados e machine learning. Python e R para insights poderosos.",
        "pc_points": 1800,
        "pcon_points": 900,
        "rank": "Mestre",
        "location": "Belo Horizonte, Brasil", 
        "skills": ["Python", "R", "TensorFlow", "Pandas", "SQL"]
    },
    {
        "username": "Mobile_Developer",
        "email": "mobile@bots.com",
        "bio": "Desenvolvimento mobile nativo e cross-platform. Android, iOS e Flutter.",
        "pc_points": 1000,
        "pcon_points": 500,
        "rank": "Intermediário",
        "location": "Brasília, Brasil",
        "skills": ["Flutter", "React Native", "Android", "iOS", "Dart"]
    },
    {
        "username": "DevOps_Guru",
        "email": "devops@bots.com",
        "bio": "Infraestrutura e automação. Docker, Kubernetes, CI/CD e cloud computing.",
        "pc_points": 2000,
        "pcon_points": 1000,
        "rank": "Guru",
        "location": "Porto Alegre, Brasil",
        "skills": ["Docker", "Kubernetes", "AWS", "Azure", "Jenkins"]
    }
]

def create_bot(bot_data, bot_number):
    """Cria um bot via API"""
    
    print(f"\n🤖 Criando Bot #{bot_number}: {bot_data['username']}")
    print(f"📧 Email: {bot_data['email']}")
    print(f"🏆 Rank: {bot_data['rank']} | PC: {bot_data['pc_points']} | PCon: {bot_data['pcon_points']}")
    
    headers = {
        'Authorization': f'Bearer {ADMIN_TOKEN}',
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }
    
    try:
        response = requests.post(
            f"{BACKEND_URL}/admin/bots/",
            headers=headers,
            json=bot_data,
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Sucesso! Bot ID: {result.get('bot_id', 'N/A')}")
            print(f"✅ Mensagem: {result.get('message', 'Bot criado')}")
            return True
        else:
            print(f"❌ Erro {response.status_code}: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print(f"❌ Erro de conexão! Verifique se o backend está rodando em {BACKEND_URL}")
        return False
    except requests.exceptions.Timeout:
        print(f"❌ Timeout! Requisição demorou mais que 10 segundos")
        return False
    except Exception as e:
        print(f"❌ Erro inesperado: {str(e)}")
        return False

def main():
    print("🚀 CRIANDO 5 BOTS AUTOMATICAMENTE")
    print("=" * 50)
    
    # Verificar se o backend está rodando
    try:
        health_response = requests.get(f"{BACKEND_URL}/", timeout=5)
        if health_response.status_code == 200:
            print(f"✅ Backend está online em {BACKEND_URL}")
        else:
            print(f"⚠️ Backend respondeu com status {health_response.status_code}")
    except:
        print(f"❌ Não foi possível conectar ao backend em {BACKEND_URL}")
        print("❌ Certifique-se de que o backend está rodando!")
        return
    
    # Criar os 5 bots
    successful_bots = 0
    failed_bots = 0
    
    for i, bot_data in enumerate(BOTS_DATA, 1):
        if create_bot(bot_data, i):
            successful_bots += 1
        else:
            failed_bots += 1
        
        # Pequena pausa entre requisições
        if i < len(BOTS_DATA):
            print("⏳ Aguardando 2 segundos...")
            time.sleep(2)
    
    # Resultado final
    print("\n" + "=" * 50)
    print("📊 RESULTADO FINAL:")
    print(f"✅ Bots criados com sucesso: {successful_bots}")
    print(f"❌ Bots que falharam: {failed_bots}")
    print(f"📈 Total tentativas: {len(BOTS_DATA)}")
    
    if successful_bots == len(BOTS_DATA):
        print("\n🎉 TODOS OS 5 BOTS FORAM CRIADOS COM SUCESSO!")
    elif successful_bots > 0:
        print(f"\n⚠️ {successful_bots} bots criados, {failed_bots} falharam")
    else:
        print("\n💥 NENHUM BOT FOI CRIADO - VERIFIQUE O BACKEND!")

if __name__ == "__main__":
    main()