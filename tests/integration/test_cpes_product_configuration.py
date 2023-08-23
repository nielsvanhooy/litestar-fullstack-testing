from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from httpx import AsyncClient


async def test_cpe_product_configurations_list(client: "AsyncClient", superuser_token_headers: dict[str, str]) -> None:
    response = await client.get("/api/product-configurations", headers=superuser_token_headers)
    assert response.status_code == 200
    assert int(response.json()["total"]) > 0


# async def test_tscm_checks_get(client: "AsyncClient", superuser_token_headers: dict[str, str]) -> None:
#     response = await client.get("/api/product-configurations/f240e0f9-41d6-4a08-975a-bec270cb8600", headers=superuser_token_headers)
#     assert response.status_code == 200
#     assert response.json()["key"] == "ACL10"
