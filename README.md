# Criação de Skills — Refatoração Arquitetural Automatizada

Ao longo do curso você aprendeu o que são Skills e como elas permitem que um agente de IA atue como um especialista em tarefas específicas. Agora imagine o seguinte cenário: você herdou 3 projetos legados com problemas de arquitetura, segurança e qualidade de código. Revisar e corrigir tudo manualmente levaria dias.

Neste desafio, você vai criar uma Skill que automatiza esse processo — analisando, auditando e refatorando qualquer projeto para o padrão MVC, independente da tecnologia.

## Objetivo

Você deve entregar uma Skill capaz de:

- Analisar uma codebase detectando linguagem, framework e arquitetura atual
- Identificar anti-patterns e code smells, classificando por severidade com arquivo e linha exatos
- Gerar um relatório de auditoria estruturado com todos os achados
- Refatorar o projeto para o padrão MVC (Model-View-Controller), eliminando os problemas encontrados
- Validar o resultado garantindo que a aplicação continua funcionando após as mudanças

A skill deve ser agnóstica de tecnologia, funcionando com diferentes linguagens e frameworks.

## Contexto

### Definição de Severidades

Para padronizar a sua auditoria e os relatórios gerados pela IA, utilize a seguinte escala de classificação baseada em problemas de MVC e SOLID:

- **CRITICAL:** Falhas graves de arquitetura ou segurança que impedem o funcionamento correto, expõem dados sensíveis (ex: credenciais hardcoded, SQL Injection) ou violam completamente a separação de responsabilidades (ex: "God Class" contendo banco de dados, lógicas complexas e roteamento no mesmo arquivo).
- **HIGH:** Fortes violações do padrão MVC ou princípios SOLID que dificultam muito a manutenção e testes (ex: lógicas de negócio pesadas presas dentro de Controllers, forte acoplamento sem Injeção de Dependência, ou uso de estado global mutável em toda a aplicação).
- **MEDIUM:** Problemas de padronização, duplicação de código ou gargalos de performance moderada (ex: Queries N+1 no banco de dados, uso inadequado de middlewares, validações ausentes nas rotas).
- **LOW:** Melhorias de legibilidade, nomenclatura de variáveis ruins, ou "magic numbers" soltos pelo código.

### Exemplo de Uso no CLI

```bash
# Executar a skill no projeto com problemas
cd code-smells-project
claude "/refactor-arch"
```

```
================================
PHASE 1: PROJECT ANALYSIS
================================
Language:      Python
Framework:      Flask 3.1.1
Dependencies:  flask-cors
Domain:        E-commerce API (produtos, pedidos, usuários)
Architecture:  Monolítica — tudo em 4 arquivos, sem separação de camadas
Source files:  4 files analyzed
DB tables:     produtos, usuarios, pedidos, itens_pedido
================================
```

```
================================
ARCHITECTURE AUDIT REPORT
================================
Project: code-smells-project
Stack:   Python + Flask
Files:   4 analyzed | ~800 lines of code

## Summary
CRITICAL: 4 | HIGH: 5 | MEDIUM: 2 | LOW: 3

## Findings

### [CRITICAL] God Class / God Method
File: models.py:1-350
Description: Arquivo único contém toda lógica de negócio, queries SQL, validação e formatação para 4 domínios diferentes.
Impact: Impossível testar em isolamento, qualquer mudança afeta tudo.
Recommendation: Separar em models e controllers por domínio.

### [CRITICAL] Hardcoded Credentials
File: app.py:8
Description: SECRET_KEY hardcoded como 'minha-chave-super-secreta-123'
...

================================
Total: 14 findings
================================

Phase 2 complete. Proceed with refactoring (Phase 3)? [y/n]
> y
```

```
[... refatoração executada ...]

================================
PHASE 3: REFACTORING COMPLETE
================================
## New Project Structure
src/
├── config/settings.py
├── models/
│   ├── produto_model.py
│   └── usuario_model.py
├── views/
│   └── routes.py
├── controllers/
│   ├── produto_controller.py
│   └── pedido_controller.py
├── middlewares/error_handler.py
└── app.py (composition root)

## Validation
  ✓ Application boots without errors
  ✓ All endpoints respond correctly
  ✓ Zero anti-patterns remaining
================================
```

## Tecnologias obrigatórias

- **Ferramenta:** uma das três opções abaixo (não são aceitas outras ferramentas):
  - Claude Code
  - Gemini CLI
  - OpenAI Codex
- **Recurso:** Custom Skills (ou o equivalente na ferramenta escolhida)
- **Formato dos arquivos de referência:** Markdown
- **Projetos-alvo:** Python/Flask (2 projetos) e Node.js/Express (1 projeto) (fornecidos no repositório base)

> **Nota sobre a ferramenta:** Os exemplos deste documento usam o Claude Code (`.claude/skills/`) como referência, pois é a ferramenta utilizada no curso. Se você optar por Gemini CLI ou Codex, adapte o nome da pasta e o comando de invocação conforme a convenção dela — o conceito de skill e a estrutura interna (SKILL.md + arquivos de referência) permanecem os mesmos.

## Requisitos

### 1. Análise Manual dos Projetos

Antes de criar a skill, você deve entender os problemas que ela vai resolver.

**Tarefas:**

- Analisar o projeto `code-smells-project/` (Python/Flask — API de E-commerce)
- Analisar o projeto `ecommerce-api-legacy/` (Node.js/Express — LMS API com fluxo de checkout)
- Analisar o projeto `task-manager-api/` (Python/Flask — API de Task Manager)

Para cada projeto, identificar e documentar no mínimo 5 problemas, incluindo pelo menos:

- 1 de severidade CRITICAL ou HIGH
- 2 de severidade MEDIUM
- 2 de severidade LOW

Documentar os achados na seção "Análise Manual" do seu `README.md`

> **Dica:** Não precisa encontrar todos os problemas — foque nos que têm maior impacto arquitetural. Use os projetos como insumo para entender quais padrões sua skill precisa detectar.

> **Por que 3 projetos?** Dois são Python/Flask (com níveis de organização diferentes) e um é Node.js/Express. Sua skill precisa funcionar nos 3 para provar que é verdadeiramente agnóstica de tecnologia — lidando tanto com código completamente desestruturado quanto com projetos que já possuem alguma separação de camadas.

### 2. Criação da Skill

Agora que você conhece os problemas, crie uma skill que os detecte, gere um relatório de auditoria e corrija automaticamente.

**Tarefas:**

Criar a skill dentro do projeto `code-smells-project/` e implementar o SKILL.md com 3 fases sequenciais:

- **Fase 1 — Análise:** Detectar stack, mapear arquitetura atual, imprimir resumo
- **Fase 2 — Auditoria:** Cruzar código contra catálogo de anti-patterns, gerar relatório, pedir confirmação
- **Fase 3 — Refatoração:** Reestruturar para o padrão MVC, validar que funciona

Criar arquivos de referência em Markdown que forneçam à skill o conhecimento necessário para executar as 3 fases. Os arquivos devem cobrir **obrigatoriamente** as seguintes áreas de conhecimento:

| Área de conhecimento | O que deve conter |
|---|---|
| Análise de projeto | Heurísticas para detecção de linguagem, framework, banco de dados e mapeamento de arquitetura |
| Catálogo de anti-patterns | Anti-patterns com sinais de detecção e classificação de severidade |
| Template de relatório | Formato padronizado do relatório de auditoria (Fase 2) |
| Guidelines de arquitetura | Regras do padrão MVC alvo (camadas Models, Views/Routes e Controllers, responsabilidades de cada uma) |
| Playbook de refatoração | Padrões concretos de transformação para cada anti-pattern (com exemplos de código) |

> **Nota:** Você tem liberdade para organizar os arquivos de referência como preferir — pode usar os nomes e a quantidade de arquivos que fizer sentido para sua skill. O importante é que todas as 5 áreas de conhecimento estejam cobertas. O nome da skill (`refactor-arch`) e o arquivo `SKILL.md` são obrigatórios e não devem ser alterados. O path da skill segue a convenção da ferramenta escolhida (no Claude Code, por exemplo, é `.claude/skills/refactor-arch/`).

**Requisitos da skill:**

- Deve ser agnóstica de tecnologia — deve funcionar corretamente nos 3 projetos fornecidos, independente da stack ou nível de organização
- O catálogo de anti-patterns deve conter no mínimo 8 anti-patterns com severidade distribuída (CRITICAL, HIGH, MEDIUM, LOW)
- O catálogo deve incluir detecção de APIs deprecated — identificar uso de APIs obsoletas e recomendar o equivalente moderno
- O playbook deve ter no mínimo 8 padrões de transformação com exemplos de código antes/depois
- A Fase 2 deve pausar e pedir confirmação antes de modificar qualquer arquivo
- A Fase 3 deve validar o resultado (boot da aplicação + endpoints funcionando)

### 3. Execução da Skill

Execute sua skill nos 3 projetos e valide que ela funciona em todas as stacks.

#### Projeto 1 — code-smells-project (Python/Flask)

Invocar a skill no Claude Code:

```bash
claude "/refactor-arch"
```

> **Nota:** O comando acima é o exemplo com Claude Code. Se você estiver usando Gemini CLI ou Codex, utilize o comando equivalente para invocar uma skill na sua ferramenta.

- Verificar que a Fase 1 detecta corretamente a stack e imprime o resumo
- Verificar que a Fase 2 encontra no mínimo 5 dos problemas documentados na sua análise manual
- Confirmar a execução da Fase 3
- Verificar que a Fase 3:
  - Cria a estrutura de diretórios baseada em MVC
  - A aplicação inicia sem erros
  - Os endpoints originais continuam respondendo
- Salvar o relatório de auditoria (output da Fase 2) em `reports/audit-project-1.md`
- Commitar o código refatorado do projeto no repositório

#### Projeto 2 — ecommerce-api-legacy (Node.js/Express)

Prove que sua skill é reutilizável em outro projeto de backend, mas com stack diferente.

- Copiar a pasta `.claude/skills/refactor-arch/` para dentro de `ecommerce-api-legacy/`
- Invocar a skill:

```bash
cd ../ecommerce-api-legacy
claude "/refactor-arch"
```

- Verificar que as 3 fases executam corretamente neste projeto
- Salvar o relatório em `reports/audit-project-2.md`
- Commitar o código refatorado do projeto no repositório

#### Projeto 3 — task-manager-api (Python/Flask)

Agora o teste com um projeto Python/Flask que já possui alguma organização de camadas (models, routes, services, utils).

- Copiar a pasta `.claude/skills/refactor-arch/` para dentro de `task-manager-api/`
- Invocar a skill:

```bash
cd ../task-manager-api
claude "/refactor-arch"
```

- Verificar que:
  - A Fase 1 detecta corretamente Python/Flask como stack e identifica o domínio de Task Manager
  - A Fase 2 identifica problemas mesmo em um projeto parcialmente organizado
  - A Fase 3 melhora a estrutura sem quebrar a aplicação (todos os endpoints devem continuar respondendo)
- Salvar o relatório em `reports/audit-project-3.md`
- Commitar o código refatorado do projeto no repositório

> **Nota:** Este projeto já possui alguma separação de camadas, mas isso não significa que a arquitetura está adequada. A skill deve identificar tanto problemas de código (segurança, performance, qualidade) quanto oportunidades de melhoria arquitetural. Se houver mudanças estruturais necessárias, a skill deve propô-las e executá-las.

#### Validação

Para cada projeto refatorado, valide o seguinte checklist:

```markdown
## Checklist de Validação

### Fase 1 — Análise
- [ ] Linguagem detectada corretamente
- [ ] Framework detectado corretamente
- [ ] Domínio da aplicação descrito corretamente
- [ ] Número de arquivos analisados condiz com a realidade

### Fase 2 — Auditoria
- [ ] Relatório segue o template definido nos arquivos de referência
- [ ] Cada finding tem arquivo e linhas exatos
- [ ] Findings ordenados por severidade (CRITICAL → LOW)
- [ ] Mínimo de 5 findings identificados
- [ ] Detecção de APIs deprecated incluída (se aplicável)
- [ ] Skill pausa e pede confirmação antes da Fase 3

### Fase 3 — Refatoração
- [ ] Estrutura de diretórios segue padrão MVC
- [ ] Configuração extraída para módulo de config (sem hardcoded)
- [ ] Models criados para abstrair dados
- [ ] Views/Routes separadas para visualização ou roteamento
- [ ] Controllers concentram o fluxo da aplicação
- [ ] Error handling centralizado
- [ ] Entry point claro
- [ ] Aplicação inicia sem erros
- [ ] Endpoints originais respondem corretamente
```

> **Dica:** Se a skill não detectou problemas suficientes ou a refatoração falhou, ajuste os arquivos de referência e execute novamente. É normal precisar de 2-4 iterações.

## Entregável

Repositório público no GitHub (fork do repositório base) contendo:

- Skill completa em `.claude/skills/refactor-arch/` (dentro dos 3 projetos)
- Código refatorado dos 3 projetos (resultado da execução da Fase 3, commitado no repositório)
- Relatórios de auditoria em `reports/` (3 arquivos)
- `README.md` atualizado

### Estrutura do repositório

Faça um fork do repositório base contendo os três projetos com code smells.

> **Nota:** A estrutura abaixo usa Claude Code como exemplo (`.claude/skills/`). Se estiver usando outra ferramenta, adapte os caminhos conforme a convenção dela.

```
desafio-skills/
├── README.md                              # Sua documentação
│
├── code-smells-project/                   # Projeto 1 — Python/Flask (API de E-commerce)
│   ├── .claude/
│   │   └── skills/
│   │       └── refactor-arch/             # ← SUA SKILL AQUI
│   │           ├── SKILL.md
│   │           └── (arquivos de referência)
│   ├── app.py
│   ├── controllers.py
│   ├── models.py
│   ├── database.py
│   └── requirements.txt
│
├── ecommerce-api-legacy/                  # Projeto 2 — Node.js/Express (LMS API com checkout)
│   ├── .claude/
│   │   └── skills/
│   │       └── refactor-arch/             # ← CÓPIA DA SKILL
│   │           └── ...
│   ├── src/
│   │   ├── app.js
│   │   ├── AppManager.js
│   │   └── utils.js
│   ├── api.http
│   └── package.json
│
├── task-manager-api/                      # Projeto 3 — Python/Flask (API de Task Manager)
│   ├── .claude/
│   │   └── skills/
│   │       └── refactor-arch/             # ← CÓPIA DA SKILL
│   │           └── ...
│   ├── app.py
│   ├── database.py
│   ├── seed.py
│   ├── requirements.txt
│   ├── models/
│   ├── routes/
│   ├── services/
│   └── utils/
│
└── reports/                               # Relatórios gerados
    ├── audit-project-1.md                 # Saída da Fase 2 no projeto 1
    ├── audit-project-2.md                 # Saída da Fase 2 no projeto 2
    └── audit-project-3.md                 # Saída da Fase 2 no projeto 3
```

**O que você vai criar:**

- `.claude/skills/refactor-arch/` — A skill completa (SKILL.md + arquivos de referência)
- Código refatorado dos 3 projetos — resultado da execução da Fase 3, commitado no repositório
- `reports/audit-project-{1,2,3}.md` — Relatório de auditoria de cada projeto
- `README.md` — Documentação do seu processo

**O que já vem pronto:**

- `code-smells-project/` — API de E-commerce Python/Flask com code smells intencionais
- `ecommerce-api-legacy/` — LMS API Node.js/Express (com fluxo de checkout) e problemas de implementação
- `task-manager-api/` — API de Task Manager Python/Flask com organização parcial e problemas de segurança/qualidade

> **Dica:** Cada projeto contém problemas intencionais de diferentes severidades (CRITICAL, HIGH, MEDIUM, LOW), incluindo falhas de segurança, violações arquiteturais e problemas de qualidade de código. Parte do desafio é identificá-los por conta própria através da análise manual do código.

### README.md deve conter

**A) Seção "Análise Manual":**

- Lista dos problemas identificados manualmente em cada projeto
- Classificação por severidade
- Justificativa de por que cada problema é relevante

**B) Seção "Construção da Skill":**

- Decisões de design: como estruturou o SKILL.md e os arquivos de referência
- Quais anti-patterns incluiu no catálogo e por quê
- Como garantiu que a skill é agnóstica de tecnologia
- Desafios encontrados e como resolveu

**C) Seção "Resultados":**

- Resumo dos relatórios de auditoria dos 3 projetos (quantos findings por severidade em cada)
- Comparação antes/depois da estrutura de cada projeto
- Checklist de validação preenchido para cada projeto
- Screenshots ou logs mostrando as aplicações rodando após refatoração
- Observações sobre como a skill se comportou em stacks diferentes

**D) Seção "Como Executar":**

- Pré-requisitos (a ferramenta escolhida — Claude Code, Gemini CLI ou Codex — instalada e configurada)
- Comandos para executar a skill em cada projeto
- Como validar que a refatoração funcionou

### Ordem de execução sugerida

**1. Analisar os projetos manualmente**

Leia o código dos três projetos e documente os problemas encontrados.

**2. Criar a skill**

Escreva o SKILL.md e os arquivos de referência.

**3. Executar nos 3 projetos**

```bash
# Projeto 1
cd code-smells-project
claude "/refactor-arch"

# Projeto 2
cd ../ecommerce-api-legacy
claude "/refactor-arch"

# Projeto 3
cd ../task-manager-api
claude "/refactor-arch"
```

Salve a saída da Fase 2 de cada projeto em `reports/audit-project-{1,2,3}.md`.

**4. Iterar**

Se a skill não detectou problemas suficientes ou a refatoração falhou, ajuste os arquivos de referência e execute novamente. É normal precisar de 2-4 iterações.

## Critérios de Aceite

A skill deve atingir os seguintes mínimos em **todos os 3 projetos**:

| Critério | Requisito |
|---|---|
| Fase 1 detecta stack corretamente | OBRIGATÓRIO (3/3 projetos) |
| Fase 2 encontra >= 5 findings | OBRIGATÓRIO (3/3 projetos) |
| Fase 2 inclui pelo menos 1 CRITICAL ou HIGH | OBRIGATÓRIO (3/3 projetos) |
| Fase 3 aplicação funciona após refatoração | OBRIGATÓRIO (3/3 projetos) |

**IMPORTANTE:** Todos os critérios devem ser atingidos nos 3 projetos, não apenas em um!

> **Sobre o projeto 3 (task-manager-api):** Este projeto já possui alguma organização. "aplicação funciona" significa que a API inicia sem erros e todos os endpoints continuam respondendo corretamente.

## Referências

- [Claude Code: Skills](https://docs.anthropic.com/en/docs/claude-code/skills) — Documentação oficial sobre como criar e estruturar Skills
- [Claude Code: Overview](https://docs.anthropic.com/en/docs/claude-code/overview) — Visão geral do Claude Code e suas capacidades
- [The Complete Guide to Building Skills for Claude (PDF)](https://resources.anthropic.com/hubfs/The-Complete-Guide-to-Building-Skill-for-Claude.pdf) — Guia completo da Anthropic sobre construção de Skills
- [Equipping Agents for the Real World with Agent Skills](https://claude.com/blog/equipping-agents-for-the-real-world-with-agent-skills) — Blog oficial da Anthropic sobre Agent Skills

---

## Dicas Finais

- **Comece pela análise manual** — entender os problemas profundamente é essencial para criar uma skill que os detecte.
- **O SKILL.md é um prompt** — ele instrui o agente sobre o que fazer, enquanto os arquivos de referência fornecem o conhecimento de domínio.
- **Seja específico nos sinais de detecção** — "código ruim" não ajuda; "query SQL dentro de loop for" é acionável.
- **Teste incrementalmente** — não tente criar a skill perfeita de primeira.
- **A skill deve ser copiável** — se ela só funciona em um projeto específico, está acoplada demais. Teste nos 3 projetos para validar.
- **Projetos diferentes exigem adaptação** — a Fase 3 de um projeto já parcialmente organizado não vai ter as mesmas transformações de um monolito. Sua skill deve se adaptar ao contexto.
- **Pedir confirmação na Fase 2 é obrigatório** — o humano deve revisar o relatório antes de qualquer modificação.
- **Consulte as referências do curso** — revise a documentação oficial da ferramenta escolhida e os materiais das aulas para relembrar a estrutura e anatomia de uma skill.
---

# Entrega

Ferramenta usada: **Claude Code**. Skill em `.claude/skills/refactor-arch/` (cópias idênticas nos 3 projetos). Artefatos de planejamento (spec, plano, tarefas) em [`specs/refactor-arch/`](specs/refactor-arch/).

## A) Análise Manual

Feita antes da skill, em duas passadas de leitura de código (achados com linha conferida). Ela serviu de gabarito: a Fase 2 da skill precisava reencontrar pelo menos 5 destes itens em cada projeto. Lista completa, com os 64 itens, em [`specs/refactor-arch/spec.md`](specs/refactor-arch/spec.md). Abaixo, os principais de cada projeto.

### Projeto 1: code-smells-project (Python/Flask, e-commerce)

| Severidade | Problema | Local | Por que importa |
| --- | --- | --- | --- |
| CRITICAL | SQL injection por concatenação de strings | models.py:28, 47-50, 110, 127-128 (e outros) | Permite burlar o login e ler/apagar qualquer dado. |
| CRITICAL | Endpoint que executa SQL arbitrário sem autenticação | app.py:59-78 | Qualquer pessoa executa qualquer comando no banco. |
| CRITICAL | `SECRET_KEY` hardcoded e devolvida no `/health` | app.py:7; controllers.py:289 | Segredo no repositório e exposto a qualquer cliente. |
| CRITICAL | Senhas em texto puro, gravadas e devolvidas pela API | models.py:83, 99; database.py:76-78 | Um vazamento expõe todas as senhas, e a API já as entrega. |
| CRITICAL | Debug ligado e servidor em `0.0.0.0` | app.py:8, 88 | O debugger do Werkzeug permite execução remota de código. |
| CRITICAL | God module: `models.py` mistura SQL, regras e relatórios de 4 domínios | models.py:1-314 | Nada pode ser testado isoladamente; qualquer mudança afeta tudo. |
| HIGH | Conexão global mutável, sem injeção de dependência | database.py:4-10 | Compartilhada entre threads, sem rollback; não dá para trocar nem mockar. |
| HIGH | Pedido não atômico: corrida no estoque e quantidade negativa aceita | models.py:139-166; controllers.py:198-203 | Vende sem estoque e aceita quantidade negativa, que aumenta o estoque. |
| HIGH | CORS aberto para qualquer origem numa API com rotas destrutivas | app.py:9 | Qualquer site pode chamar a API pelo navegador da vítima. |
| MEDIUM | Queries N+1 na listagem de pedidos | models.py:171-233 | O número de queries cresce com pedidos x itens. |
| MEDIUM | Validação ausente e nenhum tratamento de erro centralizado | controllers.py:26, 119, 169-170 | Entrada inválida vira erro 500 em vez de 400. |
| MEDIUM | Relatório soma pedidos cancelados como receita | models.py:242-245 | O faturamento reportado está errado. |
| LOW | Magic numbers nas faixas de desconto | models.py:257-262 | A regra de negócio fica escondida em literais. |
| LOW | `print()` usado como log | controllers.py:8, 11, 57 | Sem níveis de log; e-mails aparecem no output. |

### Projeto 2: ecommerce-api-legacy (Node.js/Express, LMS com checkout)

| Severidade | Problema | Local | Por que importa |
| --- | --- | --- | --- |
| CRITICAL | Credenciais hardcoded (banco, chave `pk_live` do gateway) | src/utils.js:2-5 | Segredos de produção versionados no repositório. |
| CRITICAL | "Hash" de senha caseiro e reversível | src/utils.js:17-23 | Senhas triviais de recuperar, e `123456` como senha padrão. |
| CRITICAL | Número do cartão e chave do gateway escritos no log | src/AppManager.js:45 | Vaza dado de cartão, o que viola PCI-DSS. |
| CRITICAL | God class `AppManager` (schema, rotas, pagamento, relatório) | src/AppManager.js:4-139 | Uma classe com todas as responsabilidades; impossível testar. |
| CRITICAL | Relatório financeiro e exclusão de usuário sem autenticação | src/AppManager.js:80, 131-132 | Qualquer pessoa lê a receita ou apaga usuários. |
| HIGH | Callback hell que engole erros | src/AppManager.js:37-77, 83-128 | A API responde sucesso em caso de falha, ou o processo cai. |
| HIGH | Checkout com e-mail existente não pede senha | src/AppManager.js:40, 73-74 | Permite usar a conta de outra pessoa. |
| HIGH | Checkout não atômico: usuário criado mesmo com cartão recusado | src/AppManager.js:46-48, 66-72 | Deixa registros órfãos e dados inconsistentes. |
| HIGH | Estado global mutável (`globalCache`, `totalRevenue`) | src/utils.js:9-10, 14 | Cresce sem limite, não é thread-safe e tem código morto. |
| MEDIUM | N+1 no relatório financeiro | src/AppManager.js:83-126 | Uma query por curso e outra por matrícula. |
| MEDIUM | Validação fraca e nenhum middleware de erro | src/AppManager.js:29-35; src/app.js | Um `card` numérico derruba o servidor. |
| LOW | Nomes crípticos (`u`, `e`, `cid`, `cc`) | src/AppManager.js:29-33 | Leitura difícil e contrato da API confuso. |
| LOW | Magic numbers e strings (`10000`, `"4"`, `"123456"`) | src/utils.js:19-22; src/AppManager.js:46, 68 | A intenção das regras fica oculta. |

### Projeto 3: task-manager-api (Python/Flask, Task Manager)

| Severidade | Problema | Local | Por que importa |
| --- | --- | --- | --- |
| CRITICAL | `SECRET_KEY` e credenciais SMTP hardcoded | app.py:13; services/notification_service.py:9-10 | Segredos versionados no repositório. |
| CRITICAL | Senha com MD5 sem salt | models/user.py:29, 32 | Hashes quebrados em segundos. |
| CRITICAL | Hash da senha devolvido nas respostas | models/user.py:21 | Todo endpoint de usuário expõe o hash. |
| CRITICAL | Cadastro público aceita `role=admin` (mass assignment) | routes/user_routes.py:52, 71-78 | Qualquer pessoa se torna administrador. |
| CRITICAL | Debug ligado e servidor em `0.0.0.0` | app.py:34 | Execução remota de código pelo debugger. |
| HIGH | Regra de negócio e persistência dentro das rotas | routes/task_routes.py:85-223; routes/report_routes.py:12-101 | A camada `services/` existe mas não é usada; as rotas fazem tudo. |
| HIGH | CORS aberto numa API sem autenticação | app.py:15 | Qualquer site pode chamar as rotas destrutivas. |
| MEDIUM | Queries N+1 | routes/task_routes.py:42, 51; routes/report_routes.py:56 | Uma query por tarefa ou por usuário. |
| MEDIUM | `except:` sem tipo | routes/task_routes.py:62, 137, 204 | Esconde erros reais. |
| MEDIUM | Regra de "atrasada" duplicada 6 vezes (método do model sem uso) | routes/task_routes.py:30-39, 71-80 | Mudar a regra exige editar 6 lugares. |
| MEDIUM | CRUD de categorias dentro do blueprint de relatórios | routes/report_routes.py:157-223 | Recurso no lugar errado e camadas confusas. |
| LOW | API deprecated `datetime.utcnow()` | models/task.py:15-16 (e outros) | Deprecated no Python 3.12. |
| LOW | API legada `Query.get()` | routes/task_routes.py:42 (e outros) | Legado no SQLAlchemy 2.0; o substituto é `db.session.get`. |
| LOW | Magic strings e constantes definidas mas não usadas | routes/task_routes.py:96-100; utils/helpers.py:110-116 | Listas de status repetidas e divergentes. |

## B) Construção da Skill

### Processo

Usei um speckit resumido: **spec** (análise manual mais decisões), **grilling** da spec (19 decisões explícitas), **plano**, **tarefas**, depois escrita da skill e execução. Os artefatos estão em [`specs/refactor-arch/`](specs/refactor-arch/).

### Estrutura

```text
.claude/skills/refactor-arch/
├── SKILL.md                        # orquestração: 3 fases, regras rígidas, blocos de saída
└── references/
    ├── project-analysis.md         # heurísticas: linguagem, framework, banco, rotas, domínio, arquitetura
    ├── anti-patterns.md            # catálogo: 25 anti-patterns com sinais de detecção e severidade
    ├── report-template.md          # formato do relatório da Fase 2
    ├── mvc-guidelines.md           # camadas, direção das dependências, árvores alvo Flask/Express
    ├── refactoring-playbook.md     # 16 transformações com código antes/depois
    └── validation.md               # baseline, diferenças esperadas, boot, comparação, teardown
```

Decisões de design:

- **O SKILL.md é curto e só orquestra** (cerca de 110 linhas). O conhecimento de domínio fica nas referências, e cada fase lê só os arquivos dela (progressive disclosure).
- **Regras rígidas** no topo: só lê a pasta atual; não altera nada antes do `y`; nenhum check é dado como aprovado sem ter rodado; nunca faz commit.
- **Validação objetiva**: antes de editar qualquer arquivo, a skill sobe o app original, chama todos os endpoints e grava um baseline. Depois do refactor, repete o mesmo plano e compara status e formato da resposta. Diferenças só são aceitas se declaradas antes (rota protegida virando 403, campo sensível removido).
- **Escopo da Fase 3**: corrige todos os CRITICAL e HIGH e cumpre o checklist MVC. MEDIUM e LOW que não saem naturalmente com a reestruturação ficam listados como "remaining"; a skill nunca declara "zero anti-patterns" com pendências.

### Catálogo de anti-patterns

25 entradas (8 CRITICAL, 6 HIGH, 6 MEDIUM, 5 LOW). A base veio dos achados da análise manual e foi complementada por pesquisa em OWASP Top 10 2021, OWASP API Security Top 10 2023, CWE Top 25, documentação de segurança do Express e Flask, e listas de deprecation de Python, SQLAlchemy 2.0, Flask, Node e Express 5. Cada entrada traz sinais concretos (por exemplo, "`execute(` com f-string ou `+`") em Python e JS, mais o padrão de correção do playbook. O AP23 tem uma tabela de APIs deprecated com o substituto moderno de cada uma.

### Agnóstica de tecnologia

- Os sinais de detecção são padrões de código (Python e JS), nunca nomes de arquivos destes projetos.
- O playbook mostra cada transformação em Python e em JS; as árvores alvo cobrem Flask e Express.
- Para projetos já parcialmente organizados (P3), a regra é **evoluir no lugar**: manter `models/`, `routes/` e `services/` e criar só as camadas que faltam.
- A prova é a mesma skill, copiada sem mudança nenhuma, funcionando nos 3 projetos (a cópia idêntica foi verificada com `diff -r`).

### Desafios e soluções

| Desafio | Solução |
| --- | --- |
| O `CLAUDE.md` global, os hooks e a memória do usuário contaminavam a sessão de teste (idioma, formato e até acesso ao gabarito) | Execução headless isolada: `--setting-sources project,local --strict-mcp-config` |
| Uma sessão que não resolvia a skill subia até a raiz do repo e achava o gabarito em `specs/` | Regra "só a pasta atual" no SKILL.md e auditoria de todos os caminhos lidos (stream-json) |
| O reloader do Flask em debug segura a porta depois de matar o processo pai (falso positivo na validação) | `validation.md` libera a porta antes do boot e mata a árvore inteira de processos (POSIX e Windows) |
| No Git Bash, `/refactor-arch` virava um caminho do Windows | `MSYS_NO_PATHCONV=1` |
| Guard 403 genérico bloquearia o CRUD normal | Regra explícita: guard só em admin, SQL/código arbitrário, reset e exclusão de conta |
| 1ª execução no P1: relatório resumido no terminal e contagem de endpoints errada (18 em vez de 19) | SKILL.md exige o relatório impresso por inteiro e confere a contagem; nova execução do zero |

## C) Resultados

### Resumo das auditorias

| Projeto | CRITICAL | HIGH | MEDIUM | LOW | Total | Relatório |
| --- | --- | --- | --- | --- | --- | --- |
| code-smells-project | 7 | 5 | 6 | 5 | 23 | [audit-project-1.md](reports/audit-project-1.md) |
| ecommerce-api-legacy | 5 | 5 | 5 | 5 | 20 | [audit-project-2.md](reports/audit-project-2.md) |
| task-manager-api | 5 | 4 | 6 | 5 | 20 | [audit-project-3.md](reports/audit-project-3.md) |

Nos 3 projetos, a auditoria cobriu bem mais do que os 5 itens mínimos do gabarito manual.

### Antes e depois

**Projeto 1**

```text
ANTES                      DEPOIS
app.py                     app.py                  (composition root, create_app)
controllers.py             config/settings.py, constants.py
models.py                  database.py             (conexão por request, schema, seed com hash)
database.py                errors.py
                           models/{produto,usuario,pedido,sistema}_model.py
                           controllers/{produto,usuario,pedido,relatorio,sistema}_controller.py, validators.py
                           views/{produto,usuario,pedido,relatorio,sistema}_routes.py
                           middlewares/{error_handler,guards,security_headers}.py
                           .env.example
```

**Projeto 2**

```text
ANTES                      DEPOIS
src/app.js                 src/app.js              (composition root)
src/AppManager.js          src/config/index.js
src/utils.js               src/db/connection.js    (promises + transações)
                           src/models/{user,course,enrollment,payment,audit}Model.js
                           src/controllers/{checkout,report,user}Controller.js
                           src/routes/index.js
                           src/middlewares/{errorHandler,adminOnly,rateLimit,securityHeaders}.js
                           src/utils/{constants,errors,logger,password}.js
                           .env.example
```

**Projeto 3** (evolução no lugar)

```text
ANTES                      DEPOIS
app.py, database.py,       app.py, database.py, seed.py      (mantidos e ajustados)
seed.py                    config/settings.py, constants.py  (novo)
models/                    models/ + base.py                 (sem senha no to_dict, scrypt)
routes/                    routes/ + category_routes.py, system_routes.py (rotas finas)
services/                  services/ + auth_service.py       (token assinado; SMTP injetado)
utils/                     utils/ + validators.py
                           controllers/{task,user,category,report}_controller.py (novo)
                           middlewares/{error_handler,guards,security_headers}.py (novo)
                           .env.example
```

### Checklist de validação

| Item | P1 | P2 | P3 |
| --- | --- | --- | --- |
| **Fase 1** Linguagem detectada | ✓ Python | ✓ JavaScript | ✓ Python |
| Framework detectado | ✓ Flask 3.1.1 | ✓ Express ^4.18.2 | ✓ Flask 3.0.0 |
| Domínio descrito corretamente | ✓ E-commerce | ✓ LMS com checkout | ✓ Task Manager |
| Número de arquivos condiz | ✓ 4 | ✓ 3 | ✓ 15 |
| **Fase 2** Relatório segue o template | ✓ | ✓ | ✓ |
| Arquivo e linhas exatos | ✓ | ✓ | ✓ |
| Ordenado de CRITICAL a LOW | ✓ | ✓ | ✓ |
| Mínimo de 5 findings | ✓ 23 | ✓ 20 | ✓ 20 |
| APIs deprecated detectadas | ✓ | ✓ | ✓ |
| Pausa e pede confirmação | ✓ | ✓ | ✓ |
| **Fase 3** Estrutura MVC | ✓ | ✓ | ✓ |
| Config extraída (sem hardcoded) | ✓ | ✓ | ✓ |
| Models abstraem os dados | ✓ | ✓ | ✓ |
| Views/Routes separadas | ✓ | ✓ | ✓ |
| Controllers concentram o fluxo | ✓ | ✓ | ✓ |
| Error handling centralizado | ✓ | ✓ | ✓ |
| Entry point claro | ✓ | ✓ | ✓ |
| Aplicação inicia sem erros | ✓ | ✓ | ✓ |
| Endpoints originais respondem | ✓ 26/26 | ✓ 7/7 | ✓ 29/29 |

### Evidências de execução

Cada projeto tem em `reports/` o relatório, o log de validação (baseline e depois, request por request) e os logs de boot:

- P1: [validation-log.md](code-smells-project/reports/validation-log.md), [boot-after.log](code-smells-project/reports/boot-after.log)
- P2: [validation-log.md](ecommerce-api-legacy/reports/validation-log.md), [boot-after.log](ecommerce-api-legacy/reports/boot-after.log)
- P3: [validation-log.md](task-manager-api/reports/validation-log.md), [boot-after.log](task-manager-api/reports/boot-after.log)

Além da validação da própria skill, fiz uma verificação independente em cada projeto, com banco limpo, boot e curl em todos os endpoints:

- **P1**: SQL injection no login retorna 401; quantidade negativa retorna 400; `/admin/*` retorna 403; o login seed funciona.
- **P2**: checkout ok; cartão recusado retorna 400; senha errada para conta existente retorna 401; `card` numérico retorna 400 (antes derrubava o processo).
- **P3**: o seed roda; o login seed funciona; `role=admin` no cadastro é ignorado; `DELETE /users` retorna 403.

### Comportamento em stacks diferentes

- **Python monolítico (P1)**: separação completa em camadas, com nomes de domínio em português mantidos (`produto_model.py`).
- **Node/Express (P2)**: além das camadas, converteu callbacks em async/await com transações, e os erros passaram a fluir para um middleware central. Não adicionou nenhuma dependência (`package.json` intacto): rate limit e headers foram escritos à mão.
- **Python parcialmente organizado (P3)**: evoluiu no lugar, sem mover tudo para `src/`. Criou `controllers/` e `config/`, moveu o CRUD de categorias para um blueprint próprio sem mudar as URLs, e corrigiu as APIs deprecated.
- **Pendência comum aos 3**: falta um sistema de autenticação. Está fora do escopo da refatoração; as rotas perigosas ficam protegidas por flag/token enquanto isso. O P3 marcou esse item com `✗` no bloco final, enquanto o SKILL.md pedia `✓` com a ressalva; a informação é a mesma.
- Custo aproximado por projeto (Fases 1 a 3): de US$1,06 a US$1,92.

## D) Como Executar

### Pré-requisitos

- [Claude Code](https://docs.anthropic.com/en/docs/claude-code/overview) instalado e autenticado.
- Python 3.10+ (testado com 3.14) e Node.js 18+ (testado com 24).

### Executar a skill

Interativo, a partir da pasta de cada projeto:

```bash
cd code-smells-project      # ou ecommerce-api-legacy, task-manager-api
claude "/refactor-arch"
# revise o relatório da Fase 2 e responda y para refatorar
```

Isolado das configurações do usuário (como foi executado aqui):

```bash
cd code-smells-project
claude -p "/refactor-arch" --setting-sources project,local --strict-mcp-config --permission-mode acceptEdits
claude -p "y" --continue --setting-sources project,local --strict-mcp-config --dangerously-skip-permissions
```

No Git Bash (Windows), prefixe com `MSYS_NO_PATHCONV=1`.

### Validar manualmente

```bash
# Projeto 1
cd code-smells-project && python -m venv .venv && .venv/bin/pip install -r requirements.txt
.venv/bin/python app.py                  # http://127.0.0.1:5000/produtos

# Projeto 2
cd ecommerce-api-legacy && npm ci && npm start   # requests de exemplo em api.http

# Projeto 3
cd task-manager-api && python -m venv .venv && .venv/bin/pip install -r requirements.txt
.venv/bin/python seed.py && .venv/bin/python app.py   # http://127.0.0.1:5000/tasks
```

Rotas administrativas: `ADMIN_ENABLED=1` (P1 e P3) ou `ADMIN_TOKEN=<token>` com o header `x-admin-token` (P2). As demais variáveis estão no `.env.example` de cada projeto.
