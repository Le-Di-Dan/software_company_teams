---
name: kb-nodejs
description: Node.js backend team conventions - TypeScript service layout, framework choices, validation, Postgres access and migrations, testing with Vitest/Jest and Testcontainers or docker-compose, Docker image and pitfalls.
user-invocable: false
---

# Node.js (TypeScript) backend conventions

## Setup
- Current Node LTS; TypeScript strict; ESM. Package manager per architecture (pnpm or npm), lockfile committed.
- `services/api/`: `src/modules/<domain>/{routes,service,repo,schemas}`, `src/lib`, `src/config`, `test/`, `migrations/`, `Dockerfile`, `openapi.yaml` (or generated from schemas).

## Patterns
- Framework: Fastify (default, schema-first, fast) or NestJS for large domain models — per ADR.
- Validation: zod / TypeBox schemas shared with OpenAPI generation; reject unknown fields.
- DB: Postgres with Prisma or Drizzle; migrations via the ORM's migrate tooling; transactions for multi-step writes.
- Auth: verify JWTs from the identity provider (Firebase/Supabase/own) on every request; authorization in the service layer.
- Background jobs: BullMQ (Redis) or pg-boss if needed.
- Logging: pino structured logs with request id.

## Quality commands
- `npx tsc --noEmit`, `npx eslint .`, `npx vitest run` (unit + integration with docker-compose Postgres), contract tests against `openapi.yaml`, `npm audit --omit=dev`.

## Pitfalls
- Unhandled promise rejections; always await and handle errors centrally.
- Connection pool exhaustion in serverless; size pools per hosting.
- Don't block the event loop with CPU-heavy work (use worker threads or a job).
