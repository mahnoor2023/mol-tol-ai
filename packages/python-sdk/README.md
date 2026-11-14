# Mol-Tol Python SDK

Version 0.4.0 is a standard-library HTTP client for a compatible Mol-Tol API. It does not include the API service, negotiation engine, agent implementation, or a hosted endpoint. Real LLM inference is not provided by this package.

## Install

For a normal build, `pip install .` uses the PEP 517 backend in `pyproject.toml` and requires compatible setuptools build tooling. To build offline without setuptools:

```powershell
python tools/build_wheel.py --output .\dist
python -m pip install --no-index --no-deps .\dist\mol_tol_sdk-0.4.0-py3-none-any.whl
```

The SDK has no runtime third-party dependencies and requires Python 3.12 or later.

## Authenticated request

Keep API credentials in a server-side environment variable. Do not put them in browser code or source files.

```python
import os
from mol_tol_sdk import APIError, Client

client = Client(os.environ["MOLTOL_API_URL"], os.environ["MOLTOL_API_KEY"], auth_mode="api_key")
try:
    session = client.create(
        buyer_id="procurement-agent", buyer_name="Buyer agent",
        seller_id="supplier-agent", seller_name="Seller agent",
        product_id="catalog-item", product_name="Example software plan",
        quantity=1, currency="USD", opening_offer_minor=8000,
    )
    print(session["id"], session["state"])
except APIError as exc:
    print(exc.status_code, exc.code, exc.detail)
```

See `examples/public_pilot.py` and `docs/SDK_QUICKSTART.md` for synthetic buyer/seller negotiation, finalization, proof verification and error handling.

## Behavior and boundaries

- The SDK sends structured HTTP requests. The server remains authoritative for authorization, private buyer/seller policy, party turns, currency, quantity, and state transitions.
- USD and PKR use 100 integer minor units per major unit. The SDK performs no currency conversion.
- `finalize(session_id, idempotency_key)` sends an idempotency header; `verify(proof)` asks the API to check the proof against its stored agreement.
- `APIError` exposes HTTP status, stable error code and API detail. `APIConnectionError` avoids including the URL or token in its message.
- `auth_mode="api_key"` sends `X-API-Key`. `auth_mode="demo"` is a local fixture boundary and must never be used with a public service.
- Agent orchestration and policy provisioning depend on API deployment and credential scopes. This SDK does not bypass those controls.

This is a prototype integration surface, not a production security certification or evidence of commercial validation. No public hosted API is bundled here.
