---
name: kb-go
description: Go backend team conventions - service layout, net/http or chi, sqlc/pgx with Postgres, migrations, context and error handling, table-driven tests with race detector, Docker and pitfalls.
user-invocable: false
---

# Go backend conventions

## Setup
- Current stable Go (the Mac has Go installed; check `go version` and upgrade the module's `go` directive only via ADR). Modules committed with `go.sum`.
- `services/api/`: `cmd/api/main.go`, `internal/<domain>/{handler,service,repository}`, `internal/platform/{config,db,log,auth}`, `migrations/`, `sql/queries/` (sqlc), `api/openapi.yaml`, `Dockerfile` (multi-stage, distroless).

## Patterns
- HTTP: standard `net/http` (ServeMux with method patterns) or chi; middleware for auth, request id, recovery, rate limit.
- DB: pgx + sqlc generated queries; migrations with goose or golang-migrate.
- Errors: wrap with `%w`, map domain errors to the API error shape at the handler boundary.
- Context: pass `context.Context` everywhere; timeouts on outbound calls.
- Config from env; structured logging with `log/slog`.
- Optional: oapi-codegen to generate server interfaces from the contract.

## Quality commands
- `go vet ./...`, `golangci-lint run` (if installed), `go test ./... -race -count=1` (integration tests with docker-compose Postgres), `govulncheck ./...`.

## Pitfalls
- Goroutine leaks: always cancel contexts; close response bodies.
- Nil maps/pointers in JSON responses; define explicit response structs.
- Don't share `*sql.Tx` across goroutines.
