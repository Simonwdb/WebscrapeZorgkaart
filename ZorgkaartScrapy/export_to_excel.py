import pandas as pd
from pathlib import Path

# Bestanden
DETAILS_JSON = Path("data/zorgkaart_details_update.json")
OUTPUT_EXCEL = Path("exports/zorgkaart_details.xlsx")

# Zorg dat de exports-map bestaat
OUTPUT_EXCEL.parent.mkdir(parents=True, exist_ok=True)

# Kolommen waarop ontdubbeld moet worden
DEDUPLICATE_ON = ["organisatietype", "naam", "url", "straat", "postcode", "plaats"]

# Laad nieuwe data vanuit JSON
if DETAILS_JSON.exists():
    new_df = pd.read_json(DETAILS_JSON)

    # Laad bestaande Excel als die er is
    if OUTPUT_EXCEL.exists():
        existing_df = pd.read_excel(OUTPUT_EXCEL)
        combined_df = pd.concat([existing_df, new_df], ignore_index=True)
    else:
        combined_df = new_df

    # Ontdubbelen op basis van geselecteerde kolommen
    deduplicated_df = combined_df.drop_duplicates(subset=DEDUPLICATE_ON)

    # Schrijf resultaat naar Excel
    deduplicated_df.to_excel(OUTPUT_EXCEL, index=False)
    print(f"Excel-bestand bijgewerkt met {len(deduplicated_df)} unieke rijen: {OUTPUT_EXCEL}")
else:
    print(f"Bestand niet gevonden: {DETAILS_JSON}")
