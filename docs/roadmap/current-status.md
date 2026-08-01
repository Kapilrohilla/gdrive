# Current Status

Last updated: 2026-08-01

## Completed

| Area | Detail |
| --- | --- |
| IAM schema | Users, identities, sessions, visitors, roles, permissions, role_permissions, auth_events |
| Models | SQLAlchemy models for IAM + files + folders + outbox + resource_events + short_urls |
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
| RBAC enforcement | Route-level permission checks on files, folders, users via `require_permission` |
| Visitor service | CRUD helpers, link visitor to user, touch `last_seen_at` |
| Identity service | Lookup by identifier, create identity, login success/failure tracking |
| API schemas | One schema file per endpoint under `schemas/endpoints/` |
| Storage | S3 integration, presigned PUT upload, mark-upload-complete |
| File APIs | List, get, preview (presigned inline GET), download (presigned attachment GET) |
| File activity | `GET /files/{id}/activity` — resource event timeline per file |
| Resource events | Outbox-driven event creation on file view/download; `resource_events` model |
| Thumbnail outbox | On successful upload, emits `generate_file_thumbnail` outbox event with file metadata |
| Short URLs | Shorten, list, and public redirect at `/s/*` |
| Folders | Create folder, list by owner / parent |
| Infrastructure | Docker Compose for Postgres + Redis |
| Route authentication | Access JWT on users, files, folders, visitor list, rbac; public: `POST /visitor/` + auth bootstrap |

## In progress

| Area | Detail |
| --- | --- |
| Password security | Credentials stored/compared as plain text; password hashing still needed |
| Outbox worker | Pooler exists; thumbnail generation consumer not implemented |
| OAuth providers | `IdentityProvider.GOOGLE` / `GITHUB` enum exists; flows not implemented |
| Identity router | `endpoints/identity.py` exists but is not mounted on `api_router` |

## Planned next

1. **Sharing of file** — share files with other users, shared links
2. Password hashing (bcrypt/argon2) and credential verification hardening
3. File delete / trash / soft delete
4. Thumbnail generation worker (consume `generate_file_thumbnail` outbox events)
5. Basic filename search
6. Admin-only guard on RBAC mutation endpoints

## Code map

```
app/
├── api/v1/endpoints/   auth, rbac, visitor, users, folders, files, short_url, identity (unmounted)
├── middleware/         authenticate() + require_permission + session validation
├── models/             files, folders, outbox, resource_events, short_urls
├── models/iam/         user, identity, session, visitor, role, permission, auth_events
├── services/
│   ├── drive/            files, folder, file_resource_event
│   ├── iam/              visitors, visitor_jwt, identity, identity_user_visitor,
│   │                     session, auth_session, auth_event, rbac
│   ├── utils/            jwt, outbox, encoding
│   ├── resource_events.py
│   └── short_urls.py
├── schemas/
│   ├── endpoints/      auth, rbac, visitor, users, files, folders, short_url, identity
│   └── iam/            domain DTOs (roles, sessions, etc.)
└── core/               database, queue/pooler, security (refresh token hashing)
```

See [milestones.md](milestones.md) for phase goals and [backlog.md](backlog.md) for the full planned list.
