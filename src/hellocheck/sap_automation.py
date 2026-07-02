from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .models import SapCommand, SapConfig


class SapAutomationError(RuntimeError):
    pass


@dataclass
class SapSessionAdapter:
    session: Any

    def find(self, field_id: str) -> Any:
        return self.session.FindById(field_id)


class SapAutomation:
    def __init__(self, config: SapConfig) -> None:
        self.config = config
        self._session_adapter: SapSessionAdapter | None = None

    def connect(self) -> None:
        if self.config.dry_run:
            print("[DRY-RUN] SAP connection skipped.")
            return

        session = self._connect_session(self.config.backend)
        self._session_adapter = SapSessionAdapter(session=session)

    def execute(self, command: SapCommand) -> None:
        prefix = f"[ROW {command.row_number}]"

        if command.tcode:
            self._go_to_tcode(prefix, command.tcode)

        if command.field_id and command.value is not None:
            self._set_field(prefix, command.field_id, command.value)

        if command.action:
            self._run_action(prefix, command.action)

    def _connect_session(self, backend: str) -> Any:
        if backend == "comtypes":
            from comtypes.client import GetObject

            sap_gui_auto = GetObject("SAPGUI")
        elif backend == "pywin32":
            import win32com.client

            sap_gui_auto = win32com.client.GetObject("SAPGUI")
        else:
            raise SapAutomationError(f"Unsupported backend: {backend}")

        if sap_gui_auto is None:
            raise SapAutomationError(
                "SAP GUI object not found. Ensure SAP Logon is running and scripting is enabled."
            )

        application = sap_gui_auto.GetScriptingEngine
        connection = application.Children(self.config.connection_index)
        session = connection.Children(self.config.session_index)
        return session

    def _go_to_tcode(self, prefix: str, tcode: str) -> None:
        if self.config.dry_run:
            print(f"{prefix} [DRY-RUN] Open transaction /n{tcode}")
            return

        session = self._require_session()
        ok_code = session.find("wnd[0]/tbar[0]/okcd")
        ok_code.text = f"/n{tcode}"
        session.find("wnd[0]").sendVKey(0)
        print(f"{prefix} Opened transaction {tcode}")

    def _set_field(self, prefix: str, field_id: str, value: str) -> None:
        if self.config.dry_run:
            print(f"{prefix} [DRY-RUN] Set {field_id} = {value}")
            return

        session = self._require_session()
        field = session.find(field_id)

        if hasattr(field, "text"):
            field.text = value
        elif hasattr(field, "key"):
            field.key = value
        else:
            raise SapAutomationError(
                f"Field {field_id} does not support text/key assignment"
            )

        print(f"{prefix} Set {field_id} = {value}")

    def _run_action(self, prefix: str, action: str) -> None:
        lowered = action.lower()

        if self.config.dry_run:
            print(f"{prefix} [DRY-RUN] Action {action}")
            return

        session = self._require_session()

        if lowered == "enter":
            session.find("wnd[0]").sendVKey(0)
        elif lowered == "save":
            session.find("wnd[0]/tbar[0]/btn[11]").press()
        elif lowered == "back":
            session.find("wnd[0]/tbar[0]/btn[3]").press()
        elif lowered.startswith("press:"):
            button_id = action.split(":", 1)[1]
            session.find(button_id).press()
        else:
            raise SapAutomationError(
                f"Unsupported action '{action}'. Allowed: enter, save, back, press:<id>."
            )

        print(f"{prefix} Action executed: {action}")

    def _require_session(self) -> SapSessionAdapter:
        if self._session_adapter is None:
            raise SapAutomationError("SAP session not initialized. Call connect() first.")
        return self._session_adapter
