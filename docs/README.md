# CloudDrive Documentation

Secure, scalable, AI-powered personal data platform. Users store, organize, share, and intelligently interact with digital assets while retaining ownership and complying with the Digital Personal Data Protection (DPDP) Act.

The initial focus is cloud storage. The long-term goal is a privacy-first personal knowledge platform powered by AI.

## Principles

| Principle | Meaning |
| --- | --- |
| **Security first** | Authn/authz, least privilege, encryption in transit and at rest, session management, RBAC |
| **Privacy first** | Privacy by Design — minimize collection, explicit AI consent, right to erasure, no training without consent, strong user isolation |
| **AI as enhancement** | Core storage works without AI; AI is opt-in and never a hard dependency |

## Documentation map

```
docs/
├── README.md                 ← you are here
└── roadmap/
    ├── vision.md             Product vision and long-term goal
    ├── milestones.md         Phase 1–5 milestones
    ├── backlog.md            Planned work by domain
    └── current-status.md     Completed / in progress / next
```

Planned (not yet written): `architecture/`, `api/`, `decisions/`, `diagrams/`.

## Stack

| Layer | Technology |
| --- | --- |
| API | FastAPI (`CloudDrive API`) |
| Database | PostgreSQL 16 + SQLAlchemy async |
| Cache | Redis (docker-compose; not wired in app yet) |
| Object storage | AWS S3 (presigned uploads) |
| Auth | JWT (guest, access, refresh) + visitor tracking |

## Local development

```bash
# Start Postgres + Redis
docker compose up -d

# Run API (from backend/)
fastapi dev --port 5000
```

Configure environment in `.env` (see `.env.example`). Required: `DB_URL`, `JWT_SECRET`, AWS credentials for file uploads.

Interactive docs: `http://127.0.0.1:5000/docs`

## API overview (mounted routes)

All routes are prefixed with `/api`.

| Method | Path | Auth | Description |
| --- | --- | --- | --- |
| `GET` | `/health` | — | Health check |
| `POST` | `/visitor/` | — | Register visitor, returns guest JWT |
| `GET` | `/visitor/` | — | List visitors (dev/admin) |
| `POST` | `/auth/register/me` | Guest JWT | Register user, link visitor, return access + refresh tokens |
| `POST` | `/auth/login/me` | Guest JWT | Login user, link visitor if needed, return tokens |
| `GET` | `/users/` | — | List users |
| `POST` | `/users/` | — | Create user (admin/dev) |
| `POST` | `/folders/` | — | Create folder |
| `GET` | `/folders/` | — | List folders |
| `POST` | `/files/gen_upload_link` | — | Generate S3 presigned upload URL |
| `POST` | `/files/mark_upload_complete` | — | Mark file upload complete |
| `GET` | `/drive/*` | — | Mock drive UI data (frontend dev) |

### Auth flow

1. `POST /api/visitor/` — create or fetch visitor → receive **guest** JWT
2. `POST /api/auth/register/me` or `/api/auth/login/me` with `Authorization: Bearer <guest_jwt>` → receive **access** + **refresh** JWTs
3. Protected routes use `authenticate(TokenType.ACCESS)` dependency (middleware updates `visitor.last_seen_at` on each authenticated request)

Request/response schemas live in `app/schemas/endpoints/` (one file per endpoint module).

## Project structure

```
app/
├── api/v1/endpoints/     auth, visitor, users, folders, files, drive
├── middleware/           JWT authenticate dependencies
├── models/               files, folders, outbox
├── models/iam/           user, identity, session, visitor, role, permission, auth_events
├── services/             files, folder, user, iam/, utils/
├── schemas/
│   ├── endpoints/        API request/response schemas (per endpoint)
│   └── iam/              Domain DTOs
├── constants/            Shared enums
└── core/                 database, security (stub)
```

## Long-term goal

Evolve from secure cloud storage into a **privacy-first personal intelligence platform** — store, organize, share, search, and interact with personal content using AI, with full data ownership and DPDP compliance.

See [roadmap/vision.md](roadmap/vision.md) for phases and [roadmap/current-status.md](roadmap/current-status.md) for what is implemented today.
