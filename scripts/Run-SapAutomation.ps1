param(
    [string]$ExcelPath,
    [string]$ConfigPath = "config/sap_config.json",
    [string]$Sheet,
    [ValidateSet("comtypes", "pywin32")]
    [string]$Backend,
    [switch]$DryRun
)

$ErrorActionPreference = "Stop"

# Small C# helper used from PowerShell to keep argument handling explicit.
Add-Type -TypeDefinition @"
using System;
using System.Collections.Generic;

public static class CliArgs
{
    public static string[] Build(string excelPath, string configPath, string sheet, string backend, bool dryRun)
    {
        var args = new List<string>
        {
            "-m", "hellocheck.main",
            "--excel", excelPath,
            "--config", configPath
        };

        if (!string.IsNullOrWhiteSpace(sheet))
        {
            args.Add("--sheet");
            args.Add(sheet);
        }

        if (!string.IsNullOrWhiteSpace(backend))
        {
            args.Add("--backend");
            args.Add(backend);
        }

        if (dryRun)
        {
            args.Add("--dry-run");
        }

        return args.ToArray();
    }
}
"@

function Select-ExcelFile {
    Add-Type -AssemblyName System.Windows.Forms
    $dialog = New-Object System.Windows.Forms.OpenFileDialog
    $dialog.Filter = "Excel files (*.xlsx)|*.xlsx|All files (*.*)|*.*"
    $dialog.Multiselect = $false

    if ($dialog.ShowDialog() -ne [System.Windows.Forms.DialogResult]::OK) {
        throw "No Excel file selected."
    }

    return $dialog.FileName
}

if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    throw "Python not found in PATH. Install Python 3.11+ and retry."
}

if (-not $ExcelPath) {
    $ExcelPath = Select-ExcelFile
}

if (-not (Test-Path $ExcelPath)) {
    throw "Excel file not found: $ExcelPath"
}

if (-not (Test-Path $ConfigPath)) {
    throw "Config file not found: $ConfigPath"
}

$env:PYTHONPATH = "src"

$args = [CliArgs]::Build($ExcelPath, $ConfigPath, $Sheet, $Backend, $DryRun.IsPresent)
Write-Host "Launching automation..." -ForegroundColor Cyan
python @args
