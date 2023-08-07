from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from httpx import AsyncClient


async def test_cpes_vendors_not_superuser(client: "AsyncClient", user_token_headers: dict[str, str]) -> None:
    response = await client.get("/api/cpe-vendors", headers=user_token_headers)
    assert response.status_code == 403
    assert response.json()["detail"] == "Insufficient privileges"


async def test_cpes_vendors_list(client: "AsyncClient", superuser_token_headers: dict[str, str]) -> None:
    response = await client.get("/api/cpe-vendors", headers=superuser_token_headers)
    assert response.status_code == 200
    assert int(response.json()["total"]) > 0


async def test_cpes_vendors_get(client: "AsyncClient", superuser_token_headers: dict[str, str]) -> None:
    response = await client.get(
        "/api/cpe-vendors/daa81279-1f85-41ba-a49a-a9430d99cc5c", headers=superuser_token_headers
    )
    assert response.status_code == 200
    assert response.json()["name"] == "cisco"


async def test_cpe_vendors_create(client: "AsyncClient", superuser_token_headers: dict[str, str]) -> None:
    response = await client.post(
        "/api/cpe-vendors",
        json={
            "name": "microtik",
        },
        headers=superuser_token_headers,
    )
    assert response.status_code == 201


async def test_cpe_vendors_update(client: "AsyncClient", superuser_token_headers: dict[str, str]) -> None:
    response = await client.patch(
        "/api/cpe-vendors/daa81279-1f85-41ba-a49a-a9430d99cc5c",
        json={
            "name": "juniper",
        },
        headers=superuser_token_headers,
    )
    assert response.status_code == 200
    assert response.json()["name"] == "juniper"


async def test_cpe_vendors_delete(client: "AsyncClient", superuser_token_headers: dict[str, str]) -> None:
    response = await client.delete(
        "/api/cpe-vendors/daa81279-1f85-41ba-a49a-a9430d99cc5d",
        headers=superuser_token_headers,
    )
    assert response.status_code == 204


async def test_cpe_vendors_uniqueness(client: "AsyncClient", superuser_token_headers: dict[str, str]) -> None:
    response = await client.post(
        "/api/cpe-vendors",
        json={
            "name": "cisco",
        },
        headers=superuser_token_headers,
    )
    # todo find out how to work with duplicate db objects
    assert response.status_code == 500
