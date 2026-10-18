# ecommerce-api-legacy

LMS API (com fluxo de checkout) em Node.js/Express usada como entrada do desafio `refactor-arch`.

## Como rodar

```bash
npm install
npm start
```

A aplicação sobe em `http://localhost:3000`. O banco SQLite é em memória e já carrega seeds automaticamente no boot.

Exemplos de requisições estão em `api.http`.

## Configuração

Copie `.env.example` e exporte as variáveis desejadas. As rotas `GET /api/admin/financial-report` e `DELETE /api/users/:id` respondem 403 a menos que `ADMIN_TOKEN` esteja definido e seja enviado no header `x-admin-token`.
