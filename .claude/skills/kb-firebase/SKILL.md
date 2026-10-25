---
name: kb-firebase
description: Firebase team conventions - project layout, Firestore data modeling, Security Rules with emulator tests, Cloud Functions in TypeScript, Auth, Storage, FCM, App Check, cost control and plan limits.
user-invocable: false
---

# Firebase conventions

## Setup
- `services/baas/firebase/`: `firebase.json`, `.firebaserc` (project aliases dev/staging/prod — ids provided by the PO), `firestore.rules`, `firestore.indexes.json`, `storage.rules`, `functions/` (TypeScript, Node LTS), `tests/` (rules tests with `@firebase/rules-unit-testing`).
- Firebase CLI via `npx firebase-tools` (no global install needed). Local development and tests on the **Emulator Suite** only.
- Cloud Functions and some features require the pay-as-you-go (Blaze) plan; enabling billing is a PO decision — flag it early with cost estimates.

## Data modeling (Firestore)
- Model for queries: denormalize read paths, keep documents < 1 MiB, avoid unbounded arrays, use subcollections for per-user data (`users/{uid}/...`).
- Every query needs an index plan; avoid hot-spot sequential IDs on high-write collections.

## Security Rules
- Deny by default; `request.auth != null` and ownership checks (`request.auth.uid == userId`); validate field types/sizes on writes.
- Tests for allowed *and* denied cases for every rule.

## Functions
- Callable/HTTPS functions with App Check + auth checks; idempotent background triggers; secrets via `defineSecret` (Secret Manager), never in code. AI proxy pattern from `kb-backend-common`.

## Other services
- Auth providers per architecture (Sign in with Apple required on iOS if other social logins exist). FCM for push. Remote Config for feature flags/kill switches. Crashlytics/Analytics data must be in the data inventory.

## Commands
- `npx firebase-tools emulators:exec --only firestore,auth,functions,storage "npm test"`; deploy only to dev/staging with explicit `--project` alias; production deploy is PO-only.

## Cost
- Estimate reads/writes per user action; cache on the client; use aggregation queries and counters wisely.
