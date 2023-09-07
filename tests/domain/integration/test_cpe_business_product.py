from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from httpx import AsyncClient


async def test_cpes_business_products_not_superuser(client: "AsyncClient", user_token_headers: dict[str, str]) -> None:
    response = await client.get("/api/cpe-business-products", headers=user_token_headers)
    assert response.status_code == 403
    assert response.json()["detail"] == "Insufficient privileges"


async def test_cpes_business_products_list(client: "AsyncClient", superuser_token_headers: dict[str, str]) -> None:
    response = await client.get("/api/cpe-business-products", headers=superuser_token_headers)
    assert response.status_code == 200
    assert int(response.json()["total"]) > 0


async def test_cpes_business_products_get(client: "AsyncClient", superuser_token_headers: dict[str, str]) -> None:
    response = await client.get(
        "/api/cpe-business-products/daa81279-1f85-41ba-a49a-a9430d99cc5e", headers=superuser_token_headers
    )
    assert response.status_code == 200
    assert response.json()["name"] == "VPN"


async def test_cpe_business_products_create(client: "AsyncClient", superuser_token_headers: dict[str, str]) -> None:
    response = await client.post(
        "/api/cpe-business-products",
        json={
            "name": "International network",
            "key": "International",
        },
        headers=superuser_token_headers,
    )
    assert response.status_code == 201


async def test_cpe_business_products_update(client: "AsyncClient", superuser_token_headers: dict[str, str]) -> None:
    response = await client.patch(
        "/api/cpe-business-products/daa81279-1f85-41ba-a49a-a9430d99cc5e",
        json={
            "name": "VPN",
            "key": "VPN Network New",
        },
        headers=superuser_token_headers,
    )
    assert response.status_code == 200
    assert response.json()["key"] == "VPN Network New"


async def test_cpe_business_products_delete(client: "AsyncClient", superuser_token_headers: dict[str, str]) -> None:
    response = await client.delete(
        "/api/cpe-business-products/daa81279-1f85-41ba-a49a-a9430d99cc5e",
        headers=superuser_token_headers,
    )
    assert response.status_code == 204


async def test_cpe_business_products_uniqueness(client: "AsyncClient", superuser_token_headers: dict[str, str]) -> None:
    response = await client.post(
        "/api/cpe-business-products",
        json={
            "name": "VPN",
            "key": "VPN Network",
        },
        headers=superuser_token_headers,
    )
    # todo find out how to work with duplicate db objects
    assert response.status_code == 500
