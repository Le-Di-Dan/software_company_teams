---
name: kb-supabase
description: Supabase team conventions - local stack with the Supabase CLI, Postgres schema and migrations, Row Level Security with tests, Auth, Storage policies, Edge Functions in Deno/TypeScript, Realtime, and free-tier limits.
user-invocable: false
---

# Supabase conventions

## Setup
- `services/baas/supabase/` created by `npx supabase init`: `config.toml`, `migrations/`, `seed.sql`, `functions/<name>/index.ts`, `tests/` (pgTAP database tests).
- Local stack via `npx supabase start` (requires Docker). Linking to remote projects uses project refs provided by the PO; production pushes are PO-only.
- Free tier projects pause when inactive and have quotas — check current limits on supabase.com/pricing and tell the director when the app will need a paid plan.

## Schema & RLS
- All changes via migrations (`npx supabase migration new <name>`); never edit applied migrations.
- Enable RLS on every table in exposed schemas; policies per operation (select/insert/update/delete) using `auth.uid()`; least privilege; avoid `security definer` functions unless reviewed.
- pgTAP tests for allowed and denied access per policy (`npx supabase test db`).
- Indexes for every foreign key and frequent filter; use `check` constraints for data validity.

## Auth & Storage
- Auth providers per architecture (Sign in with Apple on iOS when other social logins exist); deep-link redirect URLs per platform.
- Storage buckets private by default with policies tied to `auth.uid()`.

## Edge Functions
- Deno + TypeScript; verify JWT; secrets via `npx supabase secrets set` (names in `docs/05-architecture/secrets.md`); AI proxy pattern from `kb-backend-common`.
- Never expose the `service_role` key to clients or commit it.

## Commands
- `npx supabase db reset` (apply migrations + seed locally), `npx supabase test db`, `npx supabase functions serve`, generate types: `npx supabase gen types typescript --local`.
