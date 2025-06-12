import json
from pathlib import Path

OUDE_FILE = Path("data/zorgkaart_types_update.json")
NIEUWE_FILE = Path("data/zorgkaart_types.json")
SAMENGEVOEGD_FILE = Path("data/zorgkaart_types_update.json")  # overschrijf oude bestand

# Laad oude data
oude_items = {}
if OUDE_FILE.exists() and OUDE_FILE.stat().st_size > 0:
    with OUDE_FILE.open(encoding="utf-8") as f:
        oude_items = {item["organisatietype"]: item for item in json.load(f)}

# Laad nieuwe data
with NIEUWE_FILE.open(encoding="utf-8") as f:
    nieuwe_items = json.load(f)

# Combineer
samengevoegd = []
for nieuw in nieuwe_items:
    org_type = nieuw["organisatietype"]
    oud = oude_items.get(org_type)

    if not oud or oud.get("aantal") != nieuw["aantal"]:
        # Nieuw item of aantal gewijzigd → gebruik nieuwe inclusief scraped_at
        samengevoegd.append(nieuw)
    else:
        # Aantal niet gewijzigd → behoud originele scraped_at
        samengevoegd.append({**nieuw, "scraped_at": oud["scraped_at"]})

# Schrijf naar bestand
with SAMENGEVOEGD_FILE.open("w", encoding="utf-8") as f:
    json.dump(samengevoegd, f, ensure_ascii=False, indent=2)
