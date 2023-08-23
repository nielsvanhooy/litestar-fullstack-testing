from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from httpx import AsyncClient


async def test_tscm_checks_list(client: "AsyncClient", superuser_token_headers: dict[str, str]) -> None:
    response = await client.get("/api/tscm", headers=superuser_token_headers)
    assert response.status_code == 200
    assert int(response.json()["total"]) > 0


async def test_tscm_checks_get(client: "AsyncClient", superuser_token_headers: dict[str, str]) -> None:
    response = await client.get("/api/tscm/f240e0f9-41d6-4a08-975a-bec270cb8600", headers=superuser_token_headers)
    assert response.status_code == 200
    assert response.json()["key"] == "ACL10"


async def test_tscm_check_create(client: "AsyncClient", superuser_token_headers: dict[str, str]) -> None:
    response = await client.post(
        "/api/tscm",
        json={
            "id": "4051bd62-37e9-49de-b858-24fad4f0fc0c",
            "key": "VTY-0-4-VPN",
            "regex": "None",
            "python_code": 'regex = \\\r\n"line vty 0 4\\n"\\\r\n" access-class 14 in( vrf-also)?\\n"\\\r\n" exec-timeout 9 0\\n"\\\r\n" password 7 .{10,55}\\n"\\\r\n"( no activation-character\\n)?"\\\r\n"( logging synchronous\\n)?"\\\r\n"( length 0\\n)?"\\\r\n"( transport preferred none\\n)?"\\\r\n" transport input ssh\\n"\\\r\n" transport output none"\r\nvalidated=True\r\nif not re.search(regex,config):\r\n    validated=False\r\n    print ("VTY 0 4 niet gevonden of onjuist geconfigureerd.")',
            "remediation_commands": "None",
            "vendor": "cisco",
            "business_service": "VPN",
            "device_model": "All",
            "replaces_parent_check": "None",
            "has_child_check": False,
            "active": True,
        },
        headers=superuser_token_headers,
    )
    assert response.status_code == 201


async def test_tscm_check_update(client: "AsyncClient", superuser_token_headers: dict[str, str]) -> None:
    response = await client.patch(
        "/api/tscm/f240e0f9-41d6-4a08-975a-bec270cb8600",
        json={
            "id": "f240e0f9-41d6-4a08-975a-bec270cb8600",
            "key": "ACL10-adjusted",
            "regex": "None",
            "python_code": 'validated=True\r\nfirst_check = False\r\nsecond_check = False\r\n\r\nfirst_check_regexes=[\r\n    "ip access-list standard 10\\n"\\\r\n    " 10 permit[\\s]+193\\.172\\.69\\.64 0\\.0\\.0\\.31\\n"\\\r\n    " 20 permit[\\s]+193\\.172\\.69\\.96 0\\.0\\.0\\.31\\n"\\\r\n    " 30 deny[\\s]+any",\r\n]\r\nfor regex in first_check_regexes:\r\n    # added config it not None and  to the check because for PLTM4764\r\n    if re.search(regex,config):\r\n        first_check = True\r\n\r\nsecond_check_regexes=[\r\n    "access-list 10 permit[\\s]+193\\.172\\.69\\.64 0\\.0\\.0\\.31\\n"\\\r\n    "access-list 10 permit[\\s]+193\\.172\\.69\\.96 0\\.0\\.0\\.31\\n"\\\r\n    "access-list 10 deny[\\s]+any",\r\n]\r\nfor regex in second_check_regexes:\r\n    if re.search(regex,config):\r\n        second_check = True\r\n\r\nif not first_check and not second_check:\r\n    validated = False\r\n    print ("ACL 10 niet aangetroffen of niet juist")',
            "remediation_commands": "None",
            "vendor": "cisco",
            "business_service": "VPN",
            "device_model": "All",
            "replaces_parent_check": "None",
            "has_child_check": False,
            "active": True,
        },
        headers=superuser_token_headers,
    )
    assert response.status_code == 200
    assert response.json()["key"] == "ACL10-adjusted"


async def test_tscm_check_delete(client: "AsyncClient", superuser_token_headers: dict[str, str]) -> None:
    response = await client.delete(
        "/api/tscm/f240e0f9-41d6-4a08-975a-bec270cb8600",
        headers=superuser_token_headers,
    )
    assert response.status_code == 204


async def test_perform_tscm_check(client: "AsyncClient", superuser_token_headers: dict[str, str]) -> None:
    response = await client.post("/api/tscm/TESM1233/check", headers=superuser_token_headers)
    assert response.status_code == 201
    assert int(response.json()["total"]) > 0


######## refactor this back to the unit test part but for now its ok
