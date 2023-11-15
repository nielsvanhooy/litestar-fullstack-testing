from __future__ import annotations

import asyncio
import datetime
import re
from typing import TYPE_CHECKING, Any
from unittest.mock import MagicMock

import pytest
from litestar.testing import TestClient
from structlog.contextvars import clear_contextvars
from structlog.testing import CapturingLogger

from app.domain.tscm.tscm import CpeTscmCheck, TscmExportReport
from app.lib import settings

if TYPE_CHECKING:
    from collections import abc
    from collections.abc import Generator, Iterator

    from litestar import Litestar
    from pytest import FixtureRequest, MonkeyPatch

    from app.domain.accounts.models import User
    from app.domain.cpe.models import CPE
    from app.domain.cpe_business_product.models import CPEBusinessProduct
    from app.domain.cpe_product_configuration.models import CPEProductConfiguration
    from app.domain.cpe_vendor.models import CPEVendor
    from app.domain.teams.models import Team
    from app.domain.tscm.models import TSCMCheck


@pytest.fixture(scope="session")
def event_loop() -> "abc.Iterator[asyncio.AbstractEventLoop]":
    """Scoped Event loop.

    Need the event loop scoped to the session so that we can use it to check
    containers are ready in session scoped containers fixture.
    """
    policy = asyncio.get_event_loop_policy()
    loop = policy.new_event_loop()
    try:
        yield loop
    finally:
        loop.close()


def pytest_addoption(parser: pytest.Parser) -> None:
    """Adds Pytest ini config variables for the plugin."""
    parser.addini(
        "unit_test_pattern",
        (
            "Regex used to identify if a test is running as part of a unit or integration test "
            "suite. The pattern is matched against the path of each test function and affects the "
            "behavior of fixtures that are shared between unit and integration tests."
        ),
        type="string",
        default=r"^.*/tests/unit/.*$",
    )


@pytest.fixture(name="app")
def fx_app(pytestconfig: pytest.Config, monkeypatch: MonkeyPatch) -> Litestar:
    """Returns:
    An application instance, configured via plugin.
    """
    from app.asgi import create_app

    return create_app()


@pytest.fixture(name="client")
def fx_client(app: Litestar) -> Generator[TestClient, None, None]:
    """Test client fixture for making calls on the global app instance."""
    with TestClient(app=app) as client:
        yield client


@pytest.fixture(name="is_unit_test")
def fx_is_unit_test(request: FixtureRequest) -> bool:
    """Uses the ini option `unit_test_pattern` to determine if the test is part
    of unit or integration tests.
    """
    unittest_pattern: str = request.config.getini("unit_test_pattern")  # pyright:ignore
    return bool(re.search(unittest_pattern, str(request.path)))


@pytest.fixture(name="raw_cpes")
def fx_raw_cpes() -> list[CPE | dict[str, Any]]:
    """Unstructured cpe representations."""

    return [
        {
            "device_id": "TESM1233",
            "routername": "tes-gv-1111xx-11",
            "os": "iosxe",
            "mgmt_ip": "10.1.1.142",
            "sec_mgmt_ip": None,
            "vendor": "cisco",
            "business_service": "VPN",
            "product_configuration": 999990,
            "online_status": False,
        },
        {
            "device_id": "TESM1234",
            "routername": "tes-gv-2222xx-22",
            "os": "iosxe",
            "mgmt_ip": "10.1.1.156",
            "sec_mgmt_ip": None,
            "vendor": "cisco",
            "business_service": "VPN",
            "product_configuration": 999999,
            "online_status": True,
        },
    ]


@pytest.fixture(name="raw_cpe_business_products")
def fx_raw_cpe_business_products() -> list[CPEBusinessProduct | dict[str, Any]]:
    """Unstructured cpe business product representations."""

    return [
        {
            "id": "daa81279-1f85-41ba-a49a-a9430d99cc5e",
            "name": "VPN",
            "key": "VPN Network",
        },
        {
            "id": "daa81279-1f85-41ba-a49a-a9430d99cc5f",
            "name": "NON VPN",
            "key": "Non VPN Network",
        },
        {
            "id": "daa81279-1f85-41ba-a49a-a9430d99cc5d",
            "name": "CI",
            "key": "CI",
        },
        {
            "id": "daa81279-1f85-41ba-a49a-a9430d99cc5a",
            "name": "INS",
            "key": "INS",
        },
    ]


@pytest.fixture(name="raw_cpe_vendors")
def fx_raw_cpe_vendors() -> list[CPEVendor | dict[str, Any]]:
    """Unstructured cpe business product representations."""

    return [
        {
            "id": "daa81279-1f85-41ba-a49a-a9430d99cc5c",
            "name": "cisco",
        },
        {
            "id": "daa81279-1f85-41ba-a49a-a9430d99cc5d",
            "name": "huawei",
        },
    ]


@pytest.fixture(name="raw_tscm_checks")
def fx_raw_tscm_checks() -> list[TSCMCheck | dict[str, Any]]:
    """Unstructured tscm check representations."""

    return [
        {
            "id": "f240e0f9-41d6-4a08-975a-bec270cb8600",
            "key": "ACL10",
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
        {
            "id": "5cf14ce8-76ec-4271-b587-cb6fb63f8ebd",
            "key": "TACACS_settings",
            "regex": "None",
            "python_code": 'regexes=[\r\n"aaa new-model\\n",\r\n"aaa authentication login default group tacacs\\+ enable\\n",\r\n"aaa authentication enable default group tacacs\\+ enable\\n",\r\n"aaa authorization console\\n",\r\n"aaa authorization exec default group tacacs\\+ if-authenticated \\n",\r\n"aaa authorization commands 15 default group tacacs\\+ none \\n",\r\n"(aaa accounting exec default\\n action-type start-stop\\n group tacacs\\+\\n|aaa accounting exec default start-stop group tacacs\\+\\n)",\r\n"(aaa accounting commands 1 default\\n action-type start-stop\\n group tacacs\\+\\n|aaa accounting commands 1 default start-stop group tacacs\\+\\n)",\r\n"(aaa accounting commands 15 default\\n action-type start-stop\\n group tacacs\\+\\n|aaa accounting commands 15 default start-stop group tacacs\\+\\n)",\r\n]\r\nvalidated=True\r\nfor regex in regexes:\r\n    if not re.search(regex,config):\r\n        validated=False\r\n        print ("Niet gevonden:",regex)',
            "remediation_commands": "None",
            "vendor": "cisco",
            "business_service": "VPN",
            "device_model": "All",
            "replaces_parent_check": "None",
            "has_child_check": False,
            "active": True,
        },
        {
            "id": "4051bd62-37e9-49de-b858-24fad4f0fc0c",
            "key": "VTY-0-4-KPN-VPN",
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
        {
            "id": "db1da242-dc9d-42c7-81f2-0c25c0f9a637",
            "key": "VTY-5-15",
            "regex": "None",
            "python_code": 'regexes=[\r\n"line vty 5",\r\n]\r\nvalidated=True\r\nfor regex in regexes:\r\n    if re.search(regex,config):\r\n        validated=True\r\n        regexes=[\r\n\t\t"line vty 5.{1,4}\\n"\\\r\n        "( access-class 14 in vrf-also\\n| access-class 14 in\\n|)?"\\\r\n        "( exec-timeout 9 0\\n)?"\\\r\n        "( password 7 .{1,30}\\n)?"\\\r\n        "( no activation-character\\n)?"\\\r\n        "( logging synchronous\\n)?"\\\r\n        " no exec\\n"\\\r\n        "( transport preferred none\\n)?"\\\r\n        " transport input none\\n"\\\r\n        " transport output none\\n",\r\n        ]\r\n        for regex in regexes:\r\n            if not re.search(regex,config):\r\n                validated=False\r\n                print ("Line VTY 5 15 niet goed geconfigureerd.")\r\n        break',
            "remediation_commands": "None",
            "vendor": "cisco",
            "business_service": "VPN",
            "device_model": "All",
            "replaces_parent_check": "None",
            "has_child_check": False,
            "active": True,
        },
        {
            "id": "f5df9a31-cb5f-429b-8ef4-8d49a030c529",
            "key": "ip-ssh",
            "regex": "None",
            "python_code": 'regexes=[\r\n"ip ssh time-out 60",\r\n"ip ssh logging events",\r\n"ip ssh version 2",\r\n#\t"ip ssh dh min size 2048", Uitgezet omdat nog niet iedere router dit ondersteund\r\n"ip scp server enable",\r\n"\\nservice password-encryption",\r\n]\r\nvalidated=True\r\nfor regex in regexes:\r\n    if not re.search(regex,config):\r\n        validated=False\r\n        print("Niet gevonden", regex)',
            "remediation_commands": "None",
            "vendor": "cisco",
            "business_service": "VPN",
            "device_model": "All",
            "replaces_parent_check": "None",
            "has_child_check": False,
            "active": True,
        },
        {
            "id": "7f078246-c5d0-42f0-8c3b-5e95cce01bd0",
            "key": "TACACS-servers",
            "regex": "None",
            "python_code": 'validated=True\r\n\r\nfirst_check = True\r\nsecond_check = True\r\nthird_check = True\r\n\r\nfirst_check_regexes=[\r\n"tacacs server pri-acs\\n address ipv4 193.172.69.74\\n key 7 .{1,40}",\r\n"tacacs server sec-acs\\n address ipv4 193.172.69.106\\n key 7 .{1,40}",\r\n]\r\nfor regex in first_check_regexes:\r\n    if not re.search(regex,config):\r\n        first_check = False\r\n\r\nsecond_check_regexes=[\r\n    "tacacs-server host 193.172.69.74\\n"\\\r\n    "tacacs-server host 193.172.69.106\\n"\\\r\n    "(no tacacs-server directed-request\\n|tacacs-server directed-request\\n)?"\\\r\n    "tacacs-server key 7 .{1,40}",\r\n]\r\n\r\nfor regex in second_check_regexes:\r\n    if not re.search(regex,config):\r\n        second_check = False\r\n\r\nthird_check_regexes=[\r\n\t"tacacs-server host 193.172.69.74 key 7 .{1,40}\\ntacacs-server host 193.172.69.106 key 7 .{1,40}",\r\n]\r\n\r\nfor regex in third_check_regexes:\r\n    if not re.search(regex,config):\r\n        third_check = False\r\n\r\nif not first_check and not second_check and not third_check:\r\n    validated = False\r\n    print ("Tacacs servers niet aangetroffen of niet compleet")',
            "remediation_commands": "None",
            "vendor": "cisco",
            "business_service": "VPN",
            "device_model": "All",
            "replaces_parent_check": "None",
            "has_child_check": False,
            "active": True,
        },
        {
            "id": "b4c52e24-6c0b-4ac3-a808-6d97af511d84",
            "key": "start-end-markers",
            "regex": "None",
            "python_code": 'regexes=[\r\n    "hostname (.*)",\r\n\t"end",\r\n]\r\nvalidated=True\r\nfor regex in regexes:\r\n    if not re.search(regex,config):\r\n        validated=False\r\n        print ("Config niet compleet geladen!")',
            "remediation_commands": "None",
            "vendor": "cisco",
            "business_service": "VPN",
            "device_model": "All",
            "replaces_parent_check": "None",
            "has_child_check": False,
            "active": True,
        },
        {
            "id": "2dd6014e-fb39-4425-8919-6c6f29b2ff88",
            "key": "Telnet-SSH-FTP",
            "regex": "None",
            "python_code": 'regexes=[\r\n\t"stelnet server enable",\r\n\t"sftp server enable",\r\n]\r\nvalidated=True\r\nfor regex in regexes:\r\n    if not re.search(regex,config):\r\n        validated=False\r\n        print ("Niet gevonden,",regex)',
            "remediation_commands": "None",
            "vendor": "huawei",
            "business_service": "CI",
            "device_model": "All",
            "replaces_parent_check": "None",
            "has_child_check": False,
            "active": True,
        },
        {
            "id": "072b923e-77b7-4a6b-a151-b543a19a5c4e",
            "key": "SNMP-server_24chr-VPN-C",
            "regex": "None",
            "python_code": 'regexes=[\r\n"snmp-server community .{24} (view exclvdsl2mib )?(view crash-block )?RO 10",\r\n"snmp-server community .{24} (view exclvdsl2mib )?(view crash-block )?RO 93",\r\n#"snmp-server enable traps syslog",\r\n"snmp-server host 145.13.76.159 version 2c .{24}",\r\n"snmp-server host 145.13.76.33 version 2c .{24}",\r\n"logging history notifications",\r\n]\r\nvalidated=True\r\nfor regex in regexes:\r\n    if not re.search(regex,config):\r\n        validated=False\r\n        print ("Niet gevonden", regex)',
            "remediation_commands": "",
            "vendor": "cisco",
            "business_service": "VPN",
            "device_model": "All",
            "replaces_parent_check": "None",
            "has_child_check": False,
            "active": True,
        },
        {
            "id": "17ba90e5-9d6f-41a0-a290-d5af378c7a6c",
            "key": "SNMP-server",
            "regex": "None",
            "python_code": 'regexes=[\r\n#"snmp-server community .{8} (view exclvdsl2mib )?(view crash-block )?RO 10",\r\n"snmp-server community .{24} (view exclvdsl2mib )?(view crash-block )?RO 10",\r\n#"snmp-server community .{8} (view exclvdsl2mib )?(view crash-block )?RO 93",\r\n"snmp-server community .{24} (view exclvdsl2mib )?(view crash-block )?RO 93",\r\n#"(snmp-server ifindex persist|snmp ifmib ifindex persist)",\r\n#"snmp-server enable traps syslog",\r\n#"snmp-server host 145.13.76.159 version 2c .{8}",\r\n"snmp-server host 145.13.76.159 version 2c .{24}",\r\n#"snmp-server host 145.13.76.33 version 2c .{8}",\r\n"snmp-server host 145.13.76.33 version 2c .{24}",\r\n"logging history notifications",\r\n]\r\nvalidated=True\r\nfor regex in regexes:\r\n    if not re.search(regex,config):\r\n        validated=False\r\n        print ("Niet gevonden", regex)',
            "remediation_commands": "",
            "vendor": "cisco",
            "business_service": "VPN",
            "device_model": "All",
            "replaces_parent_check": "None",
            "has_child_check": False,
            "active": True,
        },
        {
            "id": "49a3a3d2-c3ae-4529-b049-6f504e3ca6eb",
            "key": "TACACS_servers",
            "regex": "None",
            "python_code": 'regexes=[\r\n"hwtacacs-server template ip-vpn\\n\\\r\n hwtacacs-server authentication 193.172.69.74\\n\\\r\n hwtacacs-server authentication 193.172.69.106 secondary\\n\\\r\n hwtacacs-server authorization 193.172.69.74\\n\\\r\n hwtacacs-server authorization 193.172.69.106 secondary\\n\\\r\n hwtacacs-server accounting 193.172.69.74\\n\\\r\n hwtacacs-server accounting 193.172.69.106 secondary\\n\\\r\n( hwtacacs-server source-ip source-loopback 0\\n)?\\\r\n hwtacacs-server shared-key cipher .*?\\n\\\r\n undo hwtacacs-server user-name domain-included\\n"\r\n]\r\nvalidated=True\r\nfor regex in regexes:\r\n    if not re.search(regex,config):\r\n        validated=False\r\n        print ("niet gevonden",regex)',
            "remediation_commands": "None",
            "vendor": "huawei",
            "business_service": "VPN",
            "device_model": "All",
            "replaces_parent_check": "None",
            "has_child_check": False,
            "active": True,
        },
        {
            "id": "764bd659-713a-42de-9e96-c2df0e4e09dd",
            "key": "ACL-2014",
            "regex": "None",
            "python_code": 'regexes=[\r\n    "acl number 2014  \\n"\\\r\n    " description Incoming user access\\n"\\\r\n    " rule 5 permit source 193\\.172\\.69\\.0 0\\.0\\.0\\.127 \\n"\\\r\n    " rule 10 deny \\n",\r\n]\r\nvalidated=True\r\nfor regex in regexes:\r\n    if not re.search(regex,config):\r\n        validated=False\r\n        print ("Niet gevonden,",regex)',
            "remediation_commands": "None",
            "vendor": "huawei",
            "business_service": "VPN",
            "device_model": "All",
            "replaces_parent_check": "None",
            "has_child_check": False,
            "active": True,
        },
        {
            "id": "d020ca11-b570-41fb-b340-48e8d2f815d3",
            "key": "ACL-2093",
            "regex": "None",
            "python_code": 'regexes=[\r\n    "acl number 2093  \\n"\\\r\n    " rule 5 permit source 193.172.69.0 0.0.0.127 \\n"\\\r\n    " rule 10 permit source 145.13.71.128 0.0.0.127 \\n"\\\r\n    " rule 15 permit source 145.13.76.0 0.0.0.255 \\n"\\\r\n    " rule 100 deny \\n",\r\n    ]\r\nvalidated=True\r\nfor regex in regexes:\r\n    if not re.search(regex,config):\r\n        validated=False\r\n        print ("Niet gevonden,",regex)',
            "remediation_commands": "None",
            "vendor": "huawei",
            "business_service": "VPN",
            "device_model": "All",
            "replaces_parent_check": "None",
            "has_child_check": False,
            "active": True,
        },
        {
            "id": "8fd6ddc8-d8dc-4c6c-a9b6-1d3229619c75",
            "key": "TACACS-settings",
            "regex": "None",
            "python_code": 'regexes=[\r\n"aaa\\n"\\\r\n" authentication-scheme default\\n"\\\r\n"  authentication-mode hwtacacs local\\n"\\\r\n"  authentication-super hwtacacs super\\n"\\\r\n" authentication-scheme radius\\n"\\\r\n"  authentication-mode radius\\n"\\\r\n" authorization-scheme default\\n"\\\r\n"  authorization-mode hwtacacs none\\n"\\\r\n"  authorization-cmd 1 hwtacacs none\\n"\\\r\n"  authorization-cmd 3 hwtacacs none\\n"\\\r\n"  authorization-cmd 15 hwtacacs none\\n"\\\r\n" accounting-scheme default\\n"\\\r\n"  accounting-mode hwtacacs\\n"\\\r\n"  accounting start-fail online\\n"\\\r\n" recording-scheme rscheme0\\n"\\\r\n"  recording-mode hwtacacs ip-vpn\\n"\\\r\n" cmd recording-scheme rscheme0\\n"\\\r\n" domain default\\n"\\\r\n"  authentication-scheme default\\n"\r\n"(  accounting-scheme default\\n)?"\\\r\n"  authorization-scheme default\\n"\\\r\n"(  radius-server default\\n)?"\\\r\n" domain default_admin\\n"\\\r\n"  authentication-scheme default\\n"\\\r\n"(  accounting-scheme default\\n)?"\\\r\n"  authorization-scheme default\\n"\\\r\n"  hwtacacs-server ip-vpn\\n"\\\r\n" local-user admin password irreversible-cipher .{40,60} access-limit 4\\n"\\\r\n" local-user admin privilege level 15\\n"\\\r\n" local-user admin service-type terminal ssh\\n",\r\n]\r\nvalidated=True\r\nfor regex in regexes:\r\n    if not re.search(regex,config):\r\n        validated=False\r\n        print ("Niet gevonden,",regex)',
            "remediation_commands": "None",
            "vendor": "huawei",
            "business_service": "VPN",
            "device_model": "All",
            "replaces_parent_check": "None",
            "has_child_check": False,
            "active": True,
        },
        {
            "id": "8aece957-e1c4-420d-9dc3-8c2477dd5b10",
            "key": "Statics-If-PPP",
            "regex": "None",
            "python_code": 'regexes=[\r\n"interface Dialer0\\n link-protocol ppp\\n ppp chap user .*\\n ppp chap password cipher .*",\r\n]\r\nvalidated=True\r\nfor regex in regexes:\r\n    if re.search(regex,config):\r\n        validated=True\r\n        regexes=[\r\n            "ip route-static 193.172.69.0 255.255.255.128 213.162.171.193 preference 1",\r\n            "ip route-static 193.172.69.0 255.255.255.128 (null 0|NULL0) preference 250",\r\n            "ip route-static 145.13.71.128 255.255.255.128 213.162.171.193 preference 1",\r\n            "ip route-static 145.13.71.128 255.255.255.128 (null 0|NULL0) preference 250",\r\n            "ip route-static 145.13.76.0 255.255.255.0 213.162.171.193 preference 1",\r\n            "ip route-static 145.13.76.0 255.255.255.0 (null 0|NULL0) preference 250",\r\n        ]\r\n        validated=True\r\n        for regex in regexes:\r\n            if not re.search(regex,config):\r\n                validated=False\r\n                print ("Niet gevonden,",regex)',
            "remediation_commands": "None",
            "vendor": "huawei",
            "business_service": "VPN",
            "device_model": "All",
            "replaces_parent_check": "None",
            "has_child_check": False,
            "active": True,
        },
        {
            "id": "bcc051fb-48e4-423d-bf56-293f9c803802",
            "key": "VTY-CON",
            "regex": "None",
            "python_code": 'regexes=[\r\n"user-interface vty 0 4\\n"\\\r\n" acl 2014 inbound\\n"\\\r\n" acl 2015 outbound\\n"\\\r\n" authentication-mode aaa\\n"\\\r\n" user privilege level 1\\n"\\\r\n" idle-timeout 9 0\\n"\\\r\n" screen-length 32\\n"\\\r\n" protocol inbound ssh",\r\n"user-interface con 0\\n"\\\r\n" acl 2015 outbound\\n"\\\r\n" authentication-mode aaa\\n"\\\r\n" user privilege level 1\\n"\\\r\n" idle-timeout 9 0",\r\n]\r\nvalidated=True\r\nfor regex in regexes:\r\n    if not re.search(regex,config):\r\n        validated=False\r\n        print ("Niet gevonden,",regex)',
            "remediation_commands": "None",
            "vendor": "huawei",
            "business_service": "VPN",
            "device_model": "All",
            "replaces_parent_check": "None",
            "has_child_check": False,
            "active": True,
        },
        {
            "id": "86e2104d-e86d-48d1-9b67-665b44b13cb0",
            "key": "dingen-die-je-uitzet",
            "regex": "None",
            "python_code": 'regexes=[\r\n#Deze services moeten uit staan (undo) of juist aan staan (regel moet wel voorkomen).\r\n"undo ntp-service enable",\r\n"header shell information",\r\n"header login information",\r\n#"icmp port-unreachable send",\r\n"icmp rate-limit enable",\r\n"set cpu-usage threshold 95 restore 90",\r\n"dns domain mrs",\r\n]\r\n#Deze services mogen niet aan staan (regel mag niet voorkomen)\r\nneg_regexes=[\r\n"snmp-agent community write",\r\n"hwtacacs-server timer response-timeout",\r\n"ssh server authentication-retries",\r\n"ssh server timeout",\r\n"arp-proxy",\r\n"dns resolve",\r\n"ipv6",\r\n" telnet server enable",\r\n" ftp server enable",\r\n"http server enable",\r\n"http secure-server enable",\r\n"lldp enable",\r\n"autoconfig enable",\r\n"autostart enable",\r\n"autoupdate enable",\r\n"ssh server compatible-ssh1x enable",\r\n]\r\nvalidated=True\r\nfor regex in regexes:\r\n    if not re.search(regex,config):\r\n        validated=False\r\n        print ("Niet gevonden", regex.replace(\\\'\\n\\\', \\\'\\\'))\r\nfor regex in neg_regexes:\r\n    if re.search(regex,config):\r\n        validated=False\r\n        print ("Gevonden maar zou er niet moeten zijn", regex.replace(\\\'\\n\\\', \\\'\\\'))',
            "remediation_commands": "None",
            "vendor": "huawei",
            "business_service": "VPN",
            "device_model": "All",
            "replaces_parent_check": "None",
            "has_child_check": False,
            "active": True,
        },
        {
            "id": "1ed9577a-0712-4bfe-afd5-cd69adb310a9",
            "key": "start-end-markers",
            "regex": "None",
            "python_code": 'regexes=[\r\n"\\[V",\r\n"return",\r\n" sysname ",\r\n]\r\nvalidated=True\r\nfor regex in regexes:\r\n    if not re.search(regex,config):\r\n        validated=False\r\n        print ("Niet gevonden,",regex)',
            "remediation_commands": "None",
            "vendor": "huawei",
            "business_service": "VPN",
            "device_model": "All",
            "replaces_parent_check": "None",
            "has_child_check": False,
            "active": True,
        },
        {
            "id": "d266f855-84bb-4c81-a413-b269057b6e97",
            "key": "Telnet-SSH-FTP",
            "regex": "None",
            "python_code": 'regexes=[\r\n\t"stelnet server enable",\r\n\t"sftp server enable",\r\n]\r\nvalidated=True\r\nfor regex in regexes:\r\n    if not re.search(regex,config):\r\n        validated=False\r\n        print ("Niet gevonden,",regex)',
            "remediation_commands": "None",
            "vendor": "huawei",
            "business_service": "VPN",
            "device_model": "All",
            "replaces_parent_check": "None",
            "has_child_check": False,
            "active": True,
        },
        {
            "id": "85e18031-e85e-42ba-a094-0c602f86fb88",
            "key": "Line 2",
            "regex": "None",
            "python_code": 'regexes=[\r\n"line 2",\r\n]\r\nvalidated=True\r\nfor regex in regexes:\r\n    if re.search(regex,config):\r\n        validated=True\r\n        regexes=[\r\n\t\t"line 2\\n"\\\r\n        "( no activation-character\\n)?"\\\r\n        " no exec\\n"\\\r\n        "( transport preferred none\\n)?"\\\r\n        "( transport input none\\n)?"\\\r\n        " transport output none\\n"\\\r\n        " stopbits 1\\n"\\\r\n        ]\r\n        for regex in regexes:\r\n            if not re.search(regex,config):\r\n                validated=False\r\n                print ("Line 2 onjuist geconfigureerd")\r\n        break',
            "remediation_commands": "None",
            "vendor": "cisco",
            "business_service": "VPN",
            "device_model": "All",
            "replaces_parent_check": "None",
            "has_child_check": False,
            "active": True,
        },
        {
            "id": "701da0b3-1cd2-45da-aa5c-824e2ba858d4",
            "key": "banners",
            "regex": "None",
            "python_code": 'regexes=[\r\n"banner exec",\r\n"banner login",\r\n"aaa authentication fail-message",\r\n]\r\nvalidated=True\r\nfor regex in regexes:\r\n    if not re.search(regex,config):\r\n        validated=False\r\n        print ("Niet gevonden,", regex)',
            "remediation_commands": "None",
            "vendor": "cisco",
            "business_service": "VPN",
            "device_model": "All",
            "replaces_parent_check": "None",
            "has_child_check": False,
            "active": True,
        },
        {
            "id": "ab36c215-7d64-4c40-ace0-b0e140ffff2c",
            "key": "Geldmaat specifiek",
            "regex": "None",
            "python_code": 'regexes=[\r\n"hostname gse.*",\r\n]\r\nvalidated=True\r\nfor regex in regexes:\r\n    if re.search(regex,config):\r\n        validated=True\r\n        regexes=[\r\n\t    "no ip forward-protocol nd",\r\n        "line con 0\\n"\\\r\n        "( exec-timeout 9 0\\n)?"\\\r\n        " password 7 .{10,55}\\n"\\\r\n        " no exec\\n"\\\r\n        " transport preferred none\\n"\\\r\n        "( transport input none\\n)?"\\\r\n        " transport output none\\n"\\\r\n        " stopbits 1",\r\n        "ip ssh server algorithm mac (hmac-sha2-512 hmac-sha2-256 hmac-sha1|hmac-sha1 hmac-sha2-256 hmac-sha2-512)",\r\n        ]\r\n        for regex in regexes:\r\n            if not re.search(regex,config):\r\n                validated=False\r\n                print (regex, "niet juist of niet gevonden")\r\n        break',
            "remediation_commands": "None",
            "vendor": "cisco",
            "business_service": "VPN",
            "device_model": "All",
            "replaces_parent_check": "None",
            "has_child_check": False,
            "active": True,
        },
        {
            "id": "a8008dd9-41b6-472e-a8eb-da754a542748",
            "key": "EEM-mobile-version-check",
            "regex": "None",
            "python_code": '#regexes=[\r\n#"(\\nevent manager applet Cellular-Modem-24Hrs-Down|"\\\r\n#"\\nevent manager applet Modem-Power-Cycle|"\\\r\n#"\\nevent manager applet Cellular-Modem-1Hrs-Up-)",\r\n#]\r\nvalidated=True\r\n#for regex in regexes:\r\n#    if re.search(regex,config):\r\n#        validated=True\r\n#        regexes=[\r\n#        "\\nevent manager applet Cellular-Modem-24Hrs-Down-V12",\r\n#        "\\nevent manager applet Modem-Power-Cycle-V12",\r\n#        "\\nevent manager applet Cellular-Modem-1Hrs-Up-V12",\r\n#        ]\r\n#        for regex in regexes:\r\n#            if not re.search(regex,config):\r\n#                validated=False\r\n#                print ("EEM script niet juiste versie")\r\n#        break',
            "remediation_commands": "None",
            "vendor": "cisco",
            "business_service": "VPN",
            "device_model": "All",
            "replaces_parent_check": "None",
            "has_child_check": False,
            "active": True,
        },
        {
            "id": "f5c0f1a8-0689-4fee-bdfd-7089c318bfd2",
            "key": "ACL93",
            "regex": "None",
            "python_code": 'validated=True\r\nfirst_check = False\r\nsecond_check = False\r\n\r\nfirst_check_regexes=[\r\n    "ip access-list standard 93\\n"\\\r\n    " 10 permit 193\\.172\\.69\\.0 0\\.0\\.0\\.127\\n"\\\r\n    " 20 permit 145\\.13\\.71\\.128 0\\.0\\.0\\.127\\n"\\\r\n    " 30 permit 145\\.13\\.76\\.0 0\\.0\\.0\\.255\\n"\\\r\n    " 40 deny[\\s]+any\\n",\r\n]\r\nfor regex in first_check_regexes:\r\n    if re.search(regex,config):\r\n        first_check = True\r\n\r\nsecond_check_regexes=[\r\n    "access-list 93 permit[\\s]+193\\.172\\.69\\.0 0\\.0\\.0\\.127\\n"\\\r\n    "access-list 93 permit[\\s]+145\\.13\\.71\\.128 0\\.0\\.0\\.127\\n"\\\r\n    "access-list 93 permit[\\s]+145\\.13\\.76\\.0 0\\.0\\.0\\.255\\n"\\\r\n    "access-list 93 deny[\\s]+any",\r\n]\r\nfor regex in second_check_regexes:\r\n    if re.search(regex,config):\r\n        second_check = True\r\n        \r\nif not first_check and not second_check:\r\n    validated = False\r\n    print ("ACL 93 niet aangetroffen of niet juist")',
            "remediation_commands": "None",
            "vendor": "cisco",
            "business_service": "VPN",
            "device_model": "All",
            "replaces_parent_check": "None",
            "has_child_check": False,
            "active": True,
        },
        {
            "id": "3f5fdc7a-1917-40f2-9b78-ec569e7cab2e",
            "key": "Line con 0",
            "regex": "None",
            "python_code": 'regex = \\\r\n"line con 0\\n"\\\r\n" exec-timeout 9 0\\n"\\\r\n" password 7 .{10,55}\\n"\\\r\n"( no modem enable\\n)?"\\\r\n"( no exec\\n)?"\\\r\n"( transport preferred none\\n)?"\\\r\n"( transport input (none|all)\\n)?"\\\r\n" transport output none\\n"\r\nvalidated=True\r\nif not re.search(regex,config):\r\n    validated=False\r\n    print ("Line con 0 niet gevonden of onjuist geconfigureerd.")',
            "remediation_commands": "None",
            "vendor": "cisco",
            "business_service": "VPN",
            "device_model": "All",
            "replaces_parent_check": "None",
            "has_child_check": False,
            "active": True,
        },
        {
            "id": "e6a1d7b0-dad2-4683-8381-4e87d2c6a534",
            "key": "Line aux 0",
            "regex": "None",
            "python_code": 'regexes=[\r\n"line aux 0\\n",\r\n]\r\nvalidated=True\r\nfor regex in regexes:\r\n    if re.search(regex,config):\r\n        validated=True\r\n        regexes=[\r\n\t\t"line aux 0\\n"\\\r\n        "( password 7 .{1,30}\\n)?"\\\r\n\t\t" no exec\\n"\\\r\n\t\t"( transport preferred none\\n)?"\\\r\n\t\t"( transport input none\\n)?"\\\r\n\t\t" transport output none\\n",\r\n        ]\r\n        for regex in regexes:\r\n            if not re.search(regex,config):\r\n                validated=False\r\n                print ("Line Aux 0 onjuist geconfigureerd")\r\n        break',
            "remediation_commands": "None",
            "vendor": "cisco",
            "business_service": "VPN",
            "device_model": "All",
            "replaces_parent_check": "None",
            "has_child_check": False,
            "active": True,
        },
        {
            "id": "03d46e98-5069-4b94-bb02-868415d3c3a1",
            "key": "WIFI-0",
            "regex": "None",
            "python_code": 'regexes=[\r\n"interface Wlan-Radio0/0/0",\r\n]\r\nvalidated=True\r\nfor regex in regexes:\r\n    if re.search(regex,config):\r\n        validated=True\r\n        regexes=[\r\n\t\t"interface Wlan-Radio0/0/0\\n undo radio enable",\r\n        ]\r\n        for regex in regexes:\r\n            if not re.search(regex,config):\r\n                validated=False\r\n                print ("Wifi niet uitgezet")\r\n        break',
            "remediation_commands": "None",
            "vendor": "huawei",
            "business_service": "VPN",
            "device_model": "All",
            "replaces_parent_check": "None",
            "has_child_check": False,
            "active": True,
        },
        {
            "id": "a94b6bde-319b-4f7c-ae5e-cec4a2fdbc70",
            "key": "vty 0 4 INS",
            "regex": "None",
            "python_code": 'regex = \\\r\n"line vty 0 4\\n"\\\r\n" access-class 15 in( vrf-also)?\\n"\\\r\n" exec-timeout 9 0\\n"\\\r\n" password 7 .{10,55}\\n"\\\r\n"( ipv6 access-class ACL1-v6 in\\n)?"\\\r\n"( no activation-character\\n)?"\\\r\n"( logging synchronous\\n)?"\\\r\n"( length 0\\n)?"\\\r\n"( transport preferred none\\n)?"\\\r\n" transport input ssh\\n"\\\r\n" transport output none"\r\nvalidated=True\r\nif not re.search(regex,config):\r\n    validated=False\r\n    print ("VTY 0 4 niet gevonden of onjuist geconfigureerd.")',
            "remediation_commands": "None",
            "vendor": "cisco",
            "business_service": "INS",
            "device_model": "All",
            "replaces_parent_check": "None",
            "has_child_check": False,
            "active": True,
        },
        {
            "id": "f01c2488-79e7-490e-bc10-cad34a71d1b5",
            "key": "Log-en-SNMP_24chr-VPN-H",
            "regex": "None",
            "python_code": 'regexes=[\r\n" snmp-agent sys-info contact KPN",\r\n" snmp-agent sys-info location KPN",\r\n" snmp-agent sys-info version (all|v2c v3)",\r\n" snmp-agent target-host trap-hostname rim-2-159 address 145.13.76.159 udp-port 162 trap-paramsname snmp_trap_community\\n",\r\n" snmp-agent target-host trap-hostname rim-2-(0)?33 address 145.13.76.33 udp-port 162 trap-paramsname snmp_trap_community\\n",\r\n" snmp-agent target-host trap-paramsname snmp_trap_community v2c securityname .{66,70}\\n",\r\n" snmp-agent trap enable syslog",\r\n" snmp-agent",\r\n]\r\n\r\nsnmp_community_regex = r"snmp-agent community read .* \\w+\\s(?P<acl_number>\\d+)"\r\n\r\nvalidated=True\r\nfor regex in regexes:\r\n    if not re.search(regex,config):\r\n        validated=False\r\n        print ("Niet gevonden,",regex)\r\n        \r\ncount_occurences_in_config = re.findall(snmp_community_regex, config)\r\ntscm_occurences_count = count_occurences_in_config.count("2093")\r\nif tscm_occurences_count < 2 or tscm_occurences_count > 2:\r\n    validated=False\r\n    print(f"Teveel of te weinig community strings op acl 2093\\\'s gevonden: {tscm_occurences_count} in plaats van 2")',
            "remediation_commands": "",
            "vendor": "huawei",
            "business_service": "VPN",
            "device_model": "All",
            "replaces_parent_check": "None",
            "has_child_check": False,
            "active": True,
        },
        {
            "id": "c623c0fd-a033-47a0-a4e7-0c2235ea6fe1",
            "key": "Checks voor IOS 15.x",
            "regex": "None",
            "python_code": 'regexes=[\r\n"version 15\\.8\\n",\r\n]\r\nvalidated=True\r\nfor regex in regexes:\r\n    if re.search(regex,config):\r\n        validated=True\r\n        regexes=[\r\n        "boot-start-marker\\n"\\\r\n        "boot system flash(:| )"\\\r\n        "(c800-universalk9-mz.SPA.158-3.M6.bin|c880data-universalk9-mz.158-3.M6.bin|c900-universalk9-mz.SPA.158-3.M2.bin|ir800-universalk9-mz.SPA.158-3.M2a)\\n",\r\n\t    " transport preferred none\\n transport input ssh\\n transport output none\\n",\r\n        "ip ssh server algorithm mac hmac-sha2-512 hmac-sha2-256 hmac-sha1",\r\n        "ip ssh server algorithm encryption aes256-ctr aes192-ctr aes128-ctr",\r\n#       "no service password-recovery", deze gaat niet werken omdat niet alle hardware dit laten zien in de running config\r\n#       "no service password-recovery",\r\n        "logging snmp-trap emergencies",\r\n        "logging snmp-trap alerts",\r\n        "logging snmp-trap critical",\r\n        "logging snmp-trap errors",\r\n        "logging snmp-trap warnings",\r\n        "logging snmp-trap notifications",\r\n        "logging history notifications",\r\n#        "logging persistent immediate protected",\r\n        ]\r\n        for regex in regexes:\r\n            if not re.search(regex,config):\r\n                validated=False\r\n                print (regex, "niet gevonden")\r\n        break',
            "remediation_commands": "None",
            "vendor": "cisco",
            "business_service": "VPN",
            "device_model": "All",
            "replaces_parent_check": "None",
            "has_child_check": False,
            "active": True,
        },
        {
            "id": "a81af87a-3f21-4206-a517-a7b859768aaf",
            "key": "banners",
            "regex": "None",
            "python_code": 'regexes=[\r\n"banner exec",\r\n"banner login",\r\n"aaa authentication fail-message",\r\n]\r\nvalidated=True\r\nfor regex in regexes:\r\n    if not re.search(regex,config):\r\n        validated=False\r\n        print ("Niet gevonden,", regex)',
            "remediation_commands": "None",
            "vendor": "cisco",
            "business_service": "CI",
            "device_model": "All",
            "replaces_parent_check": "None",
            "has_child_check": False,
            "active": True,
        },
        {
            "id": "a253b9a3-bdbf-439d-b628-3404dbd87a1b",
            "key": "Line 2",
            "regex": "None",
            "python_code": 'regexes=[\r\n"line 2",\r\n]\r\nvalidated=True\r\nfor regex in regexes:\r\n    if re.search(regex,config):\r\n        validated=True\r\n        regexes=[\r\n\t\t"line 2\\n"\\\r\n        "( no activation-character\\n)?"\\\r\n        " no exec\\n"\\\r\n        "( transport preferred none\\n)?"\\\r\n        " transport output none\\n"\\\r\n        "( transport input none\\n)?"\\\r\n        " stopbits 1\\n"\\\r\n        ]\r\n        for regex in regexes:\r\n            if not re.search(regex,config):\r\n                validated=False\r\n                print ("Line 2 onjuist geconfigureerd")\r\n        break',
            "remediation_commands": "None",
            "vendor": "cisco",
            "business_service": "CI",
            "device_model": "All",
            "replaces_parent_check": "None",
            "has_child_check": False,
            "active": True,
        },
        {
            "id": "9674ba37-b75b-4430-9436-e58aaf8c62e5",
            "key": "VTY-0-4",
            "regex": "None",
            "python_code": 'regex = \\\r\n"line vty 0 4\\n"\\\r\n" access-class 14 in\\n"\\\r\n" exec-timeout 9 0\\n"\\\r\n" password 7 .{10,55}\\n"\\\r\n"( ipv6 access-class ipv6_acl14 in\\n)?"\\\r\n"( logging synchronous\\n)?"\\\r\n"( notify\\n)?"\\\r\n"( transport preferred none\\n)?"\\\r\n" transport input ssh\\n"\\\r\n" transport output none"\r\nvalidated=True\r\nif not re.search(regex,config):\r\n    validated=False\r\n    print ("VTY 0 4 niet gevonden of onjuist geconfigureerd.")',
            "remediation_commands": "None",
            "vendor": "cisco",
            "business_service": "CI",
            "device_model": "All",
            "replaces_parent_check": "None",
            "has_child_check": False,
            "active": True,
        },
        {
            "id": "beb4eae0-8176-4251-b747-a66b2309b9ab",
            "key": "start-end-markers",
            "regex": "None",
            "python_code": 'regexes=[\r\n    "hostname (.*)",\r\n\t"end",\r\n]\r\nvalidated=True\r\nfor regex in regexes:\r\n    if not re.search(regex,config):\r\n        validated=False\r\n        print ("Config niet compleet geladen!")',
            "remediation_commands": "None",
            "vendor": "cisco",
            "business_service": "CI",
            "device_model": "All",
            "replaces_parent_check": "None",
            "has_child_check": False,
            "active": True,
        },
        {
            "id": "ef06c950-4ec5-4062-a049-bd887d1467c6",
            "key": "ACL10",
            "regex": "None",
            "python_code": 'validated=True\r\nfirst_check = False\r\nsecond_check = False\r\n\r\nfirst_check_regexes=[\r\n    "ip access-list standard 10\\n"\\\r\n    " 10 permit 145\\.13\\.76\\.0 0\\.0\\.0\\.255\\n"\\\r\n    " 20 permit[\\s]+193\\.172\\.69\\.64 0\\.0\\.0\\.31\\n"\\\r\n    " 30 permit[\\s]+193\\.172\\.69\\.96 0\\.0\\.0\\.31\\n"\\\r\n    " 40 deny[\\s]+any",\r\n]\r\nfor regex in first_check_regexes:\r\n    # added config it not None and  to the check because for xxxx\r\n    if re.search(regex,config):\r\n        first_check = True\r\n\r\nsecond_check_regexes=[\r\n    "access-list 10 permit[\\s]+145\\.13\\.76\\.0 0\\.0\\.0\\.255\\n"\\\r\n    "access-list 10 permit[\\s]+193\\.172\\.69\\.64 0\\.0\\.0\\.31\\n"\\\r\n    "access-list 10 permit[\\s]+193\\.172\\.69\\.96 0\\.0\\.0\\.31\\n"\\\r\n    "access-list 10 deny[\\s]+any",\r\n]\r\nfor regex in second_check_regexes:\r\n    if re.search(regex,config):\r\n        second_check = True\r\n\r\nif not first_check and not second_check:\r\n    validated = False\r\n    print ("ACL 10 niet aangetroffen of niet juist")',
            "remediation_commands": "None",
            "vendor": "cisco",
            "business_service": "CI",
            "device_model": "All",
            "replaces_parent_check": "None",
            "has_child_check": False,
            "active": True,
        },
        {
            "id": "53bec588-4003-4426-8ecf-4a47445c8b70",
            "key": "ip-ssh",
            "regex": "None",
            "python_code": 'regexes=[\r\n"( ip ssh time-out 60)?",\r\n"( ip ssh logging events)?",\r\n"ip ssh version 2",\r\n#\t"ip ssh dh min size 2048", Uitgezet omdat nog niet iedere router dit ondersteund\r\n"\\nservice password-encryption",\r\n]\r\nvalidated=True\r\nfor regex in regexes:\r\n    if not re.search(regex,config):\r\n        validated=False\r\n        print("Niet gevonden", regex)',
            "remediation_commands": "None",
            "vendor": "cisco",
            "business_service": "CI",
            "device_model": "All",
            "replaces_parent_check": "None",
            "has_child_check": False,
            "active": True,
        },
        {
            "id": "c8c7f0f4-b0ae-4dfe-9ab0-e4f27d804113",
            "key": "WIFI-1",
            "regex": "None",
            "python_code": 'regexes=[\r\n"interface Wlan-Radio0/0/1",\r\n]\r\nvalidated=True\r\nfor regex in regexes:\r\n    if re.search(regex,config):\r\n        validated=True\r\n        regexes=[\r\n        "interface Wlan-Radio0/0/1\\n undo radio enable",\r\n        ]\r\n        for regex in regexes:\r\n            if not re.search(regex,config):\r\n                validated=False\r\n                print ("Wifi niet uitgezet")\r\n        break',
            "remediation_commands": "None",
            "vendor": "huawei",
            "business_service": "CI",
            "device_model": "All",
            "replaces_parent_check": "None",
            "has_child_check": False,
            "active": True,
        },
        {
            "id": "c38465f8-114f-4e2f-8e74-9625258c81a1",
            "key": "ACL14",
            "regex": "None",
            "python_code": 'validated=True\r\nfirst_check = False\r\nsecond_check = False\r\n\r\nfirst_check_regexes=[\r\n    "ip access-list standard 14\\n"\\\r\n    " 10 permit 193\\.172\\.69\\.64 0\\.0\\.0\\.63\\n"\\\r\n    "( 20 deny[\\s]+any\\n)?",\r\n]\r\nfor regex in first_check_regexes:\r\n    if re.search(regex,config):\r\n        first_check = True\r\n\r\nsecond_check_regexes=[\r\n    "access-list 14 permit[\\s]+193\\.172\\.69\\.64 0\\.0\\.0\\.63\\n"\\\r\n    "( access-list 14 deny[\\s]+any)?",\r\n]\r\nfor regex in second_check_regexes:\r\n    if re.search(regex,config):\r\n        second_check = True\r\n        \r\nif not first_check and not second_check:\r\n    validated = False\r\n    print ("ACL 14 niet aangetroffen of niet juist")',
            "remediation_commands": "None",
            "vendor": "cisco",
            "business_service": "CI",
            "device_model": "All",
            "replaces_parent_check": "None",
            "has_child_check": False,
            "active": True,
        },
        {
            "id": "5598b973-e041-4396-ba07-e56b3df98f4d",
            "key": "ACL99",
            "regex": "None",
            "python_code": 'validated=True\r\nfirst_check = False\r\nsecond_check = False\r\n\r\nfirst_check_regexes=[\r\n    "ip access-list standard 99\\n"\\\r\n    " 10 deny[\\s]+10\\.0\\.0\\.0 0\\.255\\.255\\.255\\n"\\\r\n    " 20 deny[\\s]+172\\.16\\.0\\.0 0\\.15\\.255\\.255\\n"\\\r\n    " 30 deny[\\s]+192\\.168\\.0\\.0 0\\.0\\.255\\.255\\n"\\\r\n    " 40 permit[\\s]+any",\r\n]\r\nfor regex in first_check_regexes:\r\n    if re.search(regex,config):\r\n        first_check = True\r\n\r\nsecond_check_regexes=[\r\n    "access-list 99 deny[\\s]+10\\.0\\.0\\.0 0\\.255\\.255\\.255\\n"\\\r\n    "access-list 99 deny[\\s]+172\\.16\\.0\\.0 0\\.15\\.255\\.255\\n"\\\r\n    "access-list 99 deny[\\s]+192\\.168\\.0\\.0 0\\.0\\.255\\.255\\n"\\\r\n    "(access-list 99 deny[\\s]+193\\.172\\.69\\.0 0\\.0\\.0\\.255\\n)?"\\\r\n    "access-list 99 permit[\\s]+any",\r\n]\r\nfor regex in second_check_regexes:\r\n    if re.search(regex,config):\r\n        second_check = True\r\n        \r\nif not first_check and not second_check:\r\n    validated = False\r\n    print ("ACL 99 niet aangetroffen of niet juist")',
            "remediation_commands": "None",
            "vendor": "cisco",
            "business_service": "CI",
            "device_model": "All",
            "replaces_parent_check": "None",
            "has_child_check": False,
            "active": True,
        },
        {
            "id": "e1442f9d-d9f2-46e4-abe1-6f5b8fd4689c",
            "key": "Line con 0",
            "regex": "None",
            "python_code": 'regex = \\\r\n"line con 0\\n"\\\r\n" exec-timeout 9 0\\n"\\\r\n" password 7 .{10,55}\\n"\\\r\n"( no modem enable\\n)?"\\\r\n"( notify\\n)?"\\\r\n"( transport preferred none\\n)?"\\\r\n"( transport input none\\n)?"\\\r\n" transport output none\\n"\r\nvalidated=True\r\nif not re.search(regex,config):\r\n    validated=False\r\n    print ("Line con 0 niet gevonden of onjuist geconfigureerd.")',
            "remediation_commands": "None",
            "vendor": "cisco",
            "business_service": "CI",
            "device_model": "All",
            "replaces_parent_check": "None",
            "has_child_check": False,
            "active": True,
        },
        {
            "id": "def0ead8-163d-46d7-a5bd-eaf28c713fa9",
            "key": "log-en-debug",
            "regex": "None",
            "python_code": 'validated=True\r\nlog_check = False\r\nlog_check_regexes=[\r\n    "service timestamps debug datetime msec localtime show-timezone",\r\n    "service timestamps log datetime msec localtime show-timezone\\n",\r\n    "clock timezone CET (1|1 0)\\n",\r\n    "clock summer-time CEST recurring last Sun Mar 2:00 last Sun Oct 3:00",\r\n    "logging history notifications",\r\n    "logging trap notifications",\r\n    "logging source-interface Loopback0",\r\n    "logging (host |)193\\.172\\.69\\.71",\r\n    "logging (host |)193\\.172\\.69\\.103",\r\n    "service password-encryption",\r\n]\r\nfor regex in log_check_regexes:\r\n    if re.search(regex,config):\r\n        first_check = True\r\n                \r\nif not log_check_regexes:\r\n    validated = False\r\n    print ("log en debug statements niet aangetroffen of niet juist")',
            "remediation_commands": "None",
            "vendor": "cisco",
            "business_service": "CI",
            "device_model": "All",
            "replaces_parent_check": "None",
            "has_child_check": False,
            "active": True,
        },
        {
            "id": "83a97b14-a2f3-4aa8-8219-3c89336de5a2",
            "key": "TACACS_settings",
            "regex": "None",
            "python_code": 'regexes=[\r\n"aaa new-model\\n",\r\n"aaa authentication login default group tacacs\\+ enable\\n",\r\n"aaa authentication enable default group tacacs\\+ enable\\n",\r\n"aaa authorization console\\n",\r\n"aaa authorization exec default group tacacs\\+ if-authenticated \\n",\r\n"aaa authorization commands 15 default group tacacs\\+ none \\n",\r\n"(aaa accounting exec default\\n action-type start-stop\\n group tacacs\\+\\n|aaa accounting exec default start-stop group tacacs\\+\\n)",\r\n"(aaa accounting commands 1 default\\n action-type start-stop\\n group tacacs\\+\\n|aaa accounting commands 1 default start-stop group tacacs\\+\\n)",\r\n"(aaa accounting commands 15 default\\n action-type start-stop\\n group tacacs\\+\\n|aaa accounting commands 15 default start-stop group tacacs\\+\\n)",\r\n"ip tacacs source-interface Loopback0( |)\\n",   \r\n]\r\nvalidated=True\r\nfor regex in regexes:\r\n    if not re.search(regex,config):\r\n        validated=False\r\n        print ("Niet gevonden:",regex)',
            "remediation_commands": "None",
            "vendor": "cisco",
            "business_service": "CI",
            "device_model": "All",
            "replaces_parent_check": "None",
            "has_child_check": False,
            "active": True,
        },
        {
            "id": "9a071616-3275-461b-9530-c89aa9e181d9",
            "key": "Line aux 0",
            "regex": "None",
            "python_code": 'regexes=[\r\n"line aux 0\\n",\r\n]\r\nvalidated=True\r\nfor regex in regexes:\r\n    if re.search(regex,config):\r\n        validated=True\r\n        regexes=[\r\n\t\t"line aux 0\\n"\\\r\n\t\t" no exec\\n"\\\r\n\t\t"( transport preferred none\\n)?"\\\r\n\t\t"( transport input none\\n)?"\\\r\n\t\t"( transport output none\\n)?",\r\n        ]\r\n        for regex in regexes:\r\n            if not re.search(regex,config):\r\n                validated=False\r\n                print ("Line Aux 0 onjuist geconfigureerd")\r\n        break',
            "remediation_commands": "None",
            "vendor": "cisco",
            "business_service": "CI",
            "device_model": "All",
            "replaces_parent_check": "None",
            "has_child_check": False,
            "active": True,
        },
        {
            "id": "dae8360d-cac1-43cc-99b9-846773848823",
            "key": "TACACS-servers",
            "regex": "None",
            "python_code": 'validated=True\r\n\r\nfirst_check = True\r\nsecond_check = True\r\nthird_check = True\r\n\r\nfirst_check_regexes=[\r\n"tacacs server pri-acs\\n address ipv4 193.172.69.74\\n key 7 .{1,40}",\r\n"tacacs server sec-acs\\n address ipv4 193.172.69.106\\n key 7 .{1,40}",\r\n]\r\nfor regex in first_check_regexes:\r\n    if not re.search(regex,config):\r\n        first_check = False\r\n\r\nsecond_check_regexes=[\r\n    "tacacs-server host 193.172.69.74\\n"\\\r\n    "tacacs-server host 193.172.69.106\\n"\\\r\n    "(no tacacs-server directed-request\\n)?"\\\r\n    "tacacs-server key 7 .{1,40}",\r\n]\r\n\r\nfor regex in second_check_regexes:\r\n    if not re.search(regex,config):\r\n        second_check = False\r\n\r\nthird_check_regexes=[\r\n\t"tacacs-server host 193.172.69.74 key 7 .{1,40}\\ntacacs-server host 193.172.69.106 key 7 .{1,40}",\r\n]\r\n\r\nfor regex in third_check_regexes:\r\n    if not re.search(regex,config):\r\n        third_check = False\r\n\r\nif not first_check and not second_check and not third_check:\r\n    validated = False\r\n    print ("Tacacs servers niet aangetroffen of niet compleet")',
            "remediation_commands": "None",
            "vendor": "cisco",
            "business_service": "CI",
            "device_model": "All",
            "replaces_parent_check": "None",
            "has_child_check": False,
            "active": True,
        },
        {
            "id": "962b810c-b410-48e2-a2bd-1241640a4d28",
            "key": "ACL-2015",
            "regex": "None",
            "python_code": 'regexes=[\r\n    "acl number 2015  \\n"\\\r\n    " description Outgoing user access\\n"\\\r\n    " rule 5 deny \\n",\r\n]\r\nvalidated=True\r\nfor regex in regexes:\r\n    if not re.search(regex,config):\r\n        validated=False\r\n        print ("Niet gevonden,",regex)',
            "remediation_commands": "None",
            "vendor": "huawei",
            "business_service": "VPN",
            "device_model": "All",
            "replaces_parent_check": "None",
            "has_child_check": False,
            "active": True,
        },
        {
            "id": "861e51d4-f228-4ea8-94a0-9cfd5ba04d43",
            "key": "WIFI-1",
            "regex": "None",
            "python_code": 'regexes=[\r\n"interface Wlan-Radio0/0/1",\r\n]\r\nvalidated=True\r\nfor regex in regexes:\r\n    if re.search(regex,config):\r\n        validated=True\r\n        regexes=[\r\n\t\t"interface Wlan-Radio0/0/1\\n undo radio enable",\r\n        ]\r\n        for regex in regexes:\r\n            if not re.search(regex,config):\r\n                validated=False\r\n                print ("Wifi niet uitgezet")\r\n        break',
            "remediation_commands": "None",
            "vendor": "huawei",
            "business_service": "VPN",
            "device_model": "All",
            "replaces_parent_check": "None",
            "has_child_check": False,
            "active": True,
        },
        {
            "id": "1b730774-38aa-460a-826a-985dd597b669",
            "key": "VTY-5-15",
            "regex": "None",
            "python_code": 'find_line_regex = [\r\n    "line vty 5",\r\n]\r\nvalidated = True\r\nfor regex in find_line_regex:\r\n    if re.search(regex, config):\r\n        validated = True\r\n        regexes = [\r\n            "line vty 5.{0,4}\\n" \\\r\n            " no exec\\n" \\\r\n            "( transport preferred none\\n)?" \\\r\n            " transport input none\\n" \\\r\n            " transport output none\\n",\r\n        ]\r\n        for regex in regexes:\r\n            if not re.search(regex, config):\r\n                validated = False\r\n                print("Line VTY 5 15 niet goed geconfigureerd.")',
            "remediation_commands": "None",
            "vendor": "cisco",
            "business_service": "CI",
            "device_model": "All",
            "replaces_parent_check": "None",
            "has_child_check": False,
            "active": True,
        },
        {
            "id": "34ea978d-fc2e-4259-bc8e-259fb7fa70e4",
            "key": "start-end-markers",
            "regex": "None",
            "python_code": 'regexes=[\r\n"\\[V",\r\n"return",\r\n" sysname ",\r\n]\r\nvalidated=True\r\nfor regex in regexes:\r\n    if not re.search(regex,config):\r\n        validated=False\r\n        print ("Niet gevonden,",regex)',
            "remediation_commands": "None",
            "vendor": "huawei",
            "business_service": "CI",
            "device_model": "All",
            "replaces_parent_check": "None",
            "has_child_check": False,
            "active": True,
        },
        {
            "id": "c9e48e18-fed5-4666-99b0-c7cf9b9e43ae",
            "key": "dingen-die-je-uitzet",
            "regex": "None",
            "python_code": 'regexes=[\r\n#Deze services moeten uit staan (undo) of juist aan staan (regel moet wel voorkomen).\r\n"undo ntp-service enable",\r\n"undo hwtacacs-server user-name domain-included",\r\n"header shell information",\r\n"header login information",\r\n#"dns domain mrs",\r\n]\r\n#Deze services mogen niet aan staan (regel mag niet voorkomen)\r\nneg_regexes=[\r\n#"arp-proxy",\r\n"dns resolve",\r\n"snmp-agent community write",\r\n"lldp enable",\r\n" ftp server enable",\r\n"http secure-server enable",\r\n" telnet server enable",\r\n"http server enable",\r\n"snmp-agent complexity-check disable",\r\n# is optie bij CI "dhcp enable",\r\n"autoconfig enable",\r\n"autostart enable",\r\n"autoupdate enable",\r\n"ssh server compatible-ssh1x enable",\r\n]\r\nvalidated=True\r\nfor regex in regexes:\r\n    if not re.search(regex,config):\r\n        validated=False\r\n        print ("Niet gevonden", regex.replace(\\\'\\n\\\', \\\'\\\'))\r\nfor regex in neg_regexes:\r\n    if re.search(regex,config):\r\n        validated=False\r\n        print ("Gevonden maar zou er niet moeten zijn", regex.replace(\\\'\\n\\\', \\\'\\\'))',
            "remediation_commands": "None",
            "vendor": "huawei",
            "business_service": "CI",
            "device_model": "All",
            "replaces_parent_check": "None",
            "has_child_check": False,
            "active": True,
        },
        {
            "id": "7bd08760-acd6-48c8-a19d-48ac1a07ac61",
            "key": "SNMP-server",
            "regex": "None",
            "python_code": 'regexes=[\r\n#"snmp-server community .{11} (view exclvdsl2mib )?(view crash-block )?RO 10",\r\n#"snmp-server community .{11} (view exclvdsl2mib )?(view crash-block )?RO 10",\r\n#"snmp-server community .{16} (view exclvdsl2mib )?(view crash-block )?RO 10",\r\n"snmp-server community .{24} (view exclvdsl2mib )?(view crash-block )?RO 10",\r\n"snmp-server community .{24} (view exclvdsl2mib )?(view crash-block )?RO 10",\r\n"snmp-server trap-source Loopback0",\r\n"snmp-server enable traps syslog",   \r\n#Uitcommented ivm RIM SL problemen\r\n#"snmp-server host 145.13.76.159 version 2c .{11}",\r\n#"snmp-server host 145.13.76.33 version 2c .{11}",\r\n"snmp-server host 145.13.76.159 version 2c .{24}",\r\n"snmp-server host 145.13.76.33 version 2c .{24}",\r\n]\r\nvalidated=True\r\nfor regex in regexes:\r\n    if not re.search(regex,config):\r\n        validated=False\r\n        print ("Niet gevonden", regex)',
            "remediation_commands": "",
            "vendor": "cisco",
            "business_service": "CI",
            "device_model": "All",
            "replaces_parent_check": "None",
            "has_child_check": False,
            "active": True,
        },
        {
            "id": "ef3951d0-55ad-4dec-b704-3212f0c21d6e",
            "key": "SNMP-server_24chr-CI-C",
            "regex": "None",
            "python_code": 'regexes=[\r\n"snmp-server community .{24} (view exclvdsl2mib )?(view crash-block )?RO 10",\r\n"snmp-server community .{24} (view exclvdsl2mib )?(view crash-block )?RO 10",\r\n"snmp-server host 145.13.76.159 version 2c .{24}",\r\n"snmp-server host 145.13.76.33 version 2c .{24}",\r\n]\r\nvalidated=True\r\nfor regex in regexes:\r\n    if not re.search(regex,config):\r\n        validated=False\r\n        print ("Niet gevonden", regex)',
            "remediation_commands": "",
            "vendor": "cisco",
            "business_service": "CI",
            "device_model": "All",
            "replaces_parent_check": "None",
            "has_child_check": False,
            "active": True,
        },
        {
            "id": "9746e5dc-b548-45d1-b284-7e6b69c591e8",
            "key": "ACL-3160",
            "regex": "None",
            "python_code": 'regexes=[\r\n    "acl number 3160  \\n"\\\r\n    " rule 5 deny ip destination .{7,15} .{7,15} \\n"\\\r\n    " rule 10 deny ip source .{7,15} .{7,15} \\n"\\\r\n    " rule 15 deny ip destination 193.172.69.0 0.0.0.127 \\n"\\\r\n    " rule 20 deny ip source 193.172.69.0 0.0.0.127 \\n"\\\r\n    " rule 25 deny ip destination 145.13.71.128 0.0.0.127 \\n"\\\r\n    " rule 30 deny ip source 145.13.71.128 0.0.0.127 \\n"\\\r\n    " rule 35 deny ip destination 145.13.76.0 0.0.0.255 \\n"\\\r\n    " rule 40 deny ip source 145.13.76.0 0.0.0.255 \\n"\\\r\n    " rule 45 permit ip",\r\n]\r\nvalidated=True\r\nfor regex in regexes:\r\n    if not re.search(regex,config):\r\n        validated=False\r\n        print ("ACL3166 niet gevonden of niet juist.")',
            "remediation_commands": "None",
            "vendor": "huawei",
            "business_service": "VPN",
            "device_model": "All",
            "replaces_parent_check": "None",
            "has_child_check": False,
            "active": True,
        },
        {
            "id": "d5851c13-5a3a-4370-bed5-05e0e7275439",
            "key": "ACL-3166",
            "regex": "None",
            "python_code": 'regexes=[\r\n    "acl number 3166  \\n"\\\r\n    " rule 5 permit ip source .{7,15} 0 destination 193.172.69.0 0.0.0.127 \\n"\\\r\n    " rule 10 permit ip source .{7,15} 0 destination 145.13.71.128 0.0.0.127 \\n"\\\r\n    " rule 15 permit ip source .{7,15} 0 destination 145.13.76.0 0.0.0.255 \\n"\\\r\n]\r\nvalidated=True\r\nfor regex in regexes:\r\n    if not re.search(regex,config):\r\n        validated=False\r\n        print ("ACL3166 niet gevonden of niet juist.")',
            "remediation_commands": "None",
            "vendor": "huawei",
            "business_service": "VPN",
            "device_model": "All",
            "replaces_parent_check": "None",
            "has_child_check": False,
            "active": True,
        },
        {
            "id": "daa5d51b-f100-40cb-9591-0e24d37b0a82",
            "key": "Telnet-SSH-FTP",
            "regex": "None",
            "python_code": 'regexes=[\r\n\t"stelnet server enable",\r\n]\r\nvalidated=True\r\nfor regex in regexes:\r\n    if not re.search(regex,config):\r\n        validated=False\r\n        print ("Niet gevonden,",regex)',
            "remediation_commands": "None",
            "vendor": "huawei",
            "business_service": "CI",
            "device_model": "All",
            "replaces_parent_check": "None",
            "has_child_check": False,
            "active": True,
        },
        {
            "id": "b8961199-a86d-4b18-ad8d-761b2168a78e",
            "key": "TACACS-settings",
            "regex": "None",
            "python_code": 'regexes=[\r\n"aaa\\n"\\\r\n" authentication-scheme default\\n"\\\r\n"  authentication-mode hwtacacs local\\n"\\\r\n"  authentication-super hwtacacs super\\n"\\\r\n" authentication-scheme radius\\n"\\\r\n"  authentication-mode radius\\n"\\\r\n" authorization-scheme default\\n"\\\r\n"  authorization-mode hwtacacs none\\n"\\\r\n"  authorization-cmd 1 hwtacacs none\\n"\\\r\n"  authorization-cmd 3 hwtacacs none\\n"\\\r\n"  authorization-cmd 15 hwtacacs none\\n"\\\r\n" accounting-scheme default\\n"\\\r\n"  accounting-mode hwtacacs\\n"\\\r\n"  accounting start-fail online\\n"\\\r\n" recording-scheme rscheme0\\n"\\\r\n"  recording-mode hwtacacs internet\\n"\\\r\n" cmd recording-scheme rscheme0\\n"\\\r\n" domain default\\n"\\\r\n"  authentication-scheme default\\n"\r\n"(  accounting-scheme default\\n)?"\\\r\n"  authorization-scheme default\\n"\\\r\n"(  radius-server default\\n)?"\\\r\n" domain default_admin\\n"\\\r\n"  authentication-scheme default\\n"\\\r\n"(  accounting-scheme default\\n)?"\\\r\n"  authorization-scheme default\\n"\\\r\n"  hwtacacs-server internet\\n"\\\r\n" local-user admin password irreversible-cipher .{40,60} access-limit 4\\n"\\\r\n" local-user admin privilege level 15\\n"\\\r\n" local-user admin service-type terminal ssh\\n",\r\n]\r\nvalidated=True\r\nfor regex in regexes:\r\n    if not re.search(regex,config):\r\n        validated=False\r\n        print ("Niet gevonden,",regex)',
            "remediation_commands": "None",
            "vendor": "huawei",
            "business_service": "CI",
            "device_model": "All",
            "replaces_parent_check": "None",
            "has_child_check": False,
            "active": True,
        },
        {
            "id": "13d73a6e-68ee-4457-bf56-472be574f984",
            "key": "TACACS-servers",
            "regex": "None",
            "python_code": 'regexes=[\r\n"hwtacacs-server template internet\\n\\\r\n hwtacacs-server authentication 193.172.69.74\\n\\\r\n hwtacacs-server authentication 193.172.69.106 secondary\\n\\\r\n hwtacacs-server authorization 193.172.69.74\\n\\\r\n hwtacacs-server authorization 193.172.69.106 secondary\\n\\\r\n hwtacacs-server accounting 193.172.69.74\\n\\\r\n hwtacacs-server accounting 193.172.69.106 secondary\\n\\\r\n( hwtacacs-server source-ip source-loopback 0\\n)?\\\r\n hwtacacs-server shared-key cipher .*?\\n\\\r\n undo hwtacacs-server user-name domain-included\\n"\r\n]\r\nvalidated=True\r\nfor regex in regexes:\r\n    if not re.search(regex,config):\r\n        validated=False\r\n        print ("niet gevonden",regex)',
            "remediation_commands": "None",
            "vendor": "huawei",
            "business_service": "CI",
            "device_model": "All",
            "replaces_parent_check": "None",
            "has_child_check": False,
            "active": True,
        },
        {
            "id": "98ad0e40-ca89-4db9-9be0-2f3756f22897",
            "key": "VTY-CON",
            "regex": "None",
            "python_code": '# definitie van regexes\r\nregexes = [\r\n    "\\nipv6\\n",\r\n]\r\n\r\ndualstack_regexes = [\r\n    "acl ipv6 number 2014  \\n"\\\r\n    " rule 5 deny \\n",\r\n    "acl ipv6 number 2015  \\n"\\\r\n    " rule 5 deny \\n",\r\n    "user-interface vty 0 4\\n"\\\r\n    " acl ipv6 2014 inbound\\n"\\\r\n    " acl ipv6 2015 outbound\\n"\\\r\n    " acl 2014 inbound\\n"\\\r\n    " acl 2015 outbound\\n"\\\r\n    " authentication-mode aaa\\n"\\\r\n    " user privilege level 1\\n"\\\r\n    " idle-timeout 9 0\\n"\\\r\n    " screen-length 32\\n"\\\r\n    " protocol inbound ssh",\r\n    "user-interface con 0\\n"\\\r\n    " acl ipv6 2015 outbound\\n"\\\r\n    " acl 2015 outbound\\n"\\\r\n    " authentication-mode aaa\\n"\\\r\n    " user privilege level 1\\n"\\\r\n    " idle-timeout 9 0",\r\n]\r\n# logic starts here\r\nfor regex in regexes:\r\n    if re.search(regex, config):\r\n        for dualstack_regex in dualstack_regexes:\r\n            if re.search(dualstack_regex, config):\r\n                validated = True\r\n            else:\r\n                validated = False\r\n                print("Dualstack line vty 0 4 en of con 0 niet aangetroffen of niet juist")\r\n    else:\r\n        validated = True\r\n        ipv4only = False\r\n        ipv4only_regexes = [\r\n            "user-interface vty 0 4\\n"\\\r\n            " acl 2014 inbound\\n"\\\r\n            " acl 2015 outbound\\n"\\\r\n            " authentication-mode aaa\\n"\\\r\n            " user privilege level 1\\n"\\\r\n            " idle-timeout 9 0\\n"\\\r\n            " screen-length 32\\n"\\\r\n            " protocol inbound ssh",\r\n            "user-interface con 0\\n"\\\r\n            " acl 2015 outbound\\n"\\\r\n            " authentication-mode aaa\\n"\\\r\n            " user privilege level 1\\n"\\\r\n            " idle-timeout 9 0",\r\n        ]\r\n        for ipv4only_regex in ipv4only_regexes:\r\n            if re.search(ipv4only_regex, config):\r\n                ipv4only = True\r\n\r\n            else:\r\n                validated = False\r\n                print("Line vty 0 4 en of con 0 niet aangetroffen of niet juist")',
            "remediation_commands": "None",
            "vendor": "huawei",
            "business_service": "CI",
            "device_model": "All",
            "replaces_parent_check": "None",
            "has_child_check": False,
            "active": True,
        },
        {
            "id": "47a87047-ee60-40c3-a07d-9f58bc2f9a12",
            "key": "Log-en-SNMP",
            "regex": "None",
            "python_code": 'regexes=[\r\n" info-center logbuffer size 1024",\r\n" info-center logfile size 4",\r\n" info-center max-logfile-number 2",\r\n" info-center source default channel 0 log state[\\s]+off trap state off debug state off",\r\n" info-center source default channel 1 log level notification trap state off( debug state on)?",\r\n" info-center loghost source LoopBack0",\r\n" info-center source default channel 6 log level notification trap state off",\r\n" info-center loghost 193.172.69.71 channel 6",\r\n" info-center loghost 193.172.69.103 channel 6",\r\n" info-center timestamp debugging date precision-time tenth-second",\r\n#Hieronder zijn defaults\r\n#" info-center timestamp log date",\r\n#" undo lldp enable",\r\n" snmp-agent community read .{0,200} acl 2010",\r\n" snmp-agent sys-info contact KPN",\r\n" snmp-agent sys-info location KPN",\r\n" snmp-agent sys-info version (all|v2c v3)",\r\n" snmp-agent",\r\n]\r\nvalidated=True\r\nfor regex in regexes:\r\n    if not re.search(regex,config):\r\n        validated=False\r\n        print ("Niet gevonden,",regex)',
            "remediation_commands": "None",
            "vendor": "huawei",
            "business_service": "CI",
            "device_model": "All",
            "replaces_parent_check": "None",
            "has_child_check": False,
            "active": True,
        },
        {
            "id": "9698ed7a-542c-47b8-8fdb-efcc4acde605",
            "key": "ACL-2014",
            "regex": "None",
            "python_code": 'regexes=[\r\n    "acl number 2014  \\n"\\\r\n    " rule 5 permit source 193\\.172\\.69\\.64 0\\.0\\.0\\.63 \\n"\\\r\n    " rule 99 deny \\n",\r\n]\r\nvalidated=True\r\nfor regex in regexes:\r\n    if not re.search(regex,config):\r\n        validated=False\r\n        print ("Niet gevonden,",regex)',
            "remediation_commands": "None",
            "vendor": "huawei",
            "business_service": "CI",
            "device_model": "All",
            "replaces_parent_check": "None",
            "has_child_check": False,
            "active": True,
        },
        {
            "id": "0abf7aac-4076-481f-883c-3d0a810891c5",
            "key": "ACL-2015",
            "regex": "None",
            "python_code": 'regexes=[\r\n    "acl number 2015  \\n"\\\r\n    " rule 5 deny \\n",\r\n]\r\nvalidated=True\r\nfor regex in regexes:\r\n    if not re.search(regex,config):\r\n        validated=False\r\n        print ("Niet gevonden,",regex)',
            "remediation_commands": "None",
            "vendor": "huawei",
            "business_service": "CI",
            "device_model": "All",
            "replaces_parent_check": "None",
            "has_child_check": False,
            "active": True,
        },
        {
            "id": "4f937c06-a5f1-4e1a-af80-33b05b08cb96",
            "key": "WIFI-0",
            "regex": "None",
            "python_code": 'regexes=[\r\n"interface Wlan-Radio0/0/0",\r\n]\r\nvalidated=True\r\nfor regex in regexes:\r\n    if re.search(regex,config):\r\n        validated=True\r\n        regexes=[\r\n\t\t"interface Wlan-Radio0/0/0\\n undo radio enable",\r\n        ]\r\n        for regex in regexes:\r\n            if not re.search(regex,config):\r\n                validated=False\r\n                print ("Wifi niet uitgezet")\r\n        break',
            "remediation_commands": "None",
            "vendor": "huawei",
            "business_service": "CI",
            "device_model": "All",
            "replaces_parent_check": "None",
            "has_child_check": False,
            "active": True,
        },
        {
            "id": "ae287a6d-866a-4ecb-9be0-e239f075e036",
            "key": "ACL-2010",
            "regex": "None",
            "python_code": 'regexes=[\r\n    "acl number 2010  \\n"\\\r\n    " rule 5 permit source 145.13.76.0 0.0.0.255 \\n"\\\r\n    " rule 10 permit source 193.172.69.64 0.0.0.31 \\n"\\\r\n    " rule 15 permit source 193.172.69.96 0.0.0.31 \\n"\\\r\n    " rule 20 deny \\n",\r\n    ]\r\nvalidated=True\r\nfor regex in regexes:\r\n    if not re.search(regex,config):\r\n        validated=False\r\n        print ("Niet gevonden,",regex)',
            "remediation_commands": "None",
            "vendor": "huawei",
            "business_service": "CI",
            "device_model": "All",
            "replaces_parent_check": "None",
            "has_child_check": False,
            "active": True,
        },
        {
            "id": "0e4a8114-5468-4a69-9e8e-b0a2088c6299",
            "key": "Log-en-SNMP_24chr-CI-H",
            "regex": "None",
            "python_code": 'regexes=[\r\n" snmp-agent sys-info contact KPN",\r\n" snmp-agent sys-info location KPN",\r\n" snmp-agent sys-info version (all|v2c v3)",\r\n" snmp-agent target-host trap-hostname rim-2-159 address 145.13.76.159 udp-port 162 trap-paramsname snmp_trap_community\\n",\r\n" snmp-agent target-host trap-hostname rim-2-(0)?33 address 145.13.76.33 udp-port 162 trap-paramsname snmp_trap_community\\n",\r\n" snmp-agent target-host trap-paramsname snmp_trap_community v2c securityname .{40,80}\\n",\r\n" snmp-agent",\r\n]\r\n\r\nsnmp_community_regex = r"snmp-agent community read .* \\w+\\s(?P<acl_number>\\d+)"\r\n\r\nvalidated=True\r\nfor regex in regexes:\r\n    if not re.search(regex,config):\r\n        validated=False\r\n        print ("Niet gevonden,",regex)\r\n        \r\ncount_occurences_in_config = re.findall(snmp_community_regex, config)\r\ntscm_occurences_count = count_occurences_in_config.count("2010")\r\nif tscm_occurences_count < 2 or tscm_occurences_count > 2:\r\n    validated=False\r\n    print(f"Teveel of te weinig community strings op acl 2010\\\'s gevonden: {tscm_occurences_count} in plaats van 2")',
            "remediation_commands": "",
            "vendor": "huawei",
            "business_service": "CI",
            "device_model": "All",
            "replaces_parent_check": "None",
            "has_child_check": False,
            "active": True,
        },
        {
            "id": "777b0545-e181-4bce-acdb-83d6a1d64b32",
            "key": "Log-en-SNMP",
            "regex": "None",
            "python_code": 'regexes=[\r\n" info-center logbuffer size 1024",\r\n" info-center trapbuffer size 1024",\r\n" info-center logfile size (4|32)",\r\n" info-center max-logfile-number 2",\r\n" info-center source default channel 0 log state[\\s]+off trap state off debug state off",\r\n" info-center source default channel 1 log level notification trap state off( debug state on)?",\r\n" info-center source default channel 5 trap level notification",\r\n" info-center source default channel 6 log level notification trap state off",\r\n" info-center loghost 193.172.69.78 channel 6",\r\n" info-center loghost 193.172.69.110 channel 6",\r\n" info-center timestamp debugging date precision-time tenth-second",\r\n#Hieronder zijn defaults\r\n#" info-center timestamp log date",\r\n#" undo lldp enable",\r\n" snmp-agent complexity-check disable",\r\n"""( snmp-agent community read .{0,200} acl 2093|\r\n snmp-agent community read .{0,200} acl 2093\\n\r\n snmp-agent community read .{86,90} acl 2093\\n snmp-agent community read .{86,90} acl 2093|\r\n snmp-agent community read .{86,90} acl 2093\\n snmp-agent community read .{86,90} acl 2093)""",\r\n" snmp-agent sys-info contact KPN",\r\n" snmp-agent sys-info location KPN",\r\n" snmp-agent sys-info version (all|v2c v3)",\r\n"( snmp-agent target-host trap-paramsname snmp_trap_community v2c securityname .{23,25})?",\r\n"""( snmp-agent target-host trap-hostname rim-2-159 address 145.13.76.159 udp-port 162 trap-paramsname .{1,30}|\r\n snmp-agent target-host trap-hostname rim-2-159 address 145.13.76.159 udp-port 162 trap-paramsname snmp_trap_community)""",\r\n"""( snmp-agent target-host trap-hostname rim-2-(0)?33 address 145.13.76.33 udp-port 162 trap-paramsname .{1,30}| \r\n snmp-agent target-host trap-hostname rim-2-(0)?33 address 145.13.76.33 udp-port 162 trap-paramsname snmp_trap_community)""",\r\n" snmp-agent trap enable syslog",\r\n" snmp-agent",\r\n]\r\nvalidated=True\r\nfor regex in regexes:\r\n    if not re.search(regex,config):\r\n        validated=False\r\n        print ("Niet gevonden,",regex)',
            "remediation_commands": "",
            "vendor": "huawei",
            "business_service": "VPN",
            "device_model": "All",
            "replaces_parent_check": "None",
            "has_child_check": False,
            "active": True,
        },
        {
            "id": "b5312b79-a6d7-4389-be4d-21eb1d9c73a2",
            "key": "ACL2-3",
            "regex": "None",
            "python_code": 'validated=True\r\nfirst_check = False\r\nsecond_check = False\r\n\r\nfirst_check_regexes=[\r\n    "ip access-list standard 2\\n"\\\r\n    " \\d+\\s+deny[\\s]+any\\n"\\\r\n    "ip access-list standard 3\\n"\\\r\n    " \\d+\\s+permit 193\\.172\\.69\\.107\\n"\\\r\n    " \\d+\\s+permit 193\\.172\\.69\\.75\\n"\\\r\n    " \\d+\\s+deny[\\s]+any\\n",\r\n]\r\nfor regex in first_check_regexes:\r\n    if re.search(regex,config):\r\n        first_check = True\r\n\r\ncheck_if_more_acl2_lines = \\\'^access-list 2 .*\\\'\r\nsecond_check_regexes=[\r\n    "access-list 2 deny[\\s]+any\\n"\\\r\n    "access-list 3 permit[\\s]+193\\.172\\.69\\.107\\n"\\\r\n    "access-list 3 permit[\\s]+193\\.172\\.69\\.75\\n"\\\r\n    "access-list 3 deny[\\s]+any",\r\n]\r\n# checks if there are no acl2 lines before the acl2 line in the second_check\r\nif len(re.findall(check_if_more_acl2_lines, config, flags=re.MULTILINE)) > 1:\r\n       second_check = False\r\n# now check the correctness of lines in second_check\r\nelse:\r\n    for regex in second_check_regexes:\r\n        if re.search(regex,config):\r\n            second_check = True\r\n        \r\nif not first_check and not second_check:\r\n    validated = False\r\n    print ("""  Een of meerdere onderstaande regels niet aangetroffen of niet juist:\r\n        access-list 2 deny any\r\n        access-list 3 permit 193.172.69.107\r\n        access-list 3 permit 193.172.69.75\r\n        access-list 3 deny any\r\n""")',
            "remediation_commands": "None",
            "vendor": "cisco",
            "business_service": "VPN",
            "device_model": "All",
            "replaces_parent_check": "None",
            "has_child_check": True,
            "active": True,
        },
        {
            "id": "21df3f12-1da8-4312-96ac-d13bd94973f4",
            "key": "ACL14",
            "regex": "None",
            "python_code": '# definitie van regexes\r\nregexes=[\r\n"hostname ing.*",\r\n]\r\n\r\nacl_14_ing=[\r\n    "access-list 14 permit[\\s]+193\\.172\\.69\\.0 0\\.0\\.0\\.(127|255)\\n"\\\r\n    "(access-list 14 permit[\\s]+212\\.84\\.0\\.0 0\\.0\\.0\\.127\\n)?"\\\r\n    "access-list 14 deny[\\s]+any",\r\n]\r\n# logic starts here\r\nfor regex in regexes:\r\n    if re.search(regex,config):\r\n        if re.search(acl_14_ing[0],config):\r\n            validated=True\r\n        else:\r\n            validated=False\r\n            print ("ACL 14 voor ING niet aangetroffen of niet juist")\r\n    else:\r\n        validated=True\r\n        first_check = False\r\n        second_check = False\r\n        first_check_regexes=[\r\n            "ip access-list standard 14\\n"\\\r\n            " 10 permit 193\\.172\\.69\\.0 0\\.0\\.0\\.127\\n"\\\r\n            " 20 deny[\\s]+any\\n",\r\n        ]\r\n        for regex in first_check_regexes:\r\n            if re.search(regex,config):\r\n                first_check = True\r\n        second_check_regexes=[\r\n#            "any\\n"\\\r\n            "access-list 14 permit[\\s]+193\\.172\\.69\\.0 0\\.0\\.0\\.(127|255)\\n"\\\r\n            "access-list 14 deny[\\s]+any",\r\n        ]\r\n        for regex in second_check_regexes:\r\n            if re.search(regex,config):\r\n                second_check = True\r\n                \r\n        if not first_check and not second_check:\r\n            validated = False\r\n            print ("ACL 14 niet aangetroffen of niet juist")',
            "remediation_commands": "None",
            "vendor": "cisco",
            "business_service": "VPN",
            "device_model": "All",
            "replaces_parent_check": "None",
            "has_child_check": False,
            "active": True,
        },
        {
            "id": "98be7982-027c-48ff-89a1-a7759f508ae6",
            "key": "dingen-die-je-uitzet",
            "regex": "None",
            "python_code": 'regexes=[\r\n#Deze services moeten uit staan (no) of juist aan staan.\r\n"privilege exec level 1 traceroute",\r\n"privilege exec level 1 ping",\r\n"no logging console",\r\n"no ip domain(-| )lookup",\r\n"no ip http server",\r\n"no ip http secure-server",\r\n"service password-encryption",\r\n]\r\n#Deze services mogen niet aan staan\r\nneg_regexes=[\r\n#Checks voor de event manager\r\n#TSD items\r\n#Uitgezet ivm nog veel voorkomen\r\n#"\\nip forward-protocol nd",\r\n"\\niox client enable",\r\n"\\ntacacs-server directed-request\\n",\r\n"\\nservice dhcp",\r\n"\\nip bootp server",\r\n"\\ncdp run",\r\n"\\nservice pad",\r\n"\\nip source-route",\r\n"ip identd",\r\n" RW ",\r\n"service config",\r\n"service udp-small-servers",\r\n"service tcp-small-servers",\r\n"service finger",\r\n"no ip subnet-zero",\r\n"no ip classless",\r\n#Router vervang acties\r\n"aaa authentication login CONSOLE none",\r\n"login authentication CONSOLE",\r\n"privilege level 15\\n",\r\n#Referenties naar de oude beheeromgeving\r\n"10.77.58.38",\r\n"10.77.58.20",\r\n"10.77.58.37",\r\n"10.77.58.21",\r\n"10.77.58.32",\r\n"10.77.58.16",\r\n#Al dan niet encrypte Cisco IDs\r\n"username cisco",\r\n"enable secret cisco",\r\n"username support secret",\r\n"7 045802150C2E\\n",\r\n"7 1511021F0725\\n",\r\n"7 00071A150754\\n",\r\n"7 060506324F41\\n",\r\n"7 094F471A1A0A\\n",\r\n"7 05080F1C2243\\n",\r\n"7 110A1016141D\\n",\r\n"7 121A0C041104\\n",\r\n"7 030752180500\\n",\r\n"7 070C285F4D06\\n",\r\n"7 13061E010803\\n",\r\n"7 14141B180F0B\\n",\r\n"7 104D000A0618\\n",\r\n"7 045802150C2E\\n",\r\n"7 01100F175804\\n",\r\n"7 0822455D0A16\\n",\r\n"7 02050D480809\\n",\r\n]\r\nvalidated=True\r\nfor regex in regexes:\r\n    if not re.search(regex,config):\r\n        validated=False\r\n        print ("Niet gevonden", regex.replace(\\\'\\n\\\', \\\'\\\'))\r\nfor regex in neg_regexes:\r\n    if re.search(regex,config):\r\n        validated=False\r\n        print ("Gevonden maar zou er niet moeten zijn", regex.replace(\\\'\\n\\\', \\\'\\\'))',
            "remediation_commands": "None",
            "vendor": "cisco",
            "business_service": "CI",
            "device_model": "All",
            "replaces_parent_check": "None",
            "has_child_check": False,
            "active": True,
        },
        {
            "id": "e254b366-949c-4c26-b9dd-310b2b257be2",
            "key": "log-en-debug",
            "regex": "None",
            "python_code": '# definitie van regexes\r\ning_router = [\r\n    "hostname ing.*",\r\n]\r\n\r\nlog_ing = [\r\n    "service timestamps debug datetime msec localtime show-timezone\\n",\r\n    "service timestamps log datetime msec localtime show-timezone\\n",\r\n    "logging origin-id hostname",\r\n    "logging (host |)193\\.172\\.69\\.78",\r\n    "logging (host |)193\\.172\\.69\\.110",\r\n    "service password-encryption",\r\n    "logging buffered",\r\n]\r\n# logic starts here\r\nfor regex in ing_router:\r\n    if re.search(regex, config):\r\n        for ing_regex in log_ing:\r\n            if re.search(ing_regex, config):\r\n                validated = True\r\n            else:\r\n                validated = False\r\n#                print("log en debug statements voor ING niet aangetroffen of niet juist")\r\n                print ("Niet gevonden,", ing_regex)\r\n    else:\r\n        validated = True\r\n        failed_checks = False\r\n        log_check_regexes = [\r\n            "service timestamps debug datetime msec localtime show-timezone",\r\n            "service timestamps log datetime msec localtime show-timezone",\r\n            "clock timezone CET (1|1 0)",\r\n            "clock summer-time CEST recurring last Sun Mar 2:00 last Sun Oct 3:00",\r\n            "logging origin-id hostname",\r\n            "logging (host |)193\\.172\\.69\\.78",\r\n            "logging (host |)193\\.172\\.69\\.110",\r\n            "service password-encryption",\r\n            "logging buffered",\r\n        ]\r\n        for regex in log_check_regexes:\r\n            if re.search(regex, config):\r\n                validated = True\r\n            else:\r\n                failed_checks = True\r\n#                print("log en debug statements niet correct")\r\n                print ("Niet gevonden,",regex)\r\n        if failed_checks:\r\n            validated = False',
            "remediation_commands": "None",
            "vendor": "cisco",
            "business_service": "VPN",
            "device_model": "All",
            "replaces_parent_check": "None",
            "has_child_check": False,
            "active": True,
        },
        {
            "id": "9131f032-5a8c-457a-b76f-78af060ba571",
            "key": "dingen-die-je-uitzet",
            "regex": "None",
            "python_code": 'regexes=[\r\n#Deze services moeten uit staan (no) of juist aan staan.\r\n"privilege exec level 1 traceroute",\r\n"privilege exec level 1 ping",\r\n#6-12-22"service tcp-keepalives-in",\r\n#6-12-22"service tcp-keepalives-out",\r\n"no logging console",\r\n"no ip domain(-| )lookup",\r\n"ip domain(-| )name mrs",\r\n"no ip http server",\r\n"no ip http secure-server",\r\n"service password-encryption",\r\n]\r\n#Deze services mogen niet aan staan\r\nneg_regexes=[\r\n#Checks voor de event manager\r\n"\\nevent manager applet Cellular-Modem-24Hrs-Down-V11",\r\n"\\nevent manager applet Modem-Power-Cycle-V11",\r\n"\\naction 218   cli command \\"do test Cellular0",\r\n#TSD items\r\n#Uitgezet ivm nog veel voorkomen\r\n#"\\nip forward-protocol nd",\r\n#6-12-22"\\nlogin on-success log",\r\n#6-12-22"\\niox client enable",\r\n#6-12-22"\\niox",\r\n#6-12-22"\\nipv6 ioam timestamp",\r\n"\\ntacacs-server directed-request\\n",\r\n"\\nservice pad",\r\n"\\nip source-route",\r\n"\\nservice dhcp",\r\n"\\nip bootp server",\r\n"\\ncdp run",\r\n"\\nservice pad",\r\n"lldp run\\n",\r\n"ip identd",\r\n" RW ",\r\n"service config",\r\n"service udp-small-servers",\r\n"service tcp-small-servers",\r\n"service finger",\r\n"\\ncall rsvp-sync",\r\n"no ip subnet-zero",\r\n"no ip classless",\r\n#Router vervang acties\r\n"aaa authentication login CONSOLE none",\r\n"login authentication CONSOLE",\r\n"privilege level 15\\n",\r\n#Referenties naar de oude beheeromgeving\r\n"ntp server 193.172.69.4( prefer)?\\n",\r\n"ntp server 193.172.69.6( prefer)?\\n",\r\n"ntp server 193.172.69.7( prefer)?\\n",\r\n"logging( host)? 193.172.69.26\\n",\r\n"logging( host)? 193.172.69.24\\n",\r\n"logging( host)? 193.172.69.6\\n",\r\n"logging( host)? 193.172.69.7\\n",\r\n"ip name-server 193.172.69.6 193.172.69.7\\n",\r\n"ip name-server 193.172.69.6\\n",\r\n"ip name-server 193.172.69.7\\n",\r\n"193.172.69.8\\n",\r\n"193.172.69.9\\n",\r\n#Al dan niet encrypte Cisco IDs\r\n"username cisco",\r\n"enable secret cisco",\r\n"7 045802150C2E\\n",\r\n"7 1511021F0725\\n",\r\n"7 00071A150754\\n",\r\n"7 060506324F41\\n",\r\n"7 094F471A1A0A\\n",\r\n"7 05080F1C2243\\n",\r\n"7 110A1016141D\\n",\r\n"7 121A0C041104\\n",\r\n"7 030752180500\\n",\r\n"7 070C285F4D06\\n",\r\n"7 13061E010803\\n",\r\n"7 14141B180F0B\\n",\r\n"7 104D000A0618\\n",\r\n"7 045802150C2E\\n",\r\n"7 01100F175804\\n",\r\n"7 0822455D0A16\\n",\r\n"7 02050D480809\\n",\r\n#Oude routering tbv dialer backup interface\r\n"set interface Null0 Cellular",\r\n]\r\nvalidated=True\r\nfor regex in regexes:\r\n    if not re.search(regex,config):\r\n        validated=False\r\n        print ("Niet gevonden", regex.replace(\\\'\\n\\\', \\\'\\\'))\r\nfor regex in neg_regexes:\r\n    if re.search(regex,config):\r\n        validated=False\r\n        print ("Gevonden maar zou er niet moeten zijn", regex.replace(\\\'\\n\\\', \\\'\\\'))',
            "remediation_commands": "None",
            "vendor": "cisco",
            "business_service": "VPN",
            "device_model": "All",
            "replaces_parent_check": "None",
            "has_child_check": False,
            "active": True,
        },
        {
            "id": "ee712051-cc0e-4c67-91a5-3a54fb1d20ec",
            "key": "NTP-Servers-Exception-3600",
            "regex": "None",
            "python_code": 'ntp_regex = "ntp server.*"\r\nip_sla_regex = "ip sla.*"\r\n\r\nvalidated=True\r\n# de qualys scanner meld dat deze ivm ntp kwetsbaar zijn en momenteel kunnen we de 3600\\\'s niet met een acl beschermen\r\n# dus het advies is om het uit te zetten daar waar het niet nodig is, vandaar de ip sla check want ip sla heeft ntp nodig.\r\nif not re.search(ip_sla_regex, config):\r\n    if re.search(ntp_regex, config):\r\n        validated=False\r\n        print ("NTP server config op een 3600 aangetroffen, deze cpe heeft geen ip sla, advies: gebruik no ntp om het weg te halen")',
            "remediation_commands": "None",
            "vendor": "cisco",
            "business_service": "VPN",
            "device_model": "3600",
            "replaces_parent_check": "NTP-Servers",
            "has_child_check": False,
            "active": True,
        },
        {
            "id": "3b1bd1d7-59f9-45aa-b752-bc854040ea24",
            "key": "NTP-Servers",
            "regex": "None",
            "python_code": 'regexes=[\r\n"(ntp source.*)?",\r\n"ntp access-group peer 3",\r\n"ntp access-group serve 2",\r\n"ntp access-group serve-only 2",\r\n"ntp access-group query-only 2\\n(ntp update-calendar|)",\r\n"ntp server 193.172.69.75 prefer",\r\n"ntp server 193.172.69.107",\r\n]\r\nvalidated=True\r\nfor regex in regexes:\r\n    if not re.search(regex,config):\r\n        validated=False\r\n        print ("Niet gevonden", regex)',
            "remediation_commands": "None",
            "vendor": "cisco",
            "business_service": "VPN",
            "device_model": "All",
            "replaces_parent_check": "None",
            "has_child_check": True,
            "active": True,
        },
        {
            "id": "f454854e-56d4-425f-b347-693111427c1e",
            "key": "ACL2-3-exception-3600",
            "regex": "None",
            "python_code": 'validated=True\r\nfirst_check = False\r\nsecond_check = False\r\n\r\nfirst_check_regexes=[\r\n    "access-list standard 2.*",\r\n    "access-list standard 3.*",\r\n]\r\n\r\nfor regex in first_check_regexes:\r\n    if re.search(regex,config):\r\n        first_check = True\r\n        \r\nfor regex in first_check_regexes:\r\n    if re.search(regex,config):\r\n        first_check = True\r\n\r\nsecond_check_regexes=[\r\n    "access-list 2.*",\r\n    "access-list 3.*",\r\n\r\n]\r\nfor regex in second_check_regexes:\r\n    if re.search(regex,config):\r\n        second_check = False\r\n\r\nif first_check or second_check:\r\n    validated = False\r\n    print ("ACL 2 en of 3 tbv NTP server zijn aangetroffen op een 3600. deze zijn overbodig, je mag het weghalen")',
            "remediation_commands": "None",
            "vendor": "cisco",
            "business_service": "VPN",
            "device_model": "3600",
            "replaces_parent_check": "ACL2-3",
            "has_child_check": False,
            "active": True,
        },
    ]


@pytest.fixture(name="raw_tscm_check_results")
def fx_raw_tscm_check_results() -> list[TSCMCheck | dict[str, Any]]:
    """Unstructured tscm check results representations."""
    return [
        {
            "device_id": "TESM1234",
            "date": datetime.datetime.now().astimezone()
            - datetime.timedelta(days=settings.tscm.MAXIMUM_CONFIG_AGE - 3),
            "is_online": False,
            "is_compliant": True,
        },
        {
            "device_id": "TESM1234",
            "date": datetime.datetime.now().astimezone()
            - datetime.timedelta(days=settings.tscm.MAXIMUM_CONFIG_AGE - 2),
            "is_online": True,
            "is_compliant": True,
        },
    ]


@pytest.fixture(name="raw_users")
def fx_raw_users() -> list[User | dict[str, Any]]:
    """Unstructured user representations."""

    return [
        {
            "id": "97108ac1-ffcb-411d-8b1e-d9183399f63b",
            "email": "superuser@example.com",
            "name": "Super User",
            "password": "Test_Password1!",
            "is_superuser": True,
            "is_active": True,
        },
        {
            "id": "5ef29f3c-3560-4d15-ba6b-a2e5c721e4d2",
            "email": "user@example.com",
            "name": "Example User",
            "password": "Test_Password2!",
            "is_superuser": False,
            "is_active": True,
        },
        {
            "id": "6ef29f3c-3560-4d15-ba6b-a2e5c721e4d3",
            "email": "another@example.com",
            "name": "The User",
            "password": "Test_Password3!",
            "is_superuser": False,
            "is_active": True,
        },
        {
            "id": "7ef29f3c-3560-4d15-ba6b-a2e5c721e4e1",
            "email": "inactive@example.com",
            "name": "Inactive User",
            "password": "Old_Password2!",
            "is_superuser": False,
            "is_active": False,
        },
    ]


@pytest.fixture(name="raw_teams")
def fx_raw_teams() -> list[Team | dict[str, Any]]:
    """Unstructured team representations."""

    return [
        {
            "id": "97108ac1-ffcb-411d-8b1e-d9183399f63b",
            "slug": "test-assessment-team",
            "name": "Test Assessment Team",
            "description": "This is a description for a migration team.",
            "owner_id": "6ef29f3c-3560-4d15-ba6b-a2e5c721e4d3",
        },
    ]


@pytest.fixture(name="raw_product_configurations")
def fx_raw_product_configurations() -> list[CPEProductConfiguration | dict[str, Any]]:
    """Unstructured CPE product configuration representations."""

    return [
        {
            "id": "76175388-5fb9-42ec-b42d-701e012ce7db",
            "description": "product configuration for a device",
            "configuration_id": 999999,
            "cpe_model": "3600",
            "vendor": "cisco",
        },
        {
            "id": "f5c6e2c5-07b6-4b2c-9adf-8f9f61d449ee",
            "description": "product configuration for a device",
            "configuration_id": 999990,
            "cpe_model": "887VAG",
            "vendor": "cisco",
        },
    ]


@pytest.fixture(name="tscm_obj")
def fx_tscm_obj() -> CpeTscmCheck:
    export_report = TscmExportReport()
    return CpeTscmCheck(
        device_id="TESM1234",
        tscm_checks=[],
        provided_config="",
        online_status=True,
        vendor="cisco",
        service="VPN",
        report=export_report,
    )


@pytest.fixture()
def _patch_sqlalchemy_plugin(is_unit_test: bool, monkeypatch: MonkeyPatch) -> None:
    if is_unit_test:
        from app.lib import db

        monkeypatch.setattr(
            db.config.SQLAlchemyConfig,  # type:ignore[attr-defined]
            "on_shutdown",
            MagicMock(),
        )


@pytest.fixture()
def _patch_worker(
    is_unit_test: bool,
    monkeypatch: MonkeyPatch,
    event_loop: Iterator[asyncio.AbstractEventLoop],
) -> None:
    """We don't want the worker to start for unit tests."""
    if is_unit_test:
        from app.lib import worker

        monkeypatch.setattr(worker.Worker, "on_app_startup", MagicMock())
        monkeypatch.setattr(worker.Worker, "stop", MagicMock())
    from app.lib.worker import commands

    monkeypatch.setattr(commands, "_create_event_loop", event_loop)


@pytest.fixture(name="cap_logger")
def fx_cap_logger(monkeypatch: MonkeyPatch) -> CapturingLogger:
    """Used to monkeypatch the app logger, so we can inspect output."""
    import app.lib

    app.lib.log.configure(
        app.lib.log.default_processors,  # type:ignore[arg-type]
    )
    # clear context for every test
    clear_contextvars()
    # pylint: disable=protected-access
    logger = app.lib.log.controller.LOGGER.bind()
    logger._logger = CapturingLogger()
    # drop rendering processor to get a dict, not bytes
    # noinspection PyProtectedMember
    logger._processors = app.lib.log.default_processors[:-1]
    monkeypatch.setattr(app.lib.log.controller, "LOGGER", logger)
    monkeypatch.setattr(app.lib.log.worker, "LOGGER", logger)
    return logger._logger
