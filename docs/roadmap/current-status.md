# Current Status

Last updated: 2026-07-26

## Completed

| Area | Detail |
| --- | --- |
| IAM schema | Users, identities, sessions, visitors, roles, permissions, role_permissions, auth_events |
| Models | SQLAlchemy models for IAM + files + folders + outbox |
| Visitor flow | Register visitor, guest JWT issuance, `last_seen_at` updates on auth |
| User registration | `POST /auth/register/me` — create user + identity, link visitor, create session, return tokens |
| User login | `POST /auth/login/me` — verify credentials, link visitor, create session, return tokens |
| Token refresh | `POST /auth/refresh` — validate session + refresh hash, rotate tokens |
| Logout | `POST /auth/logout` — revoke current session |
| Logout all devices | `POST /auth/logout/all` — revoke all user sessions |
| Auth events | Persisted on login, registration, login failure, session create, logout, session revoke |
| Auth event API | `GET /auth/events` — list events for current user |
| Session persistence | Refresh token SHA-256 hash stored in `sessions`; `session_id` claim in access/refresh JWTs |
| JWT utilities | Guest, access, and refresh token generation + verification |
| Auth middleware | Guest/access/refresh dependencies; access checks active session; updates `last_seen_at` |
| RBAC APIs | CRUD for roles, permissions, role-permission assignments; `GET /rbac/me/permissions` |
| Visitor service | CRUD helpers, link visitor to user, touch `last_seen_at` |
| Identity service | Lookup by identifier, create identity, login success/failure tracking |
| API schemas | One schema file per endpoint under `schemas/endpoints/` |
| Storage | S3 integration, presigned PUT upload, mark-upload-complete |
| Folders | Create folder, list by owner / parent |
| Infrastructure | Docker Compose for Postgres + Redis |
| Route authentication | Access JWT on users, files, folders, visitor list, rbac; public: `POST /visitor/` + auth bootstrap |

## In progress

| Area | Detail |
| --- | --- |
| Password security | Credentials stored/compared as plain text; password hashing still needed |
| RBAC enforcement | APIs exist; route-level permission checks not wired yet |
| OAuth providers | `IdentityProvider.GOOGLE` / `GITHUB` enum exists; flows not implemented |
| Resource activity timeline | File/folder activity not implemented |
| Identity router | `endpoints/identity.py` exists but is not mounted on `api_router` |

## Planned next (Phase 1 finish)

1. Password hashing (bcrypt/argon2) and credential verification hardening
2. RBAC permission middleware (fine-grained checks beyond access JWT)
3. File download, list, delete
4. Activity timeline for files/folders
5. Basic filename search
6. Admin-only guard on RBAC mutation endpoints

## Code map

```
app/
├── api/v1/endpoints/   auth, rbac, visitor, users, folders, files, identity (unmounted)
├── middleware/         authenticate() + session validation + last_seen tracking
├── models/             files, folders, outbox
├── models/iam/         user, identity, session, visitor, role, permission, auth_events
├── services/
│   ├── iam/            visitors, visitor_jwt, identity, identity_user_visitor,
│   │                   session, auth_session, auth_event, rbac
│   ├── utils/          jwt
│   ├── files.py        S3 presigned uploads
│   └── folder.py       folder CRUD
├── schemas/
│   ├── endpoints/      auth, rbac, visitor, users, files, folders, identity
│   └── iam/            domain DTOs (roles, sessions, etc.)
└── core/               database, security (refresh token hashing)
```

See [milestones.md](milestones.md) for phase goals and [backlog.md](backlog.md) for the full planned list.
