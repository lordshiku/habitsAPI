from __future__ import annotations
import httpx

QUOTE_ENDPOINT = "https://api.quotable.io/random"  # public, no key required

async def fetch_motivational_quote(timeout: float = 5.0) -> str | None:
    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            r = await client.get(QUOTE_ENDPOINT)
            if r.status_code == 200:
                data = r.json()
                return data.get("content")
    except Exception:
        # swallow network errors; quote is optional
        pass
    return None