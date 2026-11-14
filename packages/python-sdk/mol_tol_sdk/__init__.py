"""Small synchronous Mol-Tol client with no runtime dependencies beyond Python."""
from __future__ import annotations

import json
import math
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlsplit
from urllib.request import Request, urlopen

SUPPORTED_CURRENCIES = frozenset({"USD", "PKR"})


def _currency_code(value: str) -> str:
    if not isinstance(value, str):
        raise ValueError("currency must be USD or PKR")
    code = value.strip().upper()
    if code not in SUPPORTED_CURRENCIES:
        raise ValueError("currency must be USD or PKR")
    return code


class APIError(RuntimeError):
    """An HTTP error returned by the Mol-Tol API."""

    def __init__(self, status_code: int, method: str, path: str, detail: Any, code: str | None = None, retry_after: str | None = None):
        self.status_code = status_code
        self.method = method
        self.path = path
        self.detail = detail
        self.code = code
        self.retry_after = retry_after
        super().__init__(f"Mol-Tol API returned HTTP {status_code} for {method} {path}: {detail}")


class APIConnectionError(RuntimeError):
    """The API could not be reached; the URL and token are not included in the message."""

    def __init__(self, method: str, path: str):
        self.method = method
        self.path = path
        super().__init__(f"Could not reach Mol-Tol API for {method} {path}")


class Client:
    """Minimal JSON/HTTP SDK. Use a production identity token outside local demos."""

    def __init__(self, base_url: str, token: str, *, timeout: float = 10.0, auth_mode: str = "demo"):
        normalized_url = base_url.strip()
        parsed = urlsplit(normalized_url)
        if (
            parsed.scheme not in ("http", "https")
            or not parsed.hostname
            or parsed.username is not None
            or parsed.password is not None
            or parsed.query
            or parsed.fragment
        ):
            raise ValueError("base_url must be an HTTP(S) URL without embedded credentials or query")
        if not isinstance(token, str) or not token.strip():
            raise ValueError("token must be a non-empty string")
        try:
            timeout = float(timeout)
        except (TypeError, ValueError) as exc:
            raise ValueError("timeout must be a positive number") from exc
        if not math.isfinite(timeout) or timeout <= 0:
            raise ValueError("timeout must be a positive number")
        if auth_mode not in ("demo", "api_key"):
            raise ValueError("auth_mode must be 'demo' or 'api_key'")
        self.base = normalized_url.rstrip("/")
        self.token = token
        self.timeout = timeout
        self.auth_mode = auth_mode
        self.auth_header = "X-API-Key" if auth_mode == "api_key" else "X-Demo-Token"

    def request(
        self,
        path: str,
        body: dict[str, Any] | None = None,
        method: str | None = None,
        headers: dict[str, str] | None = None,
    ) -> Any:
        if not path.startswith("/") or path.startswith("//"):
            raise ValueError("path must be an API path beginning with one slash")
        verb = (method or ("POST" if body is not None else "GET")).upper()
        data = None if body is None else json.dumps(body).encode("utf-8")
        request_headers = {"Accept": "application/json", "Content-Type": "application/json", self.auth_header: self.token}
        request_headers.update(headers or {})
        request = Request(self.base + path, data=data, method=verb, headers=request_headers)
        try:
            with urlopen(request, timeout=self.timeout) as response:
                return json.loads(response.read().decode("utf-8"))
        except HTTPError as exc:
            retry_after = exc.headers.get("Retry-After") if exc.headers else None
            try:
                error_body = json.loads(exc.read().decode("utf-8"))
                detail = error_body.get("detail", "request failed") if isinstance(error_body, dict) else "request failed"
                code = error_body.get("code") if isinstance(error_body, dict) else None
            except (ValueError, UnicodeDecodeError, OSError):
                detail = "request failed"
                code = None
            raise APIError(exc.code, verb, path, detail, code, retry_after) from exc
        except (URLError, TimeoutError, OSError) as exc:
            raise APIConnectionError(verb, path) from exc

    def create(self, **fields: Any) -> dict[str, Any]:
        payload = dict(fields)
        if "currency" in payload:
            payload["currency"] = _currency_code(payload["currency"])
        return self.request("/negotiations", payload)

    def offer(self, session_id: str, amount_minor: int, currency: str = "USD", quantity: int | None = None) -> dict[str, Any]:
        body: dict[str, Any] = {"amount_minor": amount_minor, "currency": _currency_code(currency)}
        if quantity is not None:
            body["quantity"] = quantity
        return self.request(f"/negotiations/{session_id}/offers", body)

    def counteroffer(self, session_id: str) -> dict[str, Any]:
        return self.request(f"/negotiations/{session_id}/counteroffer", method="POST")

    def cancel(self, session_id: str) -> dict[str, Any]:
        return self.request(f"/negotiations/{session_id}/cancel", method="POST")

    def finalize(self, session_id: str, idempotency_key: str) -> dict[str, Any]:
        return self.request(
            f"/negotiations/{session_id}/finalize",
            method="POST",
            headers={"Idempotency-Key": idempotency_key},
        )

    def get(self, session_id: str) -> dict[str, Any]:
        return self.request(f"/negotiations/{session_id}")

    def audit(self, session_id: str) -> dict[str, Any]:
        return self.request(f"/negotiations/{session_id}/audit")

    def verify(self, proof: dict[str, Any]) -> dict[str, Any]:
        session_id = proof.get("terms", {}).get("session_id") if isinstance(proof, dict) else None
        if not isinstance(session_id, str) or not session_id:
            raise ValueError("proof must contain terms.session_id")
        return self.request("/proof/verify", {"session_id": session_id, "proof": proof})

    def create_api_key(self, scopes: list[str], expires_in_seconds: int = 90 * 24 * 60 * 60) -> dict[str, Any]:
        body: dict[str, Any] = {"scopes": scopes}
        if expires_in_seconds != 90 * 24 * 60 * 60:
            body["expires_in_seconds"] = expires_in_seconds
        return self.request("/developer/api-keys", body)

    def rotate_api_key(self, key_id: str, scopes: list[str] | None = None, expires_in_seconds: int = 90 * 24 * 60 * 60) -> dict[str, Any]:
        body: dict[str, Any] = {"expires_in_seconds": expires_in_seconds}
        if scopes is not None:
            body["scopes"] = scopes
        return self.request(f"/developer/api-keys/{key_id}/rotate", body)

    def revoke_api_key(self, key_id: str) -> dict[str, Any]:
        return self.request(f"/developer/api-keys/{key_id}/revoke", method="POST")

    def set_policy(self, currency: str, *, buyer_max_minor: int | None = None, seller_min_minor: int | None = None) -> dict[str, Any]:
        body: dict[str, Any] = {"currency": _currency_code(currency)}
        if buyer_max_minor is not None: body["buyer_max_minor"] = buyer_max_minor
        if seller_min_minor is not None: body["seller_min_minor"] = seller_min_minor
        return self.request("/developer/policies", body, method="POST")

    def usage(self) -> dict[str, Any]:
        return self.request("/developer/usage")

    def security_events(self, limit: int = 100) -> dict[str, Any]:
        if type(limit) is not int or not 1 <= limit <= 200:
            raise ValueError("limit must be an integer from 1 through 200")
        return self.request(f"/developer/security-events?limit={limit}")

    def verify_security_events(self) -> dict[str, Any]:
        return self.request("/developer/security-events/verify")

    def agent_status(self) -> dict[str, Any]:
        return self.request("/agents/status")

    def run_agents(self, session_id: str, max_turns: int | None = None, *, strategy_profile: str = "baseline", remote_data_consent: bool = False) -> dict[str, Any]:
        if strategy_profile not in {"baseline", "balanced", "buyer_value", "seller_margin", "extended"}:
            raise ValueError("strategy_profile must be a supported server profile")
        if type(remote_data_consent) is not bool:
            raise ValueError("remote_data_consent must be a bool")
        params: list[str] = []
        if max_turns is not None:
            if type(max_turns) is not int or not 1 <= max_turns <= 12:
                raise ValueError("max_turns must be an integer from 1 through 12")
            params.append(f"max_turns={max_turns}")
        if strategy_profile != "baseline":
            params.append(f"strategy_profile={strategy_profile}")
        if remote_data_consent:
            params.append("remote_data_consent=true")
        suffix = "?" + "&".join(params) if params else ""
        return self.request(f"/negotiations/{session_id}/agents/run{suffix}", method="POST")

    def agent_run(self, session_id: str) -> dict[str, Any]:
        return self.request(f"/negotiations/{session_id}/agents")


__all__ = ["APIError", "APIConnectionError", "Client", "SUPPORTED_CURRENCIES"]
