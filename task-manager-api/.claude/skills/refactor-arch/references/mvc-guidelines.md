# MVC guidelines

Used in Phase 3. Defines the target architecture. For an API, the "View" is the HTTP layer: routes that parse requests and serialize responses.

## Layers and responsibilities

| Layer | Does | Never does |
| --- | --- | --- |
| Config | Reads env vars, defaults, feature flags (`ADMIN_ENABLED`, `DEBUG`, CORS origins, DB path). | Hardcoded secrets; business logic. |
| Model | Data access (SQL/ORM) for one entity or aggregate; entity rules that depend only on the entity's own data (e.g. "is overdue"). | Import HTTP objects (`request`, `req`, `res`, `jsonify`); know about other domains' tables beyond joins it owns. |
| Controller | Application flow for a use case: validate input, enforce business rules, orchestrate models and side effects, raise domain errors. | Build HTTP responses; write SQL; read env vars directly (receives config). |
| View / Routes | Map HTTP to controllers: parse path/query/body, call one controller function, return status + JSON. | Business rules; SQL; try/except around everything. |
| Middlewares | Cross-cutting HTTP concerns: error handler, guards (`admin_only`), CORS, request limits. | Business rules. |
| Composition root | Entry point: create app, load config, open DB/resources, wire dependencies, register routes and middlewares, start server. | Route handlers; SQL. |

Services (`services/`) are allowed as controller helpers for side effects (email, payment gateway) and are called only by controllers.

## Dependency direction

```text
routes (view) ──> controllers ──> models ──> db connection
      │                 │
      └─> middlewares   └─> services (side effects)
config is read by the composition root and injected downward
```

- Arrows point one way. Models never import controllers or routes. Controllers never import routes.
- Shared resources (DB connection, config, external clients) are created in the composition root or per request through the framework context, then passed in. No module-level mutable state.

## Endpoint contract (must hold after refactoring)

- Same paths, methods and success status codes as before.
- Same success response shape and field names, except removed sensitive fields (passwords, hashes, secrets, internal paths).
- Errors use `{"error": "<message>"}` with a correct status (400 invalid input, 403 guarded, 404 missing, 409 conflict, 500 unexpected).
- Guarded dangerous routes still exist and return 403 unless enabled by config.
- Seed/setup scripts found in Phase 1 still work (adapt their imports if the app creation changes).
- The original start command still works (`python app.py`, `npm start`). If it must change, update the manifest/README and report it.

## Target tree: Python / Flask (monolith being split)

```text
<project>/
├── app.py                       # composition root: create_app(), register blueprints and handlers, run
├── config/
│   └── settings.py
├── database.py | db/connection.py   # connection per app context, schema init, seed
├── models/
│   └── <entity>_model.py
├── controllers/
│   └── <entity>_controller.py
├── views/ (or routes/)
│   └── <entity>_routes.py       # one Blueprint per resource
├── middlewares/
│   ├── error_handler.py
│   └── guards.py
└── .env.example
```

Keep `app.py` at the project root when it is the original start command. Use an app factory (`create_app()`) so config and DB are injected.

## Target tree: Node.js / Express

```text
<project>/
├── package.json                 # "start" script still points to the entry point
├── src/
│   ├── app.js                   # composition root: express(), middlewares, routes, error handler, listen
│   ├── config/index.js
│   ├── db/connection.js         # connection + promisified helpers + schema/seed
│   ├── models/<entity>Model.js
│   ├── controllers/<useCase>Controller.js
│   ├── routes/index.js          # express.Router(), one file per resource if several
│   └── middlewares/
│       ├── errorHandler.js
│       └── adminOnly.js
└── .env.example
```

Models and controllers are factories receiving their dependencies (`createUserModel(db)`), so the composition root wires everything.

## Projects that are already partially layered

Evolve in place; do not move everything under a new root.

1. Keep existing folders that already match a layer (`models/`, `routes/`, `services/`). Treat `routes/` as the View layer.
2. Add only the missing layers: `config/`, `controllers/`, `middlewares/`.
3. Move logic out of route files into new controller files (PB07). Route files keep the same blueprints/paths.
4. Move resources to the right blueprint/controller when misplaced (e.g. CRUD of one entity living in another entity's routes), keeping the URL unchanged.
5. Reuse existing helpers/validators instead of duplicating them; delete those that stay unused.
6. Keep the ORM. Fix its usage (N+1, deprecated calls, transactions) instead of replacing it.

## Naming

- Python: `snake_case` files, `<entity>_model.py`, `<entity>_controller.py`, `<entity>_routes.py`.
- JS: `camelCase` files, `<entity>Model.js`, `<useCase>Controller.js`.
- Keep the domain vocabulary of the project (if entities are named in Portuguese, keep those names; do not translate the domain).

## Definition of done (Phase 3 checklist)

- [ ] Directory structure follows the target tree (or the in-place evolution rules).
- [ ] Configuration extracted to a config module; no hardcoded secrets.
- [ ] Models abstract all data access.
- [ ] Views/Routes only handle HTTP.
- [ ] Controllers hold the application flow.
- [ ] Centralized error handling.
- [ ] Clear entry point (composition root).
- [ ] App boots without errors.
- [ ] Original endpoints respond correctly (see `validation.md`).
