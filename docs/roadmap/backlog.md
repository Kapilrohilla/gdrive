# Backlog

Work not yet started, grouped by domain. See [current-status.md](current-status.md) for completed and in-progress items.

## Next up

- [ ] **Sharing of file** — share files with users, permission levels, shared links

## Storage

- [x] File download (presigned GET)
- [x] File list API
- [x] File preview (presigned inline GET)
- [x] Thumbnail outbox event on upload (`generate_file_thumbnail`)
- [ ] Thumbnail generation worker
- [ ] File delete API
- [ ] File versioning
- [ ] Trash / soft delete
- [ ] Restore from trash
- [ ] Bulk operations (move, delete, download)
- [ ] Metadata extraction on upload
- [ ] Basic filename search
- [x] Protect file/folder routes with RBAC permission checks

## IAM & security

- [ ] Password hashing (replace plain-text credential storage)
- [x] RBAC enforcement middleware (check permissions on routes)
- [ ] Admin-only guard on RBAC mutation endpoints
- [ ] OAuth flows (Google, GitHub)
- [ ] Password reset / email verification / OTP flows
- [ ] Mount identity health/router on API router
- [ ] Rate limiting on auth endpoints
- [ ] Failed login lockout (`locked_until` on identity)

## Activity

- [x] Resource activity timeline for files (view/download events via outbox)
- [ ] Folder activity timeline
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

## Short URLs

- [x] Shorten URL
- [x] List user's short URLs
- [x] Public redirect

## Documentation

- [ ] Architecture docs (`architecture/`)
- [ ] API reference docs (`api/`)
- [ ] ADRs (`decisions/`)
