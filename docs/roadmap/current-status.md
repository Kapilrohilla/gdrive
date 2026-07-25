# Current Status

Last updated: 2026-07-25

## Completed

| Area | Detail |
| --- | --- |
| IAM schema | Users, identities, sessions, visitors, roles, permissions, role_permissions, auth_events |
| Models | SQLAlchemy models for IAM + files + folders |
| Auth architecture | Identity providers (password, magic link, OTP), session design, JWT utilities stub |
| Storage | S3 integration, presigned PUT upload, mark-upload-complete |
| Folders | Create folder, list by owner / parent |

## In progress

| Area | Detail |
| --- | --- |
| Visitor APIs | Service + endpoint exist; not yet mounted on the API router |
| Refresh token rotation | Session model stores `refresh_token_hash`; rotation logic TBD |
| Auth middleware | Protect routes with validated sessions / JWT |
| RBAC middleware | Enforce role → permission checks |
| Activity timeline | Auth events modeled; resource activity still TBD |

## Planned next (Phase 1 finish)

1. Complete authentication flows (register, login, refresh, logout)
2. Mount and harden visitor endpoints
3. Auth + RBAC middleware on storage routes
4. File download, list, delete
5. Activity timeline for files/folders
6. Basic filename search

## Code map (today)

```
app/
├── api/v1/endpoints/   auth, users, folders, files, drive, visitor
├── models/             files, folders
├── models/iam/         user, identity, session, visitor, role, permission, auth_events
├── services/           files, folder, user, iam/visitors
├── schemas/            request/response DTOs
└── core/               database, security
```

See [milestones.md](milestones.md) for phase goals and [backlog.md](backlog.md) for the full planned list.
