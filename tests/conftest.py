from __future__ import annotations

import asyncio
import re
from typing import TYPE_CHECKING, Any
from unittest.mock import MagicMock

import pytest
from litestar.testing import TestClient
from structlog.contextvars import clear_contextvars
from structlog.testing import CapturingLogger

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
            "id": "b5312b79-a6d7-4389-be4d-21eb1d9c73a2",
            "key": "ACL2-3",
            "regex": "None",
            "python_code": 'validated=True\r\nfirst_check = False\r\nsecond_check = False\r\n\r\nfirst_check_regexes=[\r\n    "ip access-list standard 2\\n"\\\r\n    " \\d+\\s+deny[\\s]+any\\n"\\\r\n    "ip access-list standard 3\\n"\\\r\n    " \\d+\\s+permit 193\\.172\\.69\\.107\\n"\\\r\n    " \\d+\\s+permit 193\\.172\\.69\\.75\\n"\\\r\n    " \\d+\\s+deny[\\s]+any\\n",\r\n]\r\nfor regex in first_check_regexes:\r\n    if re.search(regex,config):\r\n        first_check = True\r\n\r\ncheck_if_more_acl2_lines = \'^access-list 2 .*\'\r\nsecond_check_regexes=[\r\n    "access-list 2 deny[\\s]+any\\n"\\\r\n    "access-list 3 permit[\\s]+193\\.172\\.69\\.107\\n"\\\r\n    "access-list 3 permit[\\s]+193\\.172\\.69\\.75\\n"\\\r\n    "access-list 3 deny[\\s]+any",\r\n]\r\n# checks if there are no acl2 lines before the acl2 line in the second_check\r\nif len(re.findall(check_if_more_acl2_lines, config, flags=re.MULTILINE)) > 1:\r\n       second_check = False\r\n# now check the correctness of lines in second_check\r\nelse:\r\n    for regex in second_check_regexes:\r\n        if re.search(regex,config):\r\n            second_check = True\r\n        \r\nif not first_check and not second_check:\r\n    validated = False\r\n    print ("""  Een of meerdere onderstaande regels niet aangetroffen of niet juist:\r\n        access-list 2 deny any\r\n        access-list 3 permit 193.172.69.107\r\n        access-list 3 permit 193.172.69.75\r\n        access-list 3 deny any\r\n""")',
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
        {
            "id": "5cf14ce8-76ec-4271-b587-cb6fb63f8ebd",
            "key": "TACACS_settings",
            "regex": "None",
            "python_code": 'regexes=[\r\n"aaa new-model\\n",\r\n"aaa authentication login default group tacacs\\+ enable\\n",\r\n"aaa authentication enable default group tacacs\\+ enable\\n",\r\n"aaa authorization console\\n",\r\n"aaa authorization exec default group tacacs\\+ if-authenticated \\n",\r\n"aaa authorization commands 15 default group tacacs\\+ none \\n",\r\n"(aaa accounting exec default\\n action-type start-stop\\n group tacacs\\+\\n|aaa accounting exec default start-stop group tacacs\\+\\n)",\r\n"(aaa accounting commands 1 default\\n action-type start-stop\\n group tacacs\\+\\n|aaa accounting commands 1 default start-stop group tacacs\\+\\n)",\r\n"(aaa accounting commands 15 default\\n action-type start-stop\\n group tacacs\\+\\n|aaa accounting commands 15 default start-stop group tacacs\\+\\n)",\r\n]\r\nvalidated=True\r\nfor regex in regexes:\r\n    if not re.search(regex,config):\r\n        validated=False\r\n        print ("Niet gevonden:",regex)',
            "remediation_commands": "None",
            "vendor": "huawei",
            "business_service": "VPN",
            "device_model": "All",
            "replaces_parent_check": "None",
            "has_child_check": False,
            "active": True,
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
        }
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
    is_unit_test: bool, monkeypatch: MonkeyPatch, event_loop: Iterator[asyncio.AbstractEventLoop]
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
        app.lib.log.default_processors  # type:ignore[arg-type]
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
