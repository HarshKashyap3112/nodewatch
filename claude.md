# CLAUDE.md

This file gives Claude (and any contributor) the context needed to work on this repository. It reflects the project's BRD (`Server_Monitoring_Platform_BRD.md`) — read that first for full requirements.

## Project Overview

**Server Monitoring Platform (SMP)** — a self-hosted, agent-based monitoring tool for personal/owned server infrastructure. Inspired by **Prometheus** (metrics collection model) and **Grafana** (dashboard UX), but scoped down to what one person needs to monitor their own servers: metrics, service checks, and threshold alerting.

Full requirements, scope boundaries, and rollout phases live in the BRD. Do not silently expand scope beyond Phase 1 (see BRD §3.1) without flagging it.

## Tech Stack (non-negotiable)

| Layer | Technology | Notes |
|---|---|---|
| Backend / API | **Python + FastAPI** | All backend services (collector API, alert engine, dashboard read API) live here. Use `async def` endpoints and Pydantic models for request/response validation. |
| Database | **SQL (MySQL)** | Relational schema, not a document store. Use SQLAlchemy (async, via `aiomysql`/`asyncmy`) + Alembic for migrations. Time-series data goes in a properly indexed `metrics` table (`server_id`, `metric_name`, `timestamp`, `value`), not one column per metric. |
| Frontend | **React** | Vite + TypeScript. Talks to the FastAPI backend only via the documented REST API — no direct DB access from the frontend. |
| Agent | **Python + psutil** | Separate deployable from the backend. Pushes metrics over HTTPS; never accepts inbound connections from the collector. |

Do not introduce a different database engine, backend framework, or frontend framework without discussing it first — this stack is fixed by design, not a placeholder.

## Architecture Rules

- **Push-based agent model.** Agents collect their own data and push it to the collector. The collector/backend never stores or uses server passwords or broad-access SSH keys (see BRD §5.2, §11). This is a security requirement, not just a style choice.
- **Clear service boundaries.** Keep these logically separate even if they share a codebase initially: (1) ingest API (receives agent data), (2) read API (serves the dashboard), (3) alert engine (evaluates rules on a schedule), (4) auth. Don't tangle alert-evaluation logic into the ingest endpoint.
- **Auth on everything.** Every agent request needs a valid per-agent API key. Every dashboard/API request needs an authenticated session or token. No open endpoints except health checks.
- **Migrations, not manual schema edits.** Any DB schema change goes through an Alembic migration, committed alongside the code that needs it.

## Backend Structure (required layout)

The backend follows a **domain-driven module layout** — one folder per domain, each self-contained with its own router, schemas, models, dependencies, service logic, and exceptions. Do not collapse everything into a handful of global files (`routes.py`, `models.py`, `utils.py`); every new domain gets its own module following this exact shape:

```
backend/
├── src/
│   ├── auth/
│   │   ├── router.py           # /api/v1/auth/* endpoints
│   │   ├── schemas.py          # pydantic request/response models (RegisterIn, TokenOut...)
│   │   ├── models.py           # SQLAlchemy ORM models (User) + query helpers
│   │   ├── dependencies.py     # get_current_user, require_role("owner"|"viewer")
│   │   ├── config.py           # module-local settings (token expiry, etc.)
│   │   ├── constants.py        # role enums, error codes
│   │   ├── exceptions.py       # InvalidCredentials, UserAlreadyExists...
│   │   ├── service.py          # register/login/hash/verify business logic
│   │   └── utils.py            # password hashing helpers, JWT encode/decode
│   │
│   ├── servers/
│   │   ├── router.py           # /api/v1/servers/* CRUD (register/rename/remove a monitored server)
│   │   ├── schemas.py          # ServerCreate, ServerOut, ApiKeyOut
│   │   ├── models.py           # Server, AgentApiKey ORM models
│   │   ├── dependencies.py     # get_server_or_404, ownership check
│   │   ├── constants.py        # server status enums (healthy/warning/critical/offline)
│   │   ├── exceptions.py       # ServerNotFound, ApiKeyRevoked
│   │   ├── service.py          # registration logic, API key issuing/revocation
│   │   └── utils.py            # API key generation/hashing helpers
│   │
│   ├── metrics/
│   │   ├── router.py           # /api/v1/metrics/* (agent ingest endpoint, dashboard query endpoint)
│   │   ├── schemas.py          # MetricIn (agent push payload), MetricSeriesOut
│   │   ├── models.py           # Metric ORM model (server_id, metric_name, timestamp, value)
│   │   ├── dependencies.py     # authenticate_agent (validates per-agent API key)
│   │   ├── constants.py        # metric_name enums (cpu, memory, disk, network)
│   │   ├── exceptions.py       # InvalidMetricPayload
│   │   ├── service.py          # ingest logic, time-range query/aggregation for charts
│   │   └── utils.py            # payload validation, downsampling helpers
│   │
│   ├── checks/
│   │   ├── router.py           # /api/v1/checks/* (service check results ingest + read)
│   │   ├── schemas.py          # CheckResultIn, CheckResultOut
│   │   ├── models.py           # CheckResult ORM model
│   │   ├── dependencies.py
│   │   ├── constants.py        # check_type enums (process_running/port_open/disk_space)
│   │   ├── exceptions.py       # CheckNotFound
│   │   ├── service.py          # check-result storage, pass/fail evaluation
│   │   └── utils.py
│   │
│   ├── alerts/
│   │   ├── router.py           # /api/v1/alerts/* (list rules, create rule, list active/past alerts)
│   │   ├── schemas.py          # AlertRuleIn, AlertRuleOut, AlertOut
│   │   ├── models.py           # AlertRule, Alert ORM models
│   │   ├── dependencies.py     # verify_rule_ownership
│   │   ├── constants.py        # alert state enums (triggered/resolved/acknowledged)
│   │   ├── exceptions.py       # AlertRuleInvalid, AlertNotFound
│   │   ├── service.py          # rule evaluation logic, alert lifecycle (trigger/recover)
│   │   └── utils.py
│   │
│   ├── notifications/          # outbound channel integrations
│   │   ├── client.py           # webhook (Slack/Telegram) + email client wrappers
│   │   ├── schemas.py          # NotificationPayload
│   │   ├── config.py           # provider keys, webhook URLs, sender address
│   │   ├── constants.py        # channel enums (webhook/email)
│   │   ├── exceptions.py       # NotificationDeliveryError
│   │   └── utils.py            # payload templating (alert text, recovery text)
│   │
│   ├── scheduler/
│   │   ├── jobs.py             # alert-rule evaluation job, offline-server sweep
│   │   ├── config.py           # interval settings (evaluation frequency, offline timeout)
│   │   └── exceptions.py
│   │
│   ├── config.py               # global settings (pydantic-settings): DB URL, JWT secret, CORS
│   ├── models.py               # global declarative Base + mixins (id, created_at/updated_at)
│   ├── exceptions.py           # global exception classes + FastAPI exception handlers
│   ├── pagination.py           # shared pagination params/response wrapper
│   ├── database.py             # SQLAlchemy async engine/session init, get_db()
│   └── main.py                 # FastAPI app factory, router registration, CORS, lifespan events
│
├── tests/
│   ├── auth/
│   ├── servers/
│   ├── metrics/
│   ├── checks/
│   └── alerts/
├── alembic/                    # migrations (one per schema change, never edit schema by hand)
├── requirements/
│   ├── base.txt
│   ├── dev.txt
│   └── prod.txt
├── .env
├── .gitignore
└── logging.ini
```

Rules that go with this layout:

- **models.py in each module = SQLAlchemy ORM models**, not Mongo documents — this project is MySQL end to end (see Tech Stack). Don't mix ORMs or add a document-store module.
- **service.py owns business logic**; `router.py` stays thin — parse request, call service, return response. Don't put query logic or business rules directly in route handlers.
- **Cross-module imports go through `service.py`**, not directly through another module's `models.py`, so ownership checks and validation aren't bypassed (e.g. `alerts/service.py` calls `servers/service.py` to confirm a server exists, rather than querying the `Server` model directly).
- Every new domain (e.g. a future `users/` module for multi-user access in Phase 3) follows this same nine-file shape unless there's a good reason not to.

## Design Direction (Frontend)

The UI should look like a **serious, professional monitoring tool** — the visual language of Grafana/Prometheus, not a generic admin dashboard template. Specifically:

- **Dark-mode-first.** Default to a dark theme (deep charcoal/navy background, not pure black) with a light-mode toggle as a secondary option. This is the convention operators expect from monitoring tools.
- **Data density with clarity.** Favor compact, information-dense layouts (like Grafana panels) over generous whitespace — but every number must be immediately legible and unambiguous. Never show a bare number without a unit, a label, or a time range attached to it.
- **Status must be instantly readable.** Use a consistent, limited color vocabulary for state: green = healthy, amber/yellow = warning, red = critical, gray = offline/unknown. Never rely on color alone — pair it with an icon or text label for accessibility.
- **Charts over tables where possible**, but always allow drilling into exact values (hover tooltips with precise numbers + timestamps, not just visual trend lines).
- **No ambiguous states.** Every panel should make it obvious whether data is live, stale, or missing — never show a blank chart with no explanation. Loading, empty, and error states are all designed explicitly, not left as blank divs.
- **Typography**: a clean monospace or semi-condensed sans for numbers/metrics (readability at a glance), a standard sans for body text/labels. Avoid decorative fonts entirely — this is an operational tool, not a marketing site.
- **Consistent iconography** for status and metric types (CPU, memory, disk, network) reused everywhere — sidebar, server list, detail view — so recognition is instant.

Before building any new UI screen, check `/mnt/skills/public/frontend-design/SKILL.md` (if working in this environment) for house design-token and styling conventions.

## Conventions

- **Python**: type-annotated everywhere, `ruff` for linting, `black` for formatting.
- **API design**: REST, versioned under `/api/v1/`, JSON in/out, errors as `{"detail": "..."}` matching FastAPI defaults.
- **React**: functional components + hooks only, no class components. Co-locate component styles. Keep API calls in a dedicated `api/` client layer, not scattered in components.
- **Commits**: small, scoped commits; reference the BRD requirement ID (e.g. `FR-2.1`) in the commit message when implementing a specific requirement.
- **Security defaults**: never log secrets or API keys; never commit `.env` files; agent API keys are write-scoped (metrics ingest only) and revocable.

## What NOT to do

- Don't add SSH/password-based remote polling as the primary collection method — agent-based push is the architecture (BRD §5.2, §8).
- Don't reach for MongoDB/InfluxDB/etc. instead of MySQL for Phase 1 — keep storage simple until scale actually requires a change (BRD §8).
- Don't build multi-tenant/SaaS features — this is single-owner infrastructure (BRD §3.3).
- Don't ship a UI screen with an unstyled/default-browser look — every screen should match the design direction above before it's considered done.