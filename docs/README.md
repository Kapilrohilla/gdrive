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
| Auth | JWT (guest, access, refresh) + DB-backed sessions + visitor tracking |

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

All routes are prefixed with `/api`, except short URL routes mounted at `/s/*`.

| Method | Path | Auth | Description |
| --- | --- | --- | --- |
| `GET` | `/health` | — | Health check |
| `POST` | `/visitor/` | — | Register visitor, returns guest JWT |
| `GET` | `/visitor/` | Access JWT | List visitors |
| `POST` | `/auth/register/me` | Guest JWT | Register user, create session, return access + refresh tokens |
| `POST` | `/auth/login/me` | Guest JWT | Login user, create session, return tokens |
| `POST` | `/auth/refresh` | Refresh JWT | Rotate refresh token, return new access + refresh tokens |
| `POST` | `/auth/logout` | Access JWT | Revoke current session |
| `POST` | `/auth/logout/all` | Access JWT | Revoke all sessions for the user |
| `GET` | `/auth/events` | Access JWT | List auth events for current user |
| `GET` | `/rbac/roles` | Access JWT | List roles |
| `POST` | `/rbac/roles` | Access JWT | Create role |
| `GET` | `/rbac/roles/{id}` | Access JWT | Get role |
| `PATCH` | `/rbac/roles/{id}` | Access JWT | Update role |
| `DELETE` | `/rbac/roles/{id}` | Access JWT | Delete role (non-system only) |
| `GET` | `/rbac/permissions` | Access JWT | List permissions |
| `POST` | `/rbac/permissions` | Access JWT | Create permission |
| `GET` | `/rbac/permissions/{id}` | Access JWT | Get permission |
| `PATCH` | `/rbac/permissions/{id}` | Access JWT | Update permission |
| `DELETE` | `/rbac/permissions/{id}` | Access JWT | Delete permission |
| `GET` | `/rbac/roles/{id}/permissions` | Access JWT | List permissions assigned to role |
| `POST` | `/rbac/roles/{id}/permissions` | Access JWT | Assign permission to role |
| `DELETE` | `/rbac/roles/{id}/permissions/{permission_id}` | Access JWT | Remove permission from role |
| `GET` | `/rbac/me/permissions` | Access JWT | List current user's permissions via role |
| `GET` | `/users/` | Access JWT | List users |
| `POST` | `/users/` | Access JWT | Create user |
| `POST` | `/folders/` | Access JWT | Create folder |
| `GET` | `/folders/` | Access JWT | List folders |
| `POST` | `/files/gen_upload_link` | Access JWT + RBAC | Generate S3 presigned upload URL |
| `POST` | `/files/mark_upload_complete` | Access JWT + RBAC | Mark file upload complete; emits thumbnail outbox event |
| `GET` | `/files/` | Access JWT + RBAC | List ready files (optional `folder_id`) |
| `GET` | `/files/{file_id}` | Access JWT + RBAC | Get file metadata |
| `GET` | `/files/{file_id}/preview` | Access JWT + RBAC | Presigned inline preview URL |
| `GET` | `/files/{file_id}/download` | Access JWT + RBAC | Presigned download URL |
| `GET` | `/files/{file_id}/activity` | Access JWT + RBAC | File activity timeline |
| `POST` | `/s/shorten` | Access JWT | Create short URL |
| `GET` | `/s/` | Access JWT | List current user's short URLs |
| `GET` | `/s/{short_code}` | — | Redirect to original URL |

### Auth flow

1. `POST /api/visitor/` — create or fetch visitor → receive **guest** JWT
2. `POST /api/auth/register/me` or `/api/auth/login/me` with `Authorization: Bearer <guest_jwt>` → creates a **session** in DB and returns **access** + **refresh** JWTs (both include `session_id`)
3. `POST /api/auth/refresh` with `Authorization: Bearer <refresh_jwt>` → validates session + rotates refresh token hash → new token pair
4. `POST /api/auth/logout` with `Authorization: Bearer <access_jwt>` → revokes current session (`revoked_at` set)
5. `POST /api/auth/logout/all` with `Authorization: Bearer <access_jwt>` → revokes all user sessions
6. Protected routes use `authenticate(TokenType.ACCESS)` — validates JWT, checks session is active, updates `last_seen_at`
7. Auth events (`login success`, `login failed`, `logout`, `session created`, `session revoked`) are persisted to `auth_events` during the above flows
8. RBAC admin APIs under `/api/rbac/*` manage roles, permissions, and role-permission assignments (access JWT required; permission enforcement middleware TBD)

Refresh tokens are stored as SHA-256 hashes in `sessions.refresh_token_hash`. Each refresh rotates the hash (reuse of an old refresh token fails after rotation).

**Public routes:** `GET /health`, `POST /api/visitor/` (register only), and auth bootstrap endpoints (`/auth/register/me`, `/auth/login/me` with guest JWT).

All other mounted API routes require an **access JWT** unless noted (refresh uses refresh JWT).

## Project structure

```
app/
├── api/v1/endpoints/     auth, rbac, visitor, users, folders, files, short_url
├── middleware/           JWT authenticate + RBAC permission dependencies
├── models/               files, folders, outbox, resource_events, short_urls
├── models/iam/           user, identity, session, visitor, role, permission, auth_events
├── services/             drive/, iam/, resource_events, short_urls, utils/
├── schemas/
│   ├── endpoints/        API request/response schemas (per endpoint)
│   └── iam/              Domain DTOs
├── constants/            Shared enums (OutboxTopics, ResourceEventActions, etc.)
└── core/                 database, queue/pooler, security (token hashing)
```

## Long-term goal

Evolve from secure cloud storage into a **privacy-first personal intelligence platform** — store, organize, share, search, and interact with personal content using AI, with full data ownership and DPDP compliance.

See [roadmap/vision.md](roadmap/vision.md) for phases and [roadmap/current-status.md](roadmap/current-status.md) for what is implemented today.
