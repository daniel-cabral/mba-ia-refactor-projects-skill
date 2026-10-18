# Project analysis heuristics

Used in Phase 1. Goal: an accurate picture of the project before auditing. Work only inside the current working directory.

## 1. Scope

- Analyze only files under the current working directory. Never read parent directories.
- Ignore: `.claude/`, `.git/`, `node_modules/`, `.venv/`, `venv/`, `env/`, `__pycache__/`, `reports/`, `dist/`, `build/`, `instance/`, lock files (`package-lock.json`, `yarn.lock`, `poetry.lock`), databases (`*.db`, `*.sqlite`), binaries and images.
- Source files = code files of the detected language(s) (`.py`, `.js`, `.ts`, `.mjs`, `.cjs`, ...). Count them and their lines (approximate total is fine for lines, exact for file count).

## 2. Language and framework

| Evidence | Conclusion |
| --- | --- |
| `requirements.txt`, `pyproject.toml`, `Pipfile`, `setup.py`, `*.py` | Python |
| `package.json`, `*.js` / `*.ts` | Node.js (JavaScript / TypeScript) |
| `go.mod`, `pom.xml` / `build.gradle`, `Gemfile`, `composer.json`, `*.csproj` | Go, Java, Ruby, PHP, .NET |

Framework: read dependency names and versions from the manifest, then confirm in code.

| Manifest dependency | Code confirmation | Framework |
| --- | --- | --- |
| `flask` | `Flask(__name__)`, `@app.route`, `Blueprint` | Flask |
| `fastapi` | `FastAPI()`, `@app.get` | FastAPI |
| `django` | `settings.py`, `urls.py` | Django |
| `express` | `express()`, `app.get(`, `Router()` | Express |
| `@nestjs/core` | `@Controller` decorators | NestJS |
| `koa`, `fastify`, `hapi` | respective constructors | Koa / Fastify / Hapi |

Report the version as declared in the manifest (e.g. `Flask 3.1.1`, `Express ^4.18.2`). List the other runtime dependencies.

## 3. Database

| Evidence | Database / access style |
| --- | --- |
| `import sqlite3`, `sqlite3.connect(` | SQLite, raw SQL (Python) |
| `flask_sqlalchemy`, `SQLAlchemy(`, `db.Model` | SQLAlchemy ORM; engine from `SQLALCHEMY_DATABASE_URI` |
| `require('sqlite3')`, `new sqlite3.Database(` | SQLite, raw SQL (Node, callback API); `':memory:'` means in-memory |
| `psycopg`, `pg`, `mysql`, `mongoose`, `prisma`, `sequelize`, `typeorm` | PostgreSQL / MySQL / MongoDB / ORM |

Tables: collect from `CREATE TABLE` statements, ORM model classes (`__tablename__` or class names), or migrations.

## 4. Entry point, start command and setup

- Entry point: file that creates the app and starts the server (`app.run(`, `app.listen(`, `if __name__ == "__main__"`, `"main"` in package.json).
- Start command: `scripts.start` in package.json; otherwise `python <entry>.py`; check the project README for the documented command.
- Port: from `app.run(port=...)`, `app.listen(...)`, config or env.
- Setup/seed: scripts that populate data (`seed.py`, `seed.js`, `scripts.seed`, `init_db`), or seeds executed at boot. Note whether data exists after a fresh boot or only after running a seed.

## 5. Route discovery

List every endpoint as `METHOD path`.

| Framework | Where to look |
| --- | --- |
| Flask | `@app.route(...)`, `@<bp>.route(...)`, `@<bp>.get/post/...`, `app.add_url_rule(...)`; blueprint `url_prefix` in `Blueprint(...)` or `register_blueprint(...)`; `methods=[...]` (default GET) |
| Express | `app.get/post/put/patch/delete(...)`, `router.<method>(...)`, `app.use('<prefix>', router)` |
| FastAPI / Django / NestJS | decorators / `urls.py` / `@Get()` etc. |

Also check `*.http`, `*.rest`, Postman collections or README examples: they give sample payloads for validation.

## 6. Domain inference

Infer the business domain from table names, route paths and entity names (e.g. products + orders + users = e-commerce; courses + enrollments + payments = LMS with checkout; tasks + categories + users = task manager). Describe it in one line with the main entities.

## 7. Architecture classification

| Classification | Signals |
| --- | --- |
| Monolithic, no layers | Few files; routing, SQL and business rules mixed; one God class/module |
| Partially layered | Folders like `models/`, `routes/`, `services/`, `utils/` exist, but routes still hold logic or SQL, or layers are bypassed |
| MVC / layered | Distinct models, controllers (or services) and routes; routes are thin |

State the classification plus one short reason (e.g. "Monolithic: 4 files, SQL and routing in the same modules").

## 8. Phase 1 output

Print exactly this block (fill every line; use `none` when absent):

```text
================================
PHASE 1: PROJECT ANALYSIS
================================
Language:      <language + version if declared>
Framework:     <framework + version>
Dependencies:  <other runtime deps>
Domain:        <one line, main entities>
Architecture:  <classification: reason>
Source files:  <N> files analyzed (~<lines> lines)
Entry point:   <file> (start: <command>, port <port>)
Database:      <engine + access style>
DB tables:     <comma list>
Seed/setup:    <script or "at boot" or none>
Endpoints:     <N> (<METHOD path, ...>)
================================
```
