# Public negotiation API contract (prototype)

This contract describes the SDK-facing HTTP shape. It does not mean a hosted Mol-Tol endpoint is available. The service operator must provision the URL, tenants, per-currency policies and scoped keys.

## Authentication and tenant model

Send `X-API-Key` from a trusted server-side client. Never expose tenant keys in browser code or mobile bundles. The buyer key creates the session and must have `negotiations:write`; the seller key must have `offers:submit` to counter or accept. Finalization uses buyer-side `agreements:finalize`; reads/proof checks use `negotiations:read`; audit reads use `audit:read`. Operators configure policy and credentials outside the public SDK example.

## Negotiation resources

| Method and path | Purpose | Expected permission |
|---|---|---|
| `POST /negotiations` | Create a session. Buyer API-key requests identify a distinct `seller_tenant_id`; both tenants need policies for the chosen currency. | Buyer `negotiations:write` |
| `GET /negotiations/{session_id}` | Read the caller tenant's public view; cross-tenant identifiers are not disclosed. | `negotiations:read` |
| `POST /negotiations/{session_id}/offers` | Submit `{ "amount_minor": 9000, "currency": "USD", "quantity": 1 }`. | Party `offers:submit` |
| `POST /negotiations/{session_id}/counteroffer` | Request a deterministic counteroffer within server policy. | Seller `offers:submit` |
| `POST /negotiations/{session_id}/finalize` | Finalize mutually accepted terms with an `Idempotency-Key` header. | Buyer `agreements:finalize` |
| `POST /proof/verify` | Submit `{ "session_id": "…", "proof": { … } }` and receive `{ "valid": true/false }`. | `negotiations:read` on that session |
| `GET /negotiations/{session_id}/audit` | Read that session's audit events. | `audit:read` |

## Create request fields

`buyer_id`, `buyer_name`, `seller_id`, `seller_name`, `product_id`, `product_name`, positive integer `quantity`, `currency` (`USD` or `PKR`), non-negative integer `opening_offer_minor`, and optional `max_rounds` (bounded by the service). Tenant-authenticated creation additionally needs `seller_tenant_id`. Unknown request fields are rejected. The public view omits private buyer maximum and seller minimum values.

## Money and proof

USD and PKR each use 100 minor units per major unit. The session's currency and quantity are fixed. No exchange conversion is performed. The final proof includes canonical terms, policy-version reference, authorized approval records and a SHA-256 fingerprint. Fingerprint recomputation verifies content consistency only; it is not a signature, identity proof or tamper-proof storage.

## Errors

Responses use structured JSON with a stable `code` and a `detail` when available. Clients should handle authentication (401), forbidden scope/actor (403), unknown or inaccessible resource (404), state/policy conflict (409), invalid schema (422), rate limiting (429, with optional `Retry-After`) and transport failures. Never retry finalization without reusing the same idempotency key.

There are no live payments in this prototype. API behavior, schemas, scopes and limits can change before any hosted beta; consult the operator's deployed OpenAPI document for the authoritative version.
