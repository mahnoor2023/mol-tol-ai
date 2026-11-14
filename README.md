# Mol-Tol AI

**A policy-first negotiation infrastructure prototype for software agents.**

Mol-Tol explores a reusable HTTP boundary for buyer and seller software agents. The API validates actors, offer terms and state transitions under server-owned business policy before allowing an agreement to be finalized. A small Python SDK demonstrates how an external server-side application can use that API.

## Portfolio highlights

- FastAPI negotiation API with strict request validation and structured errors
- Dependency-light Python SDK and synthetic API-key integration example
- Separate buyer and seller policy limits, enforced by the server
- USD and PKR sessions using integer minor units and no exchange-rate conversion
- Tenant-scoped API keys, scopes, expiration, rotation, rate limits and audit records in the local prototype
- Idempotent agreement finalization and SHA-256 content-fingerprint verification
- The separate local prototype includes a Next.js developer console with negotiation timeline and deterministic strategy provenance
- Automated tests for authorization, privacy, state boundaries, concurrency and proof checks

## Status

This repository is a local prototype, not a hosted service. Deterministic negotiation workflows have been tested locally. **Real LLM inference has not been verified** (`inference_count: 0`); strategy evaluations use synthetic fixtures. No independent security audit, external customer validation, commercial result, live payment, or production deployment is claimed.

This candidate contains the SDK, API contract, portfolio text, and static marketing page. It does not include a hosted negotiation API or interactive fixture dashboard. See the SDK [quickstart](packages/python-sdk/docs/SDK_QUICKSTART.md), [API contract](packages/python-sdk/docs/API_CONTRACT.md), and [portfolio description](docs/PORTFOLIO_PROJECT_DESCRIPTION.md).

## Authentication and data

Use tenant API keys only in trusted server-side applications and only after an API operator provisions a compatible endpoint and scoped credentials. Never place them in browser or mobile bundles. The current browser demo uses public fixture identities and is local-loopback-only; it is not a hosted demo or production authentication system.

## License and release

The current project license reserves all rights. Public redistribution or reuse rights have not been granted. A public release requires the owner to approve the exact repository content and license terms. No hosted API or native Android application is included.
