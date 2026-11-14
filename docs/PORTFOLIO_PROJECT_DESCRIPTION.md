# Mol-Tol AI — portfolio description

## CV-ready project entry

**Mol-Tol AI — Policy-First Negotiation Infrastructure (prototype)**
Designed and implemented a FastAPI negotiation service, a dependency-light Python HTTP SDK, and a Next.js developer console for bounded buyer/seller agent workflows. The prototype enforces server-side authorization and negotiation policies, supports separate USD and PKR integer-minor-unit accounting, records tenant-scoped audit events, and produces SHA-256 agreement fingerprints that can be independently recomputed for content consistency. Added automated API, policy, privacy, idempotency, concurrency, SDK, provider-failure, and evaluation tests.

**Status and limits:** Deterministic workflows are implemented and tested locally. Real LLM inference has not been verified (`inference_count: 0`); all strategy comparisons are synthetic fixtures. The service has not received an independent security audit and has no externally validated customers, revenue, or production deployment.

## Short public description

Mol-Tol explores a policy-authoritative boundary for software agents negotiating structured commercial terms. Its Python SDK talks to a typed HTTP API; the server validates offers and state transitions before an agreement can be finalized. The current local prototype supports USD and PKR without currency conversion, tenant-scoped API keys, and recomputable agreement fingerprints. Real model inference, production security, and commercial validation remain pending.

## Skills demonstrated

- Python/FastAPI domain and API design
- TypeScript/Next.js responsive developer console
- Python SDK packaging and HTTP integration
- Integer-safe monetary representation and ISO currency separation
- Authorization, tenant isolation, idempotency and audit design
- Automated testing for policy boundaries and failure handling
