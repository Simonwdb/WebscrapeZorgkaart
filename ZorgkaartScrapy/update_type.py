import json
from pathlib import Path
from math import ceil
from collections import defaultdict

# Bestanden
ORGANISATIES_FILE = Path("data/zorgkaart_details_update.json")
TYPES_FILE = Path("data/zorgkaart_types_update.json")
INPUT_FILE = Path("data/zorgkaart_types_input.json")

# Tel per organisatietype hoeveel organisaties er al zijn
org_counts = defaultdict(int)
if ORGANISATIES_FILE.exists() and ORGANISATIES_FILE.stat().st_size > 0:
    with ORGANISATIES_FILE.open(encoding="utf-8") as f:
        for item in json.load(f):
            key = item.get("organisatietype")
            if key:
                org_counts[key] += 1

# Laad organisatietypes en voeg start_page toe
with TYPES_FILE.open(encoding="utf-8") as f:
    types = json.load(f)

for item in types:
    org_type = item.get("organisatietype")
    count = org_counts.get(org_type, 0)
    item["scraped_count"] = count

# Schrijf update file met nieuw count en scraped_count
with TYPES_FILE.open("w", encoding="utf-8") as f:
    json.dump(types, f, ensure_ascii=False, indent=2)

input_items = [item for item in types if item['aantal'] != item['scraped_count']]

# Schrijf de aantal organisatietypes als input, die niet gelijk zijn aan het aantal en scraped_count
with INPUT_FILE.open('w', encoding='utf-8') as f:
    json.dump(input_items, f, ensure_ascii=False, indent=2)
