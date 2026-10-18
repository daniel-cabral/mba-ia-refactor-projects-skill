# code-smells-project

API de E-commerce em Python/Flask usada como entrada do desafio `refactor-arch`.

## Como rodar

```bash
pip install -r requirements.txt
python app.py
```

A aplicação sobe em `http://localhost:5000`. O banco SQLite (`loja.db`) é criado automaticamente no primeiro boot, já com produtos e usuários de exemplo.

## Estrutura

```text
app.py              # composition root: create_app(), registra blueprints e handlers
config/             # settings.py (variáveis de ambiente) e constants.py (regras de negócio)
database.py         # conexão por request, schema e seed
models/             # acesso a dados por entidade
controllers/        # fluxo da aplicação, validações e regras de negócio
views/              # blueprints HTTP, um por recurso
middlewares/        # error handler, guard admin, security headers
errors.py           # exceções de domínio
```

Configuração via variáveis de ambiente (veja `.env.example`). As rotas `/admin/*` retornam 403 a menos que `ADMIN_ENABLED=1`.
