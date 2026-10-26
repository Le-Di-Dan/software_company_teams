---
name: kb-backend-common
description: Rules shared by all backend and BaaS teams - API contract first, auth and authorization, data and migrations, AI proxy, observability, cost control and local testing.
user-invocable: false
---

# Backend common rules

## Contract first
- The source of truth is `docs/05-architecture/api-contract/` (OpenAPI 3.1 for servers; schema + rules/policies for BaaS). Change the contract via the architect, then code.
- Versioned API (`/v1`). Consistent error shape: `{ "error": { "code": "snake_case", "message": "human readable", "details": {} } }`. Pagination for list endpoints. Idempotency keys for payment-like operations.

## Security
- Authenticate every non-public endpoint; authorize per resource (users only touch their own data). Deny by default.
- Validate all input at the boundary (schema validation). Parameterized queries only.
- Rate limit per user and per IP; stricter for expensive endpoints (AI, uploads, auth).
- Secrets from environment variables; `.env.example` lists names only.
- Account deletion endpoint deletes user data across all stores (DB, storage, analytics where possible) and is tested.

## AI proxy (if the app uses AI)
- Mobile apps never hold provider keys. The backend/BaaS function calls the AI provider with: auth check, per-user quota, timeout, retries with backoff, streaming if the UX needs it, response validation against the JSON schema, logging of usage (tokens, cost) without PII, and a feature flag / kill switch. Follow `docs/05-architecture/ai-architecture.md`.

## Data
- Migrations are versioned and reversible where possible; never edit an applied migration.
- Timestamps in UTC; IDs as UUID/ULID; soft-delete only when the product needs it (account deletion must hard-delete or anonymize per the privacy policy).

## Observability & cost
- Structured logs (JSON) with request id; health endpoint; error tracking.
- Estimate cost per active user (requests, reads/writes, storage, AI tokens) for every new feature and note it in the hand-off.

## Local testing
- Everything runs locally: Docker (Postgres, Redis…) or the Firebase Emulator Suite / Supabase local stack. Integration tests run against them, never against production.
- Production deploys, project creation and billing changes are PO-only.
