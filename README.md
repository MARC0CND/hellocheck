# hellocheck

Application de base pour lire un fichier Excel et piloter SAP GUI via scripting COM.

Cette base combine:
- Python pour parser Excel et orchestrer les actions.
- SAP GUI Scripting via `comtypes` (ou `pywin32`) pour l'automatisation.
- PowerShell avec un helper C# embarque pour lancer l'app de facon ergonomique sous Windows.

## Prerequis

- Windows avec SAP GUI installe et **SAP GUI Scripting active**.
- Python 3.11+
- Permissions SAP permettant le scripting GUI.

Pour activer SAP GUI scripting:
1. SAP Logon -> Options -> Accessibility & Scripting -> Scripting -> Enable scripting.
2. Verifier aussi le parametre serveur SAP (`sapgui/user_scripting = TRUE`) via l'equipe BASIS.

## Installation

Depuis la racine du repo:

```bash
python -m venv .venv
# Windows PowerShell:
. .venv/Scripts/Activate.ps1
pip install -r requirements.txt
```

## Structure

- `src/hellocheck/main.py`: point d'entree CLI.
- `src/hellocheck/excel_reader.py`: lecture des commandes Excel.
- `src/hellocheck/sap_automation.py`: connexion COM SAP GUI + execution des actions.
- `config/sap_config.json`: configuration backend/session.
- `scripts/Run-SapAutomation.ps1`: launcher PowerShell (+ C# Add-Type).
- `scripts/Build-SampleWorkbook.ps1`: genere un `.xlsx` d'exemple.
- `templates/commands_template.csv`: modele CSV rapide.

## Format Excel attendu

Colonnes obligatoires (ligne d'entete):
- `tcode`
- `field_id`
- `value`
- `action`

Exemple de `action` pris en charge:
- `enter`
- `save`
- `back`
- `press:wnd[0]/tbar[1]/btn[8]` (bouton SAP cible)

## Usage Python (direct)

```bash
PYTHONPATH=src python -m hellocheck.main --excel templates/commands_template.xlsx --config config/sap_config.json --dry-run
```

Sous Windows PowerShell:

```powershell
$env:PYTHONPATH = "src"
python -m hellocheck.main --excel templates/commands_template.xlsx --config config/sap_config.json --dry-run
```

## Usage PowerShell (avec picker Excel)

```powershell
./scripts/Run-SapAutomation.ps1 -DryRun
```

Ou avec chemin explicite:

```powershell
./scripts/Run-SapAutomation.ps1 -ExcelPath "C:\\temp\\orders.xlsx" -ConfigPath "config/sap_config.json" -Backend comtypes
```

## Configuration

Le fichier `config/sap_config.json` accepte:

```json
{
	"backend": "comtypes",
	"connection_index": 0,
	"session_index": 0,
	"dry_run": true
}
```

- `backend`: `comtypes` ou `pywin32`
- `connection_index`: index de la connexion SAP ouverte
- `session_index`: index de la session dans la connexion
- `dry_run`: si `true`, affiche les actions sans piloter SAP

## Notes importantes

- Les IDs de champs SAP (`field_id`) se recuperent via SAP GUI script recorder.
- Toujours valider en `dry_run` avant execution reelle.
- Cette base est volontairement simple: ajoute des validations metier et gestion des popups selon ton process SAP.