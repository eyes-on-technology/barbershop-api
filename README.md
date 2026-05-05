# Barbershop API - Documentação Completa

Uma **API REST profissional** desenvolvida em **Python com FastAPI** para gerenciar agendamentos de barbearia. A API se comunica com **Supabase PostgreSQL** e é otimizada para deploy no **Render**.

---

## 📋 Índice

1. [Visão Geral](#visão-geral)
2. [Arquitetura](#arquitetura)
3. [Instalação Local](#instalação-local)
4. [Configuração](#configuração)
5. [Executar Localmente](#executar-localmente)
6. [Endpoints da API](#endpoints-da-api)
7. [Autenticação JWT](#autenticação-jwt)
8. [Lógica de Negócio](#lógica-de-negócio)
9. [Deploy no Render](#deploy-no-render)
10. [Troubleshooting](#troubleshooting)

---

## 🎯 Visão Geral

A **Barbershop API** fornece endpoints completos para:

- **Autenticação**: Login e cadastro de clientes e prestadores
- **Serviços**: CRUD de serviços (apenas admin)
- **Disponibilidades**: Gerenciar horários disponíveis
- **Agendamentos**: Criar, listar, atualizar agendamentos
- **Solicitações**: Prestadores aprovam/rejeitam solicitações
- **Usuários**: Gerenciar perfis e dados
- **Admin**: Estatísticas e gerenciamento do sistema

### Tecnologias

| Tecnologia | Versão | Uso |
|-----------|--------|-----|
| Python | 3.11+ | Linguagem |
| FastAPI | 0.104+ | Framework web |
| Uvicorn | 0.24+ | ASGI server |
| Supabase | - | Banco de dados PostgreSQL |
| JWT | - | Autenticação |
| Pydantic | 2.5+ | Validação de dados |

---

## 🏗️ Arquitetura

### Estrutura de Pastas

```
barbershop-api/
├── app/
│   ├── __init__.py
│   ├── main.py                 # Aplicação FastAPI
│   ├── config.py               # Configurações
│   ├── database.py             # Conexão Supabase
│   ├── auth.py                 # Autenticação JWT
│   ├── schemas.py              # Modelos Pydantic
│   ├── dependencies.py         # Dependências
│   ├── routers/
│   │   ├── auth.py             # Endpoints /auth
│   │   ├── servicos.py         # Endpoints /servicos
│   │   ├── disponibilidades.py # Endpoints /disponibilidades
│   │   ├── agendamentos.py     # Endpoints /agendamentos
│   │   ├── usuarios.py         # Endpoints /usuarios
│   │   └── admin.py            # Endpoints /admin
│   └── utils/
│       ├── exceptions.py       # Exceções customizadas
│       └── validators.py       # Validadores
├── main.py                     # Entry point
├── requirements.txt            # Dependências Python
├── .env.example                # Exemplo de variáveis
├── Procfile                    # Deploy Render
├── runtime.txt                 # Versão Python
├── .gitignore
└── README.md
```

### Fluxo de Requisição

```
Cliente (Expo App)
    ↓
HTTP Request com Bearer Token
    ↓
FastAPI Router
    ↓
Autenticação JWT (decode token)
    ↓
Validação com Pydantic
    ↓
Lógica de Negócio
    ↓
Query Supabase
    ↓
Resposta JSON
    ↓
Cliente (Expo App)
```

---

## 💻 Instalação Local

### Pré-requisitos

- Python 3.11+
- pip ou poetry
- Git
- Conta no Supabase

### Passos

```bash
# 1. Clonar repositório
git clone <seu-repositorio>
cd barbershop-api

# 2. Criar ambiente virtual
python -m venv venv

# 3. Ativar ambiente virtual
# Linux/Mac:
source venv/bin/activate
# Windows:
venv\Scripts\activate

# 4. Instalar dependências
pip install -r requirements.txt

# 5. Criar arquivo .env
cp .env.example .env
```

---

## ⚙️ Configuração

### Variáveis de Ambiente (.env)

```env
# Supabase
SUPABASE_URL=https://seu-projeto.supabase.co
SUPABASE_KEY=sua-chave-anonima
SUPABASE_SERVICE_ROLE_KEY=sua-service-role-key

# JWT
JWT_SECRET_KEY=sua-chave-secreta-muito-segura-min-32-caracteres
JWT_ALGORITHM=HS256
JWT_EXPIRATION_MINUTES=15

# Ambiente
ENVIRONMENT=development
DEBUG=true

# CORS
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8081,https://barbershop-api-evjg.onrender.com
```

### Obter Credenciais Supabase

1. Acesse [supabase.com](https://supabase.com)
2. Vá para **Settings → API**
3. Copie:
   - `Project URL` → `SUPABASE_URL`
   - `anon public` → `SUPABASE_KEY`
   - `service_role secret` → `SUPABASE_SERVICE_ROLE_KEY`

### Gerar JWT_SECRET_KEY

```bash
# Terminal
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

---

## 🚀 Executar Localmente

### Modo Desenvolvimento

```bash
# Terminal 1: Ativar ambiente
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows

# Terminal 1: Iniciar servidor
python main.py
```

A API estará disponível em `http://localhost:3000`

### Acessar Documentação

- **Swagger UI**: http://localhost:3000/docs
- **ReDoc**: http://localhost:3000/redoc

### Testar Endpoint

```bash
# Health check
curl http://localhost:3000/health

# Listar serviços
curl http://localhost:3000/servicos
```

---

## 📡 Endpoints da API

### Autenticação

#### Login
```http
POST /auth/login
Content-Type: application/json

{
  "email": "cliente@example.com",
  "password": "senha123"
}
```

**Resposta (200)**:
```json
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {
    "id": "uuid",
    "nome": "João Silva",
    "email": "cliente@example.com",
    "telefone": "11999999999"
  },
  "user_type": "cliente",
  "expires_in": 900
}
```

#### Cadastro Cliente
```http
POST /auth/signup/cliente
Content-Type: application/json

{
  "nome": "João Silva",
  "email": "joao@example.com",
  "telefone": "11999999999",
  "password": "senha123"
}
```

#### Cadastro Prestador
```http
POST /auth/signup/prestador
Content-Type: application/json

{
  "nome": "Maria Barbeira",
  "email": "maria@example.com",
  "telefone": "11988888888",
  "especialidade": "Corte de cabelo",
  "bio": "Especialista em cortes modernos",
  "password": "senha123"
}
```

### Serviços

#### Listar Serviços
```http
GET /servicos?page=1&limit=10&categoria=Corte
Authorization: Bearer {token}
```

**Resposta (200)**:
```json
{
  "data": [
    {
      "id": "uuid",
      "nome": "Corte Simples",
      "descricao": "Corte básico",
      "preco_base": 30.00,
      "categoria": "Corte"
    }
  ],
  "total": 1,
  "page": 1,
  "limit": 10,
  "pages": 1
}
```

#### Criar Serviço (Admin)
```http
POST /servicos
Authorization: Bearer {admin_token}
Content-Type: application/json

{
  "nome": "Corte Premium",
  "descricao": "Corte com design",
  "preco_base": 50.00,
  "categoria": "Corte"
}
```

#### Atualizar Serviço (Admin)
```http
PUT /servicos/{servico_id}
Authorization: Bearer {admin_token}
Content-Type: application/json

{
  "preco_base": 55.00
}
```

#### Deletar Serviço (Admin)
```http
DELETE /servicos/{servico_id}
Authorization: Bearer {admin_token}
```

### Agendamentos

#### Criar Agendamento
```http
POST /agendamentos
Authorization: Bearer {cliente_token}
Content-Type: application/json

{
  "prestador_id": "uuid",
  "servico_id": "uuid",
  "data_hora": "2024-01-20T14:30:00"
}
```

**Resposta (200)**:
```json
{
  "id": "uuid",
  "cliente_id": "uuid",
  "prestador_id": "uuid",
  "servico_id": "uuid",
  "data_hora": "2024-01-20T14:30:00",
  "status": "pendente",
  "cliente": {...},
  "prestador": {...},
  "servico": {...}
}
```

#### Listar Agendamentos Cliente
```http
GET /agendamentos/cliente?page=1&limit=10&status=pendente
Authorization: Bearer {cliente_token}
```

#### Listar Agendamentos Prestador
```http
GET /agendamentos/prestador?page=1&limit=10&status=pendente
Authorization: Bearer {prestador_token}
```

#### Obter Agendamento
```http
GET /agendamentos/{agendamento_id}
Authorization: Bearer {token}
```

#### Cancelar Agendamento (Cliente)
```http
PUT /agendamentos/{agendamento_id}/cancelar
Authorization: Bearer {cliente_token}
```

#### Aprovar Solicitação (Prestador)
```http
PUT /agendamentos/solicitacoes/{agendamento_id}/aprovar
Authorization: Bearer {prestador_token}
```

#### Rejeitar Solicitação (Prestador)
```http
PUT /agendamentos/solicitacoes/{agendamento_id}/rejeitar
Authorization: Bearer {prestador_token}
Content-Type: application/json

{
  "motivo": "Indisponível neste horário"
}
```

#### Listar Solicitações Pendentes (Prestador)
```http
GET /agendamentos/solicitacoes/pendentes?page=1&limit=10
Authorization: Bearer {prestador_token}
```

### Usuários

#### Obter Perfil Cliente
```http
GET /usuarios/perfil/cliente
Authorization: Bearer {cliente_token}
```

#### Obter Perfil Prestador
```http
GET /usuarios/perfil/prestador
Authorization: Bearer {prestador_token}
```

#### Atualizar Perfil Cliente
```http
PUT /usuarios/perfil/cliente
Authorization: Bearer {cliente_token}
Content-Type: application/json

{
  "nome": "Novo Nome",
  "telefone": "11999999999"
}
```

#### Atualizar Perfil Prestador
```http
PUT /usuarios/perfil/prestador
Authorization: Bearer {prestador_token}
Content-Type: application/json

{
  "nome": "Novo Nome",
  "especialidade": "Barba",
  "bio": "Especialista em barba"
}
```

#### Listar Prestadores
```http
GET /usuarios/prestadores?page=1&limit=10
```

#### Obter Prestador
```http
GET /usuarios/prestadores/{prestador_id}
```

### Admin

#### Obter Estatísticas
```http
GET /admin/estatisticas
Authorization: Bearer {admin_token}
```

**Resposta (200)**:
```json
{
  "total_clientes": 50,
  "total_prestadores": 10,
  "total_servicos": 25,
  "total_agendamentos": 200,
  "agendamentos_confirmados": 150,
  "agendamentos_pendentes": 30
}
```

#### Listar Agendamentos (Admin)
```http
GET /admin/agendamentos?page=1&limit=10&status=confirmado
Authorization: Bearer {admin_token}
```

#### Deletar Agendamento (Admin)
```http
DELETE /admin/agendamentos/{agendamento_id}
Authorization: Bearer {admin_token}
```

---

## 🔐 Autenticação JWT

### Fluxo

1. **Login/Signup**: Usuário envia credenciais
2. **Token Gerado**: API retorna JWT válido por 15 minutos
3. **Armazenamento**: App armazena token em SecureStore
4. **Requisições**: Cada requisição inclui `Authorization: Bearer {token}`
5. **Validação**: API decodifica e valida token
6. **Expiração**: Se expirado, retorna 401 e usuário faz login novamente

### Estrutura do Token

```json
{
  "sub": "uuid-do-usuario",
  "type": "cliente|prestador",
  "email": "usuario@example.com",
  "exp": 1234567890,
  "iat": 1234567800
}
```

### Implementação

```python
# Criar token
token = create_access_token(
    data={
        "sub": str(user_id),
        "type": user_type,
        "email": user_email,
    }
)

# Validar token
payload = decode_token(token)
user_id = payload.get("sub")
```

---

## 💼 Lógica de Negócio

### Máximo de Solicitações por Horário

**Regra**: Um prestador pode receber no máximo **3 solicitações** para cada horário.

**Implementação** (app/routers/agendamentos.py):

```python
MAX_SOLICITACOES_POR_HORARIO = 3

# Ao criar agendamento
count = db.count_agendamentos_por_horario(
    data_hora=agendamento.data_hora,
    prestador_id=agendamento.prestador_id,
)

if count >= MAX_SOLICITACOES_POR_HORARIO:
    raise MaxSolicitacoesException()
```

### Fluxo de Agendamento

```
1. Cliente cria agendamento
   ↓
2. Status = "pendente"
   ↓
3. Prestador recebe solicitação
   ↓
4. Prestador aprova → Status = "confirmado"
   OU
   Prestador rejeita → Status = "cancelado"
   ↓
5. Cliente vê resultado
```

### Validações

- ✅ Data/hora deve ser no futuro
- ✅ Prestador deve existir
- ✅ Serviço deve existir
- ✅ Máximo 3 solicitações por horário
- ✅ Apenas cliente pode cancelar
- ✅ Apenas prestador pode aprovar/rejeitar
- ✅ Apenas agendamentos pendentes podem ser cancelados

---

## 🚀 Deploy no Render

### Pré-requisitos

- Conta no [Render](https://render.com)
- Repositório Git (GitHub, GitLab, etc)
- Variáveis de ambiente configuradas

### Passos

1. **Conectar Repositório**
   - Acesse [dashboard.render.com](https://dashboard.render.com)
   - Clique em "New +" → "Web Service"
   - Conecte seu repositório GitHub

2. **Configurar Serviço**
   - **Name**: `barbershop-api`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

3. **Adicionar Variáveis de Ambiente**
   - Vá para **Environment**
   - Adicione todas as variáveis de `.env.example`

4. **Deploy**
   - Clique em "Deploy"
   - Aguarde conclusão (2-3 minutos)
   - Acesse sua API em `https://barbershop-api-evjg.onrender.com`

### Verificar Deploy

```bash
# Health check
curl https://barbershop-api-evjg.onrender.com/health

# Documentação
https://barbershop-api-evjg.onrender.com/docs
```

### Monitorar Logs

```bash
# No dashboard Render
Settings → Logs
```

---

## 🔧 Troubleshooting

### Erro: "Conexão com Supabase recusada"

**Solução**:
1. Verificar `SUPABASE_URL` e `SUPABASE_KEY`
2. Verificar se Supabase está online
3. Verificar firewall/VPN

```bash
# Testar conexão
curl https://seu-projeto.supabase.co/rest/v1/servicos \
  -H "Authorization: Bearer sua-chave"
```

### Erro: "Token inválido"

**Solução**:
1. Verificar se `JWT_SECRET_KEY` é consistente
2. Verificar se token não expirou
3. Verificar se header está correto: `Authorization: Bearer {token}`

### Erro: "Máximo de solicitações atingido"

**Solução**: Prestador já tem 3 solicitações para este horário. Cliente deve escolher outro horário ou prestador.

### Erro 500 na API

**Solução**:
1. Verificar logs: `Settings → Logs` no Render
2. Verificar variáveis de ambiente
3. Verificar conexão com Supabase

```bash
# Testar localmente
python main.py
# Verificar erro no terminal
```

### Slow Response Time

**Otimizações**:

1. **Adicionar índices no Supabase**:
```sql
CREATE INDEX idx_agendamentos_cliente_status 
  ON agendamentos(cliente_id, status);
```

2. **Implementar cache**:
```python
from functools import lru_cache

@lru_cache(maxsize=100)
def get_servico_cached(servico_id: str):
    return db.get_servico_by_id(servico_id)
```

3. **Usar connection pooling**:
```python
# Já implementado no Supabase client
```

---

## 📚 Referências

- [FastAPI Docs](https://fastapi.tiangolo.com)
- [Supabase Docs](https://supabase.com/docs)
- [JWT.io](https://jwt.io)
- [Render Docs](https://render.com/docs)
- [Pydantic Docs](https://docs.pydantic.dev)

---

## 📝 Notas Importantes

### Segurança

- ✅ Senhas devem ser hasheadas no Supabase Auth
- ✅ JWT_SECRET_KEY deve ser muito seguro (min 32 caracteres)
- ✅ HTTPS obrigatório em produção
- ✅ CORS configurado apenas para domínios permitidos
- ✅ Rate limiting recomendado para endpoints de autenticação

### Performance

- ✅ Paginação implementada em todas as listagens
- ✅ Índices no banco de dados para queries frequentes
- ✅ Validação rápida com Pydantic
- ✅ Logging estruturado para debugging

### Manutenção

- ✅ Código modularizado em routers
- ✅ Exceções customizadas para melhor tratamento
- ✅ Schemas Pydantic para validação automática
- ✅ Documentação automática com Swagger

---

## 🎉 Conclusão

A **Barbershop API** está pronta para produção! Com arquitetura profissional, autenticação JWT segura, lógica de negócio implementada e deploy automatizado no Render.

**Próximos passos**:
1. Configurar variáveis de ambiente
2. Fazer deploy no Render
3. Testar endpoints com Swagger UI
4. Integrar com app Expo
5. Monitorar logs e performance

Boa sorte! 🚀