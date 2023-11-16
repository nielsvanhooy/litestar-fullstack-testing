from typing import TYPE_CHECKING

import pytest
from app.domain.tscm.dependencies import provides_tscm_service
from app.lib.db.base import session

if TYPE_CHECKING:
    from app.domain.tscm.tscm import CpeTscmCheck


pytestmark = pytest.mark.anyio

# async def test_perform_tscm_check(client: "AsyncClient", superuser_token_headers: dict[str, str]) -> None:


async def test_returned_checks_with_replaced_parents() -> None:
    db = session()
    async with db as db_session:
        tscm_service = await anext(provides_tscm_service(db_session=db_session))
        checks = await tscm_service.vendor_product_checks("cisco", "VPN", "3600")
        assert checks[0].key == "ACL10"
        assert checks[1].key == "ACL2-3-exception-3600"


async def test_returned_checks_without_replaced_parents() -> None:
    db = session()
    async with db as db_session:
        tscm_service = await anext(provides_tscm_service(db_session=db_session))
        checks = await tscm_service.vendor_product_checks("cisco", "VPN", "3800")
        assert checks[0].key == "ACL10"
        assert checks[1].key == "ACL2-3"


async def test_tscm_config_age_compliant_below_minimum(tscm_obj: "CpeTscmCheck") -> None:
    config_age_compliant = tscm_obj.config_age_compliant(config_age=tscm_obj.MINIMUM_CONFIG_AGE - 1)
    assert config_age_compliant is True
    assert tscm_obj.is_compliant is True


async def test_tscm_config_age_compliant_above_minimum(tscm_obj: "CpeTscmCheck") -> None:
    config_age_compliant = tscm_obj.config_age_compliant(config_age=tscm_obj.MINIMUM_CONFIG_AGE + 1)
    assert config_age_compliant is False
    assert tscm_obj.is_compliant is False
    assert tscm_obj.export_report.tscm_doc[0].compliancy_reason == "CONFIG_OUT_OF_DATE"
    assert "config_age" in tscm_obj.tscm_email_doc.checks


async def test_tscm_config_age_compliant_above_maximum(tscm_obj: "CpeTscmCheck") -> None:
    config_age_compliant = tscm_obj.config_age_compliant(config_age=tscm_obj.MAXIMUM_CONFIG_AGE + 1)
    assert config_age_compliant is False


async def test_tscm_offline_compliant_not_compliant__offline_not_compliant(tscm_obj: "CpeTscmCheck") -> None:
    latest_compliancy = False
    tscm_obj.offline_compliant_not_compliant(latest_compliancy)

    assert tscm_obj.is_compliant is False
    assert tscm_obj.export_report.tscm_doc[0].compliancy_reason == "OFFLINE_NOT_COMPLIANT"


async def test_tscm_offline_compliant_not_compliant__offline_compliant(tscm_obj: "CpeTscmCheck") -> None:
    latest_compliancy = True
    tscm_obj.offline_compliant_not_compliant(latest_compliancy)

    assert tscm_obj.is_compliant is True
    assert tscm_obj.export_report.tscm_doc[0].compliancy_reason == "OFFLINE_COMPLIANT"
