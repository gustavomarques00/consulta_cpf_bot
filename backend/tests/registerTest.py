import sys
import os

# Adiciona a pasta backend ao sys.path para permitir importar o app
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../backend')))  # Ajuste o caminho para a pasta backend

from app import app  # Agora a importação deve funcionar corretamente

import pytest

# Configuração para o teste
@pytest.fixture
def client():
    with app.test_client() as client:
        yield client

# Teste de sucesso para o endpoint /register
def test_register_success(client):
    data = {
        "nome": "João Silva",
        "email": "joao.silva@example.com",
        "telefone": "(11) 98765-4321",
        "tipoUsuario": "Operador",
        "senha": "Senha@123",
        "confirmarSenha": "Senha@123"
    }
    response = client.post('/register', json=data)
    assert response.status_code == 201
    assert response.json == {"message": "Usuário registrado com sucesso!"}

# Teste de falha - Senhas diferentes
def test_register_password_mismatch(client):
    data = {
        "nome": "João Silva",
        "email": "joao.silva@example.com",
        "telefone": "(11) 98765-4321",
        "tipoUsuario": "Operador",
        "senha": "Senha@123",
        "confirmarSenha": "Senha@321"  # Senhas não coincidem
    }

    response = client.post('/register', json=data)
    assert response.status_code == 400  # Espera-se status 400 (Bad Request)
    assert response.json == {"error": "As senhas não coincidem!"}

# Teste de falha - Email inválido
def test_register_invalid_email(client):
    data = {
        "nome": "João Silva",
        "email": "joao.silva",  # Email inválido
        "telefone": "(11) 98765-4321",
        "tipoUsuario": "Operador",
        "senha": "Senha@123",
        "confirmarSenha": "Senha@123"
    }

    response = client.post('/register', json=data)
    assert response.status_code == 400
    assert response.json == {"error": "Email inválido!"}

# Teste de falha - Tipo de usuário inválido
def test_register_invalid_user_type(client):
    data = {
        "nome": "João Silva",
        "email": "joao.silva@example.com",
        "telefone": "(11) 98765-4321",
        "tipoUsuario": "Administrador",  # Tipo inválido
        "senha": "Senha@123",
        "confirmarSenha": "Senha@123"
    }

    response = client.post('/register', json=data)
    assert response.status_code == 400
    assert response.json == {"error": "Tipo de usuário inválido! Os tipos válidos são: Operador, Chefe de Equipe, Independente"}
