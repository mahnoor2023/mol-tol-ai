"""Synthetic API-key integration example for an owner-provisioned API."""
from __future__ import annotations

import os
import uuid

from mol_tol_sdk import APIConnectionError, APIError, Client


def main() -> None:
    base_url = os.environ["MOLTOL_API_URL"]
    buyer = Client(base_url, os.environ["MOLTOL_BUYER_API_KEY"], auth_mode="api_key")
    seller = Client(base_url, os.environ["MOLTOL_SELLER_API_KEY"], auth_mode="api_key")

    try:
        session = buyer.create(
            buyer_id="portfolio-buyer-agent",
            buyer_name="Synthetic buyer",
            seller_id="portfolio-seller-agent",
            seller_name="Synthetic seller",
            seller_tenant_id=os.environ["MOLTOL_SELLER_TENANT_ID"],
            product_id="synthetic-api-plan",
            product_name="Synthetic software API plan",
            quantity=1,
            currency="USD",
            opening_offer_minor=8000,
            max_rounds=4,
        )
        session_id = session["id"]
        if "buyer_max_minor" in session or "seller_min_minor" in session:
            raise RuntimeError("Public session response unexpectedly contains private policy values")

        buyer.offer(session_id, 8000, "USD", quantity=1)
        counter = seller.counteroffer(session_id)
        amount_minor = counter["offers"][-1]["amount_minor"]
        buyer.offer(session_id, amount_minor, "USD", quantity=1)
        seller.offer(session_id, amount_minor, "USD", quantity=1)

        proof = buyer.finalize(session_id, f"public-pilot-{uuid.uuid4()}")
        verification = buyer.verify(proof)
        print("Workflow: API-key authenticated; deterministic server policies authoritative")
        print("Final state:", buyer.get(session_id)["state"])
        print("Proof verified:", verification.get("valid") is True)
        print("Model inference count: 0 (this example does not call a model provider)")
    except APIError as exc:
        print(f"API error: status={exc.status_code}, code={exc.code}, detail={exc.detail}")
        raise
    except APIConnectionError as exc:
        print(f"Transport error: {exc}")
        raise


if __name__ == "__main__":
    main()
