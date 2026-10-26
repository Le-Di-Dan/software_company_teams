---
name: kb-web-admin
description: Add-on rules for the admin surface (back office that operates the product) - roles, server-side authorization, audit log, PII masking, the admin UI bar and role-based tests. Read on top of kb-web-frontend when a web surface is an admin console.
user-invocable: false
---

# Admin surface (back office)

The admin console is how the PO's team runs the product: content, users and support, moderation, subscription lookup, push campaigns, feature flags, reports. It is another client of the same backend, never a second backend. Everything in `kb-web-frontend` applies; this adds what is specific to operators. Code in `apps/web/admin/`, E2E in `tests/web-e2e/admin/`.

## Roles and authorization
- Roles and a permissions matrix come from `docs/05-architecture/` (e.g. owner, editor, support, moderator). No self-sign-up to admin; an owner grants roles; the first owner account is created by a documented script, not by the UI.
- Every admin action is authorized on the backend (admin endpoints under their own prefix, or RLS/Rules policies on an admin role). A hidden button is not a permission.
- MFA for admin accounts when the identity provider supports it (Supabase Auth TOTP; Firebase needs the Identity Platform upgrade, so check the cost with the PO). Re-authentication before destructive actions.
- Privileged work (refunds, deleting users, sending pushes) runs in backend endpoints or functions that check the caller's role; the browser never holds service-role or Admin SDK credentials.

## Audit and data protection
- Every write is audited server-side: who, what, target id, before/after summary, when, IP/user agent; the record's audit trail is visible in the console.
- PII masked by default (email, phone); reveal and export are role-gated and audited.
- `noindex` (robots meta + `X-Robots-Tag`), `frame-ancestors 'none'`.

## Admin UI bar (on top of `kb-web-ui-bar`)
- [ ] Shell: sidebar grouped by job, environment badge (DEV / STAGING / PROD in distinct colors), signed-in user and role.
- [ ] Desktop-first (1280–1920 px), usable at 1024 px; denser spacing scale than the product, same brand.
- [ ] Data tables: server-side pagination, sort and filters kept in the URL, column visibility, sticky header, row actions, bulk select with a count, skeleton rows, numbers right-aligned, dates in the operator's time zone with the zone shown.
- [ ] Detail pages: summary header, tabs for related data, audit trail.
- [ ] Destructive and bulk actions: confirmation naming the object and the consequence; undo where cheap.
- [ ] Keyboard: every action reachable, `Esc` closes dialogs, focus returns to the trigger.

## Tests
Seeded accounts per role. For every privileged action: one spec where the allowed role succeeds and one where a lower role is refused by the server (not just by the UI).
