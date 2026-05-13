# ProjetoTunning — Frontend

Frontend simples em HTML/CSS/JS para o sistema de gerenciamento de loja de eletrônicos.

## Estrutura
```
ProjetoTunning-Frontend/
├── index.html              # Dashboard principal
├── css/
│   └── style.css           # Estilos globais
├── js/
│   └── api.js              # Comunicação com a API (fetch + CRUD)
└── pages/
    ├── usuarios.html       # CRUD de Usuários
    ├── produtos.html       # CRUD de Produtos
    └── categorias.html     # CRUD de Categorias
```

## Como rodar

### Backend (FastAPI)
```bash
cd ProjetoTunning-main
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

### Frontend
Abra o `index.html` diretamente no navegador, **ou** rode um servidor local simples:

```bash
cd ProjetoTunning-Frontend
python -m http.server 5500
# Acesse: http://localhost:5500
```

> ⚠️ Use um servidor local (não abrir o arquivo direto) para evitar problemas de CORS com a API.

## Configuração da API
No arquivo `js/api.js`, altere a variável `API_BASE` caso sua API rode em outra porta:

```js
const API_BASE = 'http://localhost:8000/api/v1';
```

## Rotas esperadas no backend
| Método | Rota                  | Descrição               |
|--------|-----------------------|-------------------------|
| GET    | /api/v1/usuarios      | Listar usuários         |
| POST   | /api/v1/usuarios      | Criar usuário           |
| PUT    | /api/v1/usuarios/{id} | Atualizar usuário       |
| DELETE | /api/v1/usuarios/{id} | Excluir usuário         |
| GET    | /api/v1/produtos      | Listar produtos         |
| POST   | /api/v1/produtos      | Criar produto           |
| PUT    | /api/v1/produtos/{id} | Atualizar produto       |
| DELETE | /api/v1/produtos/{id} | Excluir produto         |
| GET    | /api/v1/categorias    | Listar categorias       |
| POST   | /api/v1/categorias    | Criar categoria         |
| PUT    | /api/v1/categorias/{id}| Atualizar categoria    |
| DELETE | /api/v1/categorias/{id}| Excluir categoria      |

## CORS no FastAPI
Adicione ao `app/main.py`:
```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)
```
