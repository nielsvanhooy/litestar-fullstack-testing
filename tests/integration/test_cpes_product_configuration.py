from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from httpx import AsyncClient


async def test_cpe_product_configurations_list(client: "AsyncClient", superuser_token_headers: dict[str, str]) -> None:
    response = await client.get("/api/product-configurations", headers=superuser_token_headers)
    assert response.status_code == 200
    assert int(response.json()["total"]) > 0


async def test_cpe_product_configuration_get(client: "AsyncClient", superuser_token_headers: dict[str, str]) -> None:
    response = await client.get(
        "/api/product-configurations/76175388-5fb9-42ec-b42d-701e012ce7db", headers=superuser_token_headers
    )
    assert response.status_code == 200
    assert response.json()["cpeModel"] == "3600"


async def test_cpe_product_configuration_create(client: "AsyncClient", superuser_token_headers: dict[str, str]) -> None:
    response = await client.post(
        "/api/product-configurations",
        json={
            "id": "76175388-5fb9-42ec-b42d-701e013ce8db",
            "description": "product configuration for an ASR920",
            "configuration_id": 99991,
            "cpe_model": "ASR920",
            "vendor": "cisco",
        },
        headers=superuser_token_headers,
    )
    assert response.status_code == 201


async def test_cpe_product_configuration_update(client: "AsyncClient", superuser_token_headers: dict[str, str]) -> None:
    response = await client.patch(
        "/api/product-configurations/76175388-5fb9-42ec-b42d-701e012ce7db",
        json={
            "id": "76175388-5fb9-42ec-b42d-701e012ce7db",
            "description": "product configuration for an Cisco 3800",
            "configuration_id": 99991,
            "cpe_model": "C3800",
            "vendor": "cisco",
        },
        headers=superuser_token_headers,
    )
    assert response.status_code == 200
    assert response.json()["cpeModel"] == "C3800"


async def test_cpe_product_configuration_delete(client: "AsyncClient", superuser_token_headers: dict[str, str]) -> None:
    response = await client.delete(
        "/api/product-configurations/76175388-5fb9-42ec-b42d-701e012ce7db",
        headers=superuser_token_headers,
    )
    assert response.status_code == 204
