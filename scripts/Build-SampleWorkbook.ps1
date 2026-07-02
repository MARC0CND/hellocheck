param(
    [string]$OutputPath = "templates/commands_template.xlsx"
)

$ErrorActionPreference = "Stop"

if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    throw "Python is required to create the workbook template."
}

$code = @'
from pathlib import Path
from openpyxl import Workbook

output = Path(r"__OUTPUT__")
output.parent.mkdir(parents=True, exist_ok=True)

wb = Workbook()
ws = wb.active
ws.title = "Commands"

ws.append(["tcode", "field_id", "value", "action"])
ws.append(["VA01", "", "", "enter"])
ws.append(["", "wnd[0]/usr/ctxtVBAK-AUART", "OR", ""])
ws.append(["", "wnd[0]/usr/ctxtVBAK-VKORG", "1000", ""])
ws.append(["", "wnd[0]/usr/ctxtVBAK-VTWEG", "10", ""])
ws.append(["", "wnd[0]/usr/ctxtVBAK-SPART", "00", "enter"])
ws.append(["", "", "", "save"])

wb.save(output)
print(f"Template written to {output}")
'@

$escaped = $OutputPath.Replace('\\', '\\\\')
$finalCode = $code.Replace("__OUTPUT__", $escaped)
python -c $finalCode
