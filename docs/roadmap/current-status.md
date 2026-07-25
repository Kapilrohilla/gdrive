# Current Status

Last updated: 2026-07-26

## Completed

| Area | Detail |
| --- | --- |
| IAM schema | Users, identities, sessions, visitors, roles, permissions, role_permissions, auth_events |
| Models | SQLAlchemy models for IAM + files + folders + outbox |
| Visitor flow | Register visitor, guest JWT issuance, `last_seen_at` updates on auth |
| User registration | `POST /auth/register/me` — create user + identity, link visitor, return tokens |
| User login | `POST /auth/login/me` — verify credentials, link visitor, update `last_login_at` |
| JWT utilities | Guest, access, and refresh token generation + verification |
| Auth middleware | FastAPI dependencies for guest/access/refresh; sets `request.state` claims |
| Visitor service | CRUD helpers, link visitor to user, touch `last_seen_at` |
| Identity service | Lookup by identifier, create identity, login success/failure tracking |
| API schemas | One schema file per endpoint under `schemas/endpoints/` |
| Storage | S3 integration, presigned PUT upload, mark-upload-complete |
| Folders | Create folder, list by owner / parent |
| Infrastructure | Docker Compose for Postgres + Redis |
| Mock drive API | `/drive/*` endpoints for frontend development |

## In progress

| Area | Detail |
| --- | --- |
| Password security | Credentials stored/compared as plain text; `core/security.py` is a stub — needs hashing |
| Refresh token rotation | Session model stores `refresh_token_hash`; rotation + `/auth/refresh` endpoint TBD |
| Logout | Session revocation not implemented |
| RBAC middleware | Roles/permissions modeled; enforcement on routes not wired |
| OAuth providers | `IdentityProvider.GOOGLE` / `GITHUB` enum exists; flows not implemented |
| Activity timeline | Auth events modeled; resource activity still TBD |
| Identity router | `endpoints/identity.py` exists but is not mounted on `api_router` |

## Planned next (Phase 1 finish)

1. Password hashing (bcrypt/argon2) and credential verification hardening
2. Refresh + logout endpoints with session persistence
3. Apply `authenticate(TokenType.ACCESS)` to storage routes (files, folders)
4. RBAC middleware on protected resources
5. File download, list, delete
6. Activity timeline for files/folders
7. Basic filename search

## Code map

```
app/
├── api/v1/endpoints/   auth, visitor, users, folders, files, drive, identity (unmounted)
├── middleware/         authenticate() dependencies + visitor last_seen_at
├── models/             files, folders, outbox
├── models/iam/         user, identity, session, visitor, role, permission, auth_events
├── services/
│   ├── iam/            visitors, visitor_jwt, identity, identity_user_visitor, user
│   ├── utils/          jwt
│   ├── files.py        S3 presigned uploads
│   └── folder.py       folder CRUD
├── schemas/
│   ├── endpoints/      auth, visitor, users, files, folders, drive, identity
│   └── iam/            domain DTOs (roles, sessions, etc.)
└── core/               database, security (stub)
```

See [milestones.md](milestones.md) for phase goals and [backlog.md](backlog.md) for the full planned list.
