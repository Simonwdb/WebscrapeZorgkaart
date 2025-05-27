import json
from pathlib import Path
from typing import Dict, List

OUDE_FILE = Path("data/zorgkaart_details_update.json")  # bestaand bestand
NIEUWE_FILE = Path("data/zorgkaart_details.json")        # output van spider 3
SAMENGEVOEGD_FILE = Path("data/zorgkaart_details_update.json")  # overschrijft oude bestand

# Laad oude data
oude_data: Dict[str, Dict] = {}
if OUDE_FILE.exists() and OUDE_FILE.stat().st_size > 0:
    with OUDE_FILE.open(encoding="utf-8") as f:
        for item in json.load(f):
            oude_data[item["url"]] = item

# Laad nieuwe data
with NIEUWE_FILE.open(encoding="utf-8") as f:
    nieuwe_data: List[Dict] = json.load(f)

# Combineer
samengevoegd: List[Dict] = []
for nieuw in nieuwe_data:
    url = nieuw["url"]
    oud = oude_data.get(url)

    if not oud or any(nieuw.get(k) != oud.get(k) for k in nieuw if k != "scraped_at"):
        # Nieuw of gewijzigd → update incl. nieuwe scrape-datum
        samengevoegd.append(nieuw)
    else:
        # Ongewijzigd → behoud originele scraped_at
        nieuw["scraped_at"] = oud.get("scraped_at")
        samengevoegd.append(nieuw)

# Voeg oude entries toe die niet meer in nieuwe zitten
nieuwe_urls = {item["url"] for item in nieuwe_data}
for url, oud in oude_data.items():
    if url not in nieuwe_urls:
        samengevoegd.append(oud)

# Schrijf naar bestand
with SAMENGEVOEGD_FILE.open("w", encoding="utf-8") as f:
    json.dump(samengevoegd, f, ensure_ascii=False, indent=2)
