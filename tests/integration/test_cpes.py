from typing import TYPE_CHECKING

from app.domain.cpe.dependencies import provides_cpe_service
from app.lib.db.base import session

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
            "product_configuration": 999990,
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


######## refactor this back to the unit test part but for now its ok
async def test_get_cpes_to_ping() -> None:
    db = session()
    async with db as db_session:
        cpe_service = await anext(provides_cpe_service(db_session=db_session))
        cpes_to_ping = await cpe_service.get_cpes_to_ping()
        assert len(cpes_to_ping) > 0
        assert "mgmt_ip" in cpes_to_ping["10.1.1.142"]
