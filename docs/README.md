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
├── README.md                          ← you are here
├── architecture/                      System design & domain docs
├── roadmap/                           Vision, milestones, backlog, status
├── decisions/                         Architecture Decision Records (ADRs)
├── api/                               API reference by domain
└── diagrams/                          Visual flows (draw.io)
```

### Architecture

| Doc | Description |
| --- | --- |
| [overview.md](architecture/overview.md) | High-level system overview |
| [system-design.md](architecture/system-design.md) | Service boundaries and data flow |
| [database-schema.md](architecture/database-schema.md) | IAM, storage, and shared models |
| [authentication.md](architecture/authentication.md) | Visitors, identities, sessions, JWT |
| [authorization-rbac.md](architecture/authorization-rbac.md) | Roles, permissions, enforcement |
| [storage.md](architecture/storage.md) | Files, folders, S3, uploads |
| [sharing.md](architecture/sharing.md) | Collaboration (Phase 2) |
| [search.md](architecture/search.md) | Search & indexing (Phase 3) |
| [ai-architecture.md](architecture/ai-architecture.md) | AI services & consent (Phase 4–5) |
| [security-dpdp.md](architecture/security-dpdp.md) | Security & DPDP compliance |

### Roadmap

| Doc | Description |
| --- | --- |
| [vision.md](roadmap/vision.md) | Product vision and long-term goal |
| [milestones.md](roadmap/milestones.md) | Phase 1–5 milestones |
| [backlog.md](roadmap/backlog.md) | Planned work by domain |
| [current-status.md](roadmap/current-status.md) | Completed / in progress / next |

### Decisions

| ADR | Topic |
| --- | --- |
| [ADR-001](decisions/ADR-001-authentication.md) | Authentication model |
| [ADR-002](decisions/ADR-002-storage-engine.md) | Object storage engine |
| [ADR-003](decisions/ADR-003-file-versioning.md) | File versioning |
| [ADR-004](decisions/ADR-004-ai-indexing.md) | AI indexing & consent |

### API

| Doc | Description |
| --- | --- |
| [authentication.md](api/authentication.md) | Auth & visitor endpoints |
| [files.md](api/files.md) | File upload & management |
| [folders.md](api/folders.md) | Folder hierarchy |
| [sharing.md](api/sharing.md) | Sharing (planned) |
| [search.md](api/search.md) | Search (planned) |

## Stack (current)

- **API:** FastAPI (`CloudDrive API`)
- **DB:** PostgreSQL + SQLAlchemy async
- **Object storage:** AWS S3 (presigned uploads)
- **Auth design:** JWT + refresh sessions (implementation in progress)

## Long-term goal

Evolve from secure cloud storage into a **privacy-first personal intelligence platform** — store, organize, share, search, and interact with personal content using AI, with full data ownership and DPDP compliance.
