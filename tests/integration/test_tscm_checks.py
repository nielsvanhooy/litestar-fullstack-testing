from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from httpx import AsyncClient


async def test_tscm_check_create(client: "AsyncClient", superuser_token_headers: dict[str, str]) -> None:
    response = await client.post(
        "/api/tscm",
        json=   {
      "id":"4051bd62-37e9-49de-b858-24fad4f0fc0c",
      "key":"VTY-0-4-KPN-VPN",
      "regex":"None",
      "python_code":"regex = \\\r\n\"line vty 0 4\\n\"\\\r\n\" access-class 14 in( vrf-also)?\\n\"\\\r\n\" exec-timeout 9 0\\n\"\\\r\n\" password 7 .{10,55}\\n\"\\\r\n\"( no activation-character\\n)?\"\\\r\n\"( logging synchronous\\n)?\"\\\r\n\"( length 0\\n)?\"\\\r\n\"( transport preferred none\\n)?\"\\\r\n\" transport input ssh\\n\"\\\r\n\" transport output none\"\r\nvalidated=True\r\nif not re.search(regex,config):\r\n    validated=False\r\n    print (\"VTY 0 4 niet gevonden of onjuist geconfigureerd.\")",
      "remediation_commands":"None",
      "vendor": "cisco",
      "business_service": "VPN",
      "device_model":"All",
      "replaces_parent_check":"None",
      "has_child_check":False,
      "active":True
   },
        headers=superuser_token_headers,
    )
    assert response.status_code == 201
