from __future__ import annotations

import datetime
import re
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from app.domain.tscm.helpers import stdoutio
from app.lib import settings

__all__ = ["TscmExportReport", "CpeTscmCheck", "TSCMDoc", "TSCMEmailDoc", "TSCMPerCheckDetailDoc"]


if TYPE_CHECKING:
    from app.domain.tscm.models import TSCMCheck


@dataclass
class TSCMEmailDoc:
    device_id: str | None = None
    is_compliant: bool | None = None
    checks: dict = field(default_factory=dict)


@dataclass
class TSCMPerCheckDetailDoc:
    _id: str
    vendor: str
    device_id: str
    check_key: str
    timestamp: str
    service: str
    is_compliant: bool = False
    deviation: str = ""
    output: str = ""
    error: str = ""


@dataclass
class TSCMDoc:
    _id: str
    date: str
    device_id: str
    service: str
    is_compliant: bool = False
    is_online: bool = False
    compliancy_reason: str = "NOT_ALL_CHECKS_PASSED"


class TscmExportReport:
    def __init__(self) -> None:
        self.tscm_doc: list[TSCMDoc] = []
        self.tscm_per_check_detail_result: list[TSCMPerCheckDetailDoc] = []

        self.timestamp = datetime.datetime.now().astimezone().strftime("%Y-%m-%d")

    def create_per_check_doc(
        self,
        vendor: str,
        device_id: str,
        service: str,
        check_is_compliant: bool,
        deviation: str,
        remediation: str,
        output: str,
        check: TSCMCheck,
    ) -> None:
        """Function is used to process the results from the TSCM checks.
        tscm_per_check_detail_result: details of the tscm check per check. can be used for exporting to Splunk/Elastic
        """

        per_check_detail_doc = TSCMPerCheckDetailDoc(
            _id=f"{self.timestamp}-{device_id}-{check.key}",
            vendor=vendor,
            device_id=device_id,
            check_key=check.key,
            timestamp=self.timestamp,
            service=service,
            is_compliant=check_is_compliant,
            deviation=deviation,
            output=output,
        )

        self.tscm_per_check_detail_result.append(per_check_detail_doc)

    def create_tscm_doc(
        self,
        device_id: str,
        service: str,
        is_compliant: bool,
        online_status: bool,
        reason: str = "",
    ) -> None:
        self.tscm_doc.append(
            TSCMDoc(
                _id=f"{self.timestamp}-{device_id}",
                date=self.timestamp,
                device_id=device_id,
                service=service,
                is_compliant=is_compliant,
                is_online=online_status,
                compliancy_reason=reason,
            )
        )

    def results(self) -> dict[str, TSCMEmailDoc | list | TSCMDoc | None]:
        return {
            "tscm_per_check_detail": self.tscm_per_check_detail_result,
            "tscm_doc": self.tscm_doc,
        }


class CpeTscmCheck:
    def __init__(
        self,
        device_id: str,
        tscm_checks: list[TSCMCheck],
        provided_config: str,
        online_status: bool,
        vendor: str,
        service: str,
        report: TscmExportReport,
    ):
        self.device_id = device_id
        self.tscm_checks = tscm_checks
        self.provided_config = provided_config
        self.online_status = online_status
        self.vendor = vendor
        self.service = service
        self.export_report = report

        self.MINIMUM_CONFIG_AGE: int = settings.tscm.MINIMUM_CONFIG_AGE
        self.MAXIMUM_CONFIG_AGE: int = settings.tscm.MAXIMUM_CONFIG_AGE

        self.remediation_instructions = {"device_id": self.device_id, "commands": []}

        # we start out with compliance is True. based on ruling we set it to False
        self.is_compliant = True

        # email results
        self.tscm_email_doc: TSCMEmailDoc = TSCMEmailDoc(device_id=self.device_id, is_compliant=self.is_compliant)

    def __repr__(self) -> str:
        return f"CpeTscmCheck({self.device_id})"

    def _validate(self, python_code: str, check_name: str) -> tuple[bool, str, str]:
        data = {
            "config": self.provided_config,
            "validated": False,
        }

        code = compile(python_code, check_name, "exec")
        allowed_builtins = {"__builtins__": {"re": re, "print": print, "len": len}}
        exec(code, allowed_builtins, data)  # noqa: S102

        is_validated = data.get("validated", False)
        deviation = data.get("deviation", "")
        remediation = data.get("remediation", "")

        return is_validated, deviation, remediation  # type: ignore[return-value]

    def config_age_compliant(self, config_age: int) -> bool:
        """Main TSCM Rule:

        If config older than MAXIMUM_CONFIG_AGE days: then we find the device not compliant

        if device is online and config age > MINIMUM_CONFIG_AGE days.
        then the device is marked as not compliant. network engineers should troubleshoot
        why the config is out of age (unreachable? disruption?)
        the result of this will we added to the v
        """
        if config_age > self.MAXIMUM_CONFIG_AGE:
            self.is_compliant = False
            return False

        if config_age > self.MINIMUM_CONFIG_AGE:
            self.is_compliant = False

            self.export_report.create_tscm_doc(
                device_id=self.device_id,
                service=self.service,
                is_compliant=self.is_compliant,
                online_status=self.online_status,
                reason="CONFIG_OUT_OF_DATE",
            )

            if self.online_status:
                self.tscm_email_doc.checks["config_age"] = {
                    "output": f"Device online but config older than expected ( currently {config_age} days!)"
                    f"no further checks have been performed due to config out of date\n",
                    "is_compliant": False,
                }
                self.tscm_email_doc.is_compliant = False

            return False
        return True

    def offline_compliant_not_compliant(self, latest_compliancy: bool) -> None:
        """2 TSCM Rules when CPE is offline (online_status = False)

        if device offline and device was compliant in the last MAXIMUM_CONFIG_AGE days: compliant
        if device offline and was not compliant in the last MAXIMUM_CONFIG_AGE days: not compliant
        """

        self.is_compliant = latest_compliancy
        reason = "OFFLINE_COMPLIANT" if self.is_compliant else "OFFLINE_NOT_COMPLIANT"

        self.export_report.create_tscm_doc(
            device_id=self.device_id,
            service=self.service,
            is_compliant=self.is_compliant,
            online_status=self.online_status,
            reason=reason,
        )

    def online_compliant_not_compliant(self) -> None:
        """2 TSCM rules when CPE is online.

        if device online and device not compliant: not compliant
        if device online and compliant in the last MAXIMUM_CONFIG_AGE: compliant
        """
        for check in self.tscm_checks:
            try:
                with stdoutio() as out:
                    check_is_compliant, deviation, remediation = self._validate(check.python_code, self.provided_config)
                    output = out.getvalue()
                    self.tscm_email_doc.checks[check.key] = {
                        "output": output,
                        "is_compliant": check_is_compliant,
                    }
                    self.export_report.create_per_check_doc(
                        vendor=self.vendor,
                        device_id=self.device_id,
                        service=self.service,
                        check_is_compliant=check_is_compliant,
                        deviation=deviation,
                        remediation=remediation,
                        output=output,
                        check=check,
                    )

                    # if one check is not compliant we set the global variable is_compliant to False
                    # hence the cpe is not compliant.
                    if not check_is_compliant:
                        self.is_compliant = False

            except Exception:
                import traceback

                traceback.print_exc()
        if self.is_compliant:
            self.export_report.create_tscm_doc(
                device_id=self.device_id,
                service=self.service,
                is_compliant=self.is_compliant,
                online_status=self.online_status,
                reason="ALL_CHECKS_PASSED",
            )
        else:
            self.export_report.create_tscm_doc(
                device_id=self.device_id,
                service=self.service,
                is_compliant=self.is_compliant,
                online_status=self.online_status,
                reason="NOT_ALL_CHECKS_HAVE_PASSED",
            )

        self.tscm_email_doc.is_compliant = self.is_compliant

    def get_email_results(self) -> TSCMEmailDoc:
        return self.tscm_email_doc
