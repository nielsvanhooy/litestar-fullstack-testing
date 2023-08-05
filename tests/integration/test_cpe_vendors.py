from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from httpx import AsyncClient


async def test_cpes_vendors_not_superuser(client: "AsyncClient", user_token_headers: dict[str, str]) -> None:
    response = await client.get("/api/cpe-vendors", headers=user_token_headers)
    assert response.status_code == 403
    assert response.json()["detail"] == "Insufficient privileges"
