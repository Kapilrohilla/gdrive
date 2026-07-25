# Milestones

## Phase 1 — Secure Storage Platform

**Goal:** Production-ready cloud storage foundation.

| Feature | Status |
| --- | --- |
| Visitor management | Done — register, guest JWT, last_seen tracking |
| User registration | Done — guest-gated `/auth/register/me` |
| User login | Done — guest-gated `/auth/login/me` |
| JWT (guest / access / refresh) | Done — generation + verify |
| Auth middleware | Done — FastAPI dependencies; RBAC TBD |
| Session management | Done — DB sessions, refresh rotation, logout + logout all |
| Password security | Not started — hashing required before production |
| File upload | Done — presigned PUT |
| File download | Planned |
| Folder hierarchy | Done (basic) |
| Metadata extraction | Planned |
| S3 object storage | Done |
| Presigned uploads | Done |
| File management | Partial — upload only |
| Folder management | Partial — create + list |
| Basic filename search | Planned |
| RBAC | Partial — management APIs done; route enforcement TBD |
| Auth events | Done — persisted during auth flows; `GET /auth/events` |
| Activity timeline | Partial — auth events only; resource activity planned |
| Secure APIs | Partial — auth routes protected; storage routes open |

## Phase 2 — Collaboration

**Goal:** Secure collaboration between users.

- File and folder sharing
- Viewer / Editor / Owner permissions
- Permission management
- Shared links (password-protected, expiring)
- Shared workspaces
- Notifications

## Phase 3 — Intelligent Search

**Goal:** Transform storage into searchable knowledge.

- OCR
- Metadata indexing
- Full-text search
- Semantic / natural language search
- Duplicate detection
- Similar image search
- Smart filtering

**Example queries**

- "Show invoices from 2025."
- "Find my passport."
- "Show receipts related to travel."

## Phase 4 — AI Media Intelligence

**Goal:** Google Photos–like experiences with privacy controls.

- Smart photo albums
- Face grouping (optional, consent-gated)
- Object / scene detection
- Automatic image tagging
- AI-generated collages
- Memory highlights
- AI-generated videos from albums

## Phase 5 — Personal Knowledge Platform

**Goal:** Turn stored content into a searchable knowledge base.

- AI document summaries
- Cross-document search
- Question answering
- Smart recommendations
- Content relationships / knowledge graph
- AI assistant

**Example queries**

- "Summarize my insurance documents."
- "Compare these contracts."
- "Show every document mentioning New Relic."
