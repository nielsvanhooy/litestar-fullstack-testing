from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from httpx import AsyncClient


async def test_cpes_list(client: "AsyncClient", superuser_token_headers: dict[str, str]) -> None:
    response = await client.get("/api/cpes", headers=superuser_token_headers)
    assert response.status_code == 200
    assert int(response.json()["total"]) > 0


async def test_cpes_get(client: "AsyncClient", superuser_token_headers: dict[str, str]) -> None:
    response = await client.get("/api/cpes/TESM1233", headers=superuser_token_headers)
    assert response.status_code == 200
    assert response.json()["routername"] == "tes-gv-1111xx-11"


async def test_cpes_create(client: "AsyncClient", superuser_token_headers: dict[str, str]) -> None:
    response = await client.post(
        "/api/cpes",
        json={
            "device_id": "TESM1235",
            "routername": "tes-gv-3333xx-33",
            "os": "iosxe",
            "mgmt_ip": "10.1.1.151",
            "sec_mgmt_ip": None,
            "vendor": "cisco",
            "business_service": "VPN",
        },
        headers=superuser_token_headers,
    )
    assert response.status_code == 201


async def test_cpes_update(client: "AsyncClient", superuser_token_headers: dict[str, str]) -> None:
    response = await client.patch(
        "/api/cpes/TESM1233",
        json={
            "device_id": "TESM1233",
            "os": "hvrp",
        },
        headers=superuser_token_headers,
    )
    assert response.status_code == 200
    assert response.json()["os"] == "hvrp"


async def test_cpes_delete(client: "AsyncClient", superuser_token_headers: dict[str, str]) -> None:
    response = await client.delete(
        "/api/cpes/TESM1234",
        headers=superuser_token_headers,
    )
    assert response.status_code == 204


async def test_cpe_readout(client: "AsyncClient", superuser_token_headers: dict[str, str]) -> None:
    response = await client.post(
        "/api/cpes/TESM1233/readout",
        headers=superuser_token_headers,
    )
    assert response.status_code == 201
