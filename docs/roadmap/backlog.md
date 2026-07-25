# Backlog

Work not yet started, grouped by domain. See [current-status.md](current-status.md) for completed and in-progress items.

## Storage

- [ ] File download (presigned GET)
- [ ] File list / delete APIs
- [ ] File versioning
- [ ] Trash / soft delete
- [ ] Restore from trash
- [ ] Bulk operations (move, delete, download)
- [ ] Metadata extraction on upload
- [ ] Basic filename search
- [ ] Thumbnails / previews
- [ ] Protect file/folder routes with RBAC permission checks (access JWT already required)

## IAM & security

- [ ] Password hashing (replace plain-text credential storage)
- [ ] RBAC enforcement middleware (check permissions on routes)
- [ ] Admin-only guard on RBAC mutation endpoints
- [ ] OAuth flows (Google, GitHub)
- [ ] Password reset / email verification / OTP flows
- [ ] Mount identity health/router on API router
- [ ] Rate limiting on auth endpoints
- [ ] Failed login lockout (`locked_until` on identity)

## Activity

- [ ] Resource activity timeline (create, update, share, delete)
- [ ] Audit log query APIs for non-auth resources

## Collaboration (Phase 2)

- [ ] File / folder sharing
- [ ] Permission inheritance
- [ ] Shared links
- [ ] Password-protected links
- [ ] Expiring links
- [ ] Shared workspaces
- [ ] Notifications

## Search (Phase 3)

- [ ] Full-text search
- [ ] OCR pipeline
- [ ] Metadata indexing
- [ ] Semantic search
- [ ] Duplicate detection
- [ ] Similar image search

## AI (Phase 4–5)

- [ ] Consent management for AI features
- [ ] Image understanding / tagging
- [ ] AI albums
- [ ] AI videos
- [ ] Document summarization
- [ ] Global knowledge search / Q&A
- [ ] Cascading erasure of embeddings, OCR, summaries on delete

## Documentation

- [ ] Architecture docs (`architecture/`)
- [ ] API reference docs (`api/`)
- [ ] ADRs (`decisions/`)
