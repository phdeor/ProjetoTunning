# 🛒 ProjetoTunning — Sistema de Gerenciamento de Mercado

> Projeto acadêmico desenvolvido para a disciplina de PERFORMANCE E TUNNING DE DADOS — Centro Universitário FEI, 2026.

---

## 👥 Integrantes

| Nome | RA |
|---|---|
| Pedro Henrique Lima de Oliveira | 22124019-5 |
| Gustavo Souza Alvarenga | 22124058-3 |
| Matheus Sarmento Pinto | 22124062-5 |

---

## 1. Tema Escolhido

O projeto consiste em um **sistema de gerenciamento de mercado**, simulando o backend de um supermercado com controle completo de produtos, estoque, clientes e vendas.

O sistema permite:

- Cadastro e consulta de **produtos** com informações detalhadas (nome, categoria, marca, preço, validade)
- Gerenciamento de **estoque** (entrada, saída e controle de quantidade disponível por produto)
- Registro de **vendas** e **clientes**
- Armazenamento de **imagens dos produtos**
- **Fila de processamento** de vendas para garantir ordem e consistência nas operações

O tema foi escolhido por ser um cenário do cotidiano que justifica naturalmente o uso de múltiplos bancos de dados com responsabilidades distintas, além de apresentar alto volume de leituras e escritas — ideal para explorar técnicas de performance e tuning de dados.

---

## 2. Justificativa dos Bancos de Dados e Implementação do Backend

### 🐘 PostgreSQL — Banco Principal

**Por que PostgreSQL?**

O PostgreSQL foi escolhido como banco principal por ser um banco relacional robusto com suporte completo a **transações ACID**, ideal para garantir consistência nos dados do mercado. Toda a estrutura central da aplicação reside aqui: produtos, clientes, vendas e itens de venda possuem relacionamentos bem definidos e precisam de integridade referencial. Operações como registrar uma venda devem ser atômicas — ou todos os dados são gravados corretamente, ou nada é alterado.

**O que é armazenado:**
- Tabela `clientes`: dados cadastrais (nome, email, CPF, endereço)
- Tabela `produtos`: informações do produto (nome, categoria, marca, preço, validade, estoque)
- Tabela `vendas`: histórico de compras por cliente (data, status, valor total)
- Tabela `itens_venda`: produtos comprados por venda (quantidade, preço unitário)

**Como é usado no backend:**

O acesso ao PostgreSQL é feito de forma **assíncrona** com SQLAlchemy 2.0 + asyncpg, garantindo que a API não bloqueie o event loop enquanto aguarda respostas do banco. As queries são mapeadas via ORM e executadas em contexto de sessão assíncrona.

---

### 🍃 MongoDB — Armazenamento de Imagens dos Produtos

**Por que MongoDB?**

O MongoDB foi escolhido para armazenar as **imagens dos produtos**. Dados binários como imagens não se encaixam bem em bancos relacionais — armazená-las no PostgreSQL aumentaria desnecessariamente o tamanho das tabelas e prejudicaria a performance das queries. O MongoDB, com seu modelo de documentos flexível, permite armazenar as imagens de forma eficiente associadas ao ID do produto, mantendo o banco relacional leve e focado nos dados estruturados.

**O que é armazenado:**
- Coleção `imagens_produtos`: documentos contendo o ID do produto (referência ao PostgreSQL), nome do arquivo, tipo MIME e o binário da imagem em Base64

**Como é usado no backend:**

O acesso ao MongoDB é feito via **Motor** (driver assíncrono oficial para MongoDB em Python), integrado ao FastAPI. Quando um produto é consultado, o backend busca seus dados no PostgreSQL e, separadamente, recupera sua imagem no MongoDB pelo ID do produto. As imagens são servidas diretamente pela API como resposta binária ou Base64.

---

### ⚡ Redis — Fila de Processamento de Vendas

**Por que Redis?**

O Redis foi escolhido para gerenciar a **fila de processamento de vendas**. Em um mercado com múltiplos caixas operando simultaneamente, vendas podem chegar ao sistema de forma concorrente. Processar todas diretamente no PostgreSQL ao mesmo tempo geraria concorrência nas tabelas e risco de inconsistências. O Redis, com suas estruturas de dados nativas para filas (listas com `LPUSH`/`RPOP`), permite enfileirar as vendas à medida que chegam e processá-las de forma ordenada e controlada, uma a uma.

**O que é armazenado:**
- Fila `fila_vendas`: lista de vendas pendentes aguardando processamento (payload JSON com itens, cliente e valor)

**Como é usado no backend:**

Quando uma venda é iniciada, seu payload é inserido na fila do Redis. Um worker consome a fila em ordem e persiste cada venda no PostgreSQL, garantindo que o processamento seja sequencial e sem conflitos mesmo sob alta demanda.

---

### 🔧 Implementação do Backend

O backend é construído com **FastAPI**, um framework Python moderno e assíncrono. A arquitetura segue a separação de responsabilidades:

```
ProjetoTunning/
├── app/                        # Código principal da API
│   ├── main.py                 # Instância FastAPI e inclusão de rotas
│   ├── routes/                 # Endpoints organizados por entidade
│   │   ├── produtos.py         # GET /produtos, POST /produtos, etc.
│   │   ├── vendas.py           # GET /vendas, POST /vendas, etc.
│   │   └── clientes.py         # GET /clientes, POST /clientes, etc.
│   ├── models/                 # Schemas Pydantic (validação de dados)
│   └── db/                     # Configuração das conexões
├── front/                      # Interface web (HTML/CSS/JS)
├── conecta.py                  # Funções de conexão com os bancos
├── requirements.txt            # Dependências Python
└── .envexample                 # Modelo de variáveis de ambiente
```

Cada requisição HTTP passa pelo FastAPI → rota correspondente → banco correto:
- **PostgreSQL** para dados estruturais (produtos, clientes, vendas)
- **MongoDB** para imagens dos produtos
- **Redis** para enfileiramento de vendas

---

## 3. Como Executar o Projeto

### ✅ Pré-requisitos — Instale antes de tudo

| Recurso | Versão mínima | Download |
|---|---|---|
| Python | 3.11 | https://www.python.org/downloads/ |
| PostgreSQL | 14+ | https://www.postgresql.org/download/ |
| Git | qualquer | https://git-scm.com/ |

> **MongoDB e Redis**: o projeto usa instâncias em nuvem (**MongoDB Atlas** e **Redis Cloud**), então **não é necessário instalar esses dois localmente**. As credenciais de acesso já estão no `.envexample`.

---

### Passo a Passo

#### 1. Clone o repositório

```bash
git clone https://github.com/phdeor/ProjetoTunning.git
cd ProjetoTunning
```

#### 2. Crie e ative o ambiente virtual

```bash
python -m venv venv
```

```bash
# Windows
venv\Scripts\activate

# Linux / macOS
source venv/bin/activate
```

#### 3. Instale as dependências

```bash
pip install -r requirements.txt
```

#### 4. Configure as variáveis de ambiente

Copie o arquivo de exemplo:

```bash
# Windows
copy .envexample .env

# Linux / macOS
cp .envexample .env
```

Abra o `.env` e preencha as variáveis do PostgreSQL com os dados da sua instalação local:

```env
PROJECT_NAME="ProjetoTunning"

# PostgreSQL — ajuste usuário, senha e porta conforme sua instalação local
DATABASE_URL="postgresql+asyncpg://postgres:sua_senha@localhost:5432/mercado_db"

# MongoDB Atlas — já configurado, não precisa alterar
MONGODB_URL="mongodb+srv://admin_fei:grupofoda123@cluster0.ytfqci2.mongodb.net/?appName=Cluster0"
MONGODB_DATABASE_NAME="supermercado_db"

# Redis Cloud — já configurado, não precisa alterar
REDIS_HOST="redis-13656.crce196.sa-east-1-2.ec2.cloud.redislabs.com"
REDIS_PORT=13656
REDIS_PASSWORD="V2ND0fxW3ulJfhkZV2ByAsYnr5ZM9s0g"
```

#### 5. Crie o banco de dados no PostgreSQL

Abra o psql ou pgAdmin e execute:

```sql
CREATE DATABASE mercado_db;
```

#### 6. Inicie o servidor

```bash
uvicorn app.main:app --reload
```

O servidor estará disponível em:

| URL | Descrição |
|---|---|
| http://localhost:8000 | API principal |
| http://localhost:8000/docs | Documentação interativa (Swagger UI) |
| http://localhost:8000/redoc | Documentação alternativa (ReDoc) |

#### 7. (Opcional) Testar as conexões com os bancos

```bash
python teste.py
```

Saída esperada no terminal:
```
Conectado ao Postgre!
Conectado ao MongoDB! Coleções disponíveis: [...]
Deu certo a conexão com o Redis Cloud!
```

---

### Serviços utilizados

| Serviço | Onde roda | O que precisa fazer |
|---|---|---|
| **FastAPI** | Local | Iniciar com `uvicorn` (passo 6) |
| **PostgreSQL** | Local | Instalar + criar o banco (passos 4 e 5) |
| **MongoDB** | Nuvem (Atlas) | Nada — credenciais já estão no `.env` |
| **Redis** | Nuvem (Redis Cloud) | Nada — credenciais já estão no `.env` |
| **Frontend** | Local | Abrir `front/index.html` no navegador |

---

## 4. Dependências

Todas as dependências estão em `requirements.txt` e são instaladas de uma vez no passo 3. As principais:

| Pacote | Versão | Função |
|---|---|---|
| fastapi | 0.136.1 | Framework web da API |
| uvicorn | 0.46.0 | Servidor ASGI para rodar o FastAPI |
| sqlalchemy | 2.0.49 | ORM para PostgreSQL |
| asyncpg | 0.31.0 | Driver assíncrono do PostgreSQL |
| psycopg2 | 2.9.12 | Driver síncrono do PostgreSQL |
| motor | 3.7.1 | Driver assíncrono do MongoDB |
| pymongo | 4.17.0 | Driver do MongoDB |
| redis | 7.4.0 | Cliente Redis |
| pydantic | 2.13.3 | Validação de dados e schemas |
| python-dotenv | 1.2.2 | Leitura do arquivo `.env` |

---

## Tecnologias

![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=flat&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.136-009688?style=flat&logo=fastapi&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-14+-336791?style=flat&logo=postgresql&logoColor=white)
![MongoDB](https://img.shields.io/badge/MongoDB-Atlas-47A248?style=flat&logo=mongodb&logoColor=white)
![Redis](https://img.shields.io/badge/Redis-Cloud-DC382D?style=flat&logo=redis&logoColor=white)
