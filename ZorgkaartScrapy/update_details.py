import json
from pathlib import Path
from typing import Dict, List

OUDE_FILE = Path("data/zorgkaart_details_update.json")  # bestaand bestand
NIEUWE_FILE = Path("data/zorgkaart_details.json")        # output van spider 3
COUNT_FILE = Path("data/zorgkaart_number.json")         # output van spider 4
SAMENGEVOEGD_FILE = Path("data/zorgkaart_details_update.json")  # overschrijft oude bestand

# Laden oude data
oude_data: Dict[str, Dict] = {}
if OUDE_FILE.exists() and OUDE_FILE.stat().st_size > 0:
    with OUDE_FILE.open(encoding="utf-8") as f:
        for item in json.load(f):
            oude_data[item["url"]] = item

# Laden nieuwe data
with NIEUWE_FILE.open(encoding="utf-8") as f:
    nieuwe_data: List[Dict] = json.load(f)

# Laden numbers data
with COUNT_FILE.open(encoding='utf-8') as f:
    number_data: List[Dict] = json.load(f)

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

number_lookup = {
    (item['url'], item['organisatietype']): item for item in number_data
}

for item in samengevoegd:
    key = (item['url'], item['organisatietype'])
    match = number_lookup.get(key)
    if match:
        item['specialisten_count'] = match.get('specialisten_count')

# Schrijf naar bestand
with SAMENGEVOEGD_FILE.open("w", encoding="utf-8") as f:
    json.dump(samengevoegd, f, ensure_ascii=False, indent=2)
