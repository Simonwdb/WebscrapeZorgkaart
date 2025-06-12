import json
import pandas as pd
from pathlib import Path

# Paddefinities
ORGANISATIES_FILE = Path("data/zorgkaart_organisaties.json")
DETAILS_FILE_JSON = Path("data/zorgkaart_details_update.json")
DETAILS_FILE_XLSX = Path("exports/zorgkaart_details.xlsx")
OUTPUT_FILE = Path("data/zorgkaart_organisaties_input.json")

# Laad organisaties
if not ORGANISATIES_FILE.exists():
    print(f"Organisatiebestand niet gevonden: {ORGANISATIES_FILE}")
    exit(1)

with ORGANISATIES_FILE.open(encoding="utf-8") as f:
    organisaties = json.load(f)

# Laad bestaande namen uit JSON of Excel
bestaande_namen = set()

if DETAILS_FILE_XLSX.exists():
    df = pd.read_excel(DETAILS_FILE_XLSX)
    if "naam" in df.columns:
        bestaande_namen.update(df["naam"].dropna().astype(str).str.strip())

elif DETAILS_FILE_JSON.exists():
    with DETAILS_FILE_JSON.open(encoding="utf-8") as f:
        bestaande_namen.update(item["naam"] for item in json.load(f) if "naam" in item)

# Filter organisaties
uniek_organisaties = [item for item in organisaties if item.get("naam", "").strip() not in bestaande_namen]

print(f"{len(uniek_organisaties)} organisaties over na filteren ({len(organisaties) - len(uniek_organisaties)} gefilterd).")

# Schrijf output
with OUTPUT_FILE.open("w", encoding="utf-8") as f:
    json.dump(uniek_organisaties, f, ensure_ascii=False, indent=2)
