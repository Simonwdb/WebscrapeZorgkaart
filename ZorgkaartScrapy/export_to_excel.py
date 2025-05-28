import pandas as pd
from pathlib import Path

# Kies het bestand dat je wilt exporteren
DETAILS_JSON = Path("data/zorgkaart_details_update.json")
OUTPUT_EXCEL = Path("exports/zorgkaart_details.xlsx")

# Zorg dat de exports-map bestaat
OUTPUT_EXCEL.parent.mkdir(parents=True, exist_ok=True)

# Laad data en exporteer
if DETAILS_JSON.exists():
    df = pd.read_json(DETAILS_JSON)
    df.to_excel(OUTPUT_EXCEL, index=False)
    print(f"Excel-bestand aangemaakt: {OUTPUT_EXCEL}")
else:
    print(f"Bestand niet gevonden: {DETAILS_JSON}")
