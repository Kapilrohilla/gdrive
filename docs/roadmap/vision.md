# Vision

Build a platform where users can:

- Securely store files and folders
- Organize and manage digital assets
- Share files and folders with fine-grained permissions
- View a complete activity timeline for every resource
- Search across personal content using AI
- Automatically organize photos and documents
- Generate AI-powered insights and media while keeping data private and DPDP-compliant

## From storage to intelligence

| Stage | Focus | Current state |
| --- | --- | --- |
| Phase 1 | Secure storage platform | In progress — auth + upload foundation built |
| Phase 2 | Collaboration & sharing | Not started |
| Phase 3 | Intelligent / semantic search | Not started |
| Phase 4 | AI media intelligence | Not started |
| Phase 5 | Personal knowledge platform | Not started |

Although the initial implementation focuses on cloud storage, the long-term vision extends beyond a traditional Drive clone into a **privacy-first personal knowledge platform** powered by AI.

## Core principles

### Security first

- Secure authentication and authorization
- Principle of least privilege
- Encryption in transit and at rest
- Session management
- Role-Based Access Control (RBAC)

### Privacy first

Every feature follows **Privacy by Design**:

- Collect only necessary information
- Require explicit consent before AI processing
- Allow complete data deletion
- Never use customer data for model training without consent
- Maintain strong logical isolation between users

### AI as an enhancement

AI enhances productivity; it does not replace core functionality. The storage platform must remain fully functional if AI services are unavailable.

## Current implementation focus (Phase 1)

The backend is building the IAM and storage foundation:

1. **Anonymous visitors** — device/browser identity with guest JWT
2. **Registered users** — identity-linked accounts (email/phone/username) with access + refresh tokens
3. **Object storage** — S3 presigned uploads with folder hierarchy
4. **Session lifecycle** — refresh rotation, single logout, logout all devices
5. **Next** — password hashing, RBAC on storage routes, file lifecycle APIs

See [current-status.md](current-status.md) for the live checklist.

## Long-term goal

Evolve into a privacy-first personal intelligence platform where users securely store, organize, share, search, and interact with digital content using AI — retaining complete ownership and remaining fully compliant with the Digital Personal Data Protection (DPDP) Act.
