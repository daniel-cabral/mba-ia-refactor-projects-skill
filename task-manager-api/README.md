# task-manager-api

API de Task Manager em Python/Flask usada como entrada do desafio `refactor-arch`. Estrutura em camadas MVC: `config/`, `models/`, `controllers/`, `routes/` (views), `middlewares/`, `services/` e `utils/`.

## Como rodar

```bash
pip install -r requirements.txt
python seed.py
python app.py
```

A aplicação sobe em `http://127.0.0.1:5000`. O `seed.py` popula o banco SQLite (`tasks.db`) com usuários, categorias e tasks de exemplo — **rode-o antes do primeiro boot**, caso contrário os endpoints vão retornar listas vazias.

## Configuração

Variáveis de ambiente (veja `.env.example`; um arquivo `.env` é carregado automaticamente): `SECRET_KEY`, `DATABASE_URL`, `FLASK_DEBUG`, `HOST`, `PORT`, `CORS_ORIGINS`, `ADMIN_ENABLED`, `SMTP_*`.

`ADMIN_ENABLED=1` habilita a exclusão de usuários (`DELETE /users/<id>`) e a aceitação de `role`/`active` nas requisições de usuário. Sem isso, a rota responde 403 e esses campos são ignorados.
