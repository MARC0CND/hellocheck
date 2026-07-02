from __future__ import annotations

import argparse
from pathlib import Path

from .config_loader import load_config
from .excel_reader import read_commands
from .sap_automation import SapAutomation, SapAutomationError


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Read Excel steps and execute SAP GUI scripting automation"
    )
    parser.add_argument("--excel", required=True, help="Path to xlsx file")
    parser.add_argument("--sheet", default=None, help="Sheet name (optional)")
    parser.add_argument(
        "--config",
        default="config/sap_config.json",
        help="Path to JSON config file",
    )
    parser.add_argument(
        "--backend",
        choices=["comtypes", "pywin32"],
        default=None,
        help="COM backend for SAP GUI scripting",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print actions without controlling SAP",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    excel_path = Path(args.excel)
    config_path = Path(args.config)

    if not excel_path.exists():
        raise FileNotFoundError(f"Excel file not found: {excel_path}")

    config = load_config(config_path, cli_backend=args.backend, cli_dry_run=args.dry_run)
    commands = read_commands(excel_path, sheet_name=args.sheet)

    if not commands:
        print("No commands found in Excel.")
        return 0

    print(f"Loaded {len(commands)} command(s) from {excel_path}")

    automation = SapAutomation(config=config)
    try:
        automation.connect()
        for command in commands:
            automation.execute(command)
    except SapAutomationError as exc:
        print(f"SAP automation failed: {exc}")
        return 1

    print("Automation completed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
