import pandas as pd
from pathlib import Path
from datetime import datetime

# Bestanden
DETAILS_JSON = Path("data/zorgkaart_details_update.json")
today_str = datetime.today().strftime("%Y%m%d")
OUTPUT_EXCEL = Path(f"exports/{today_str} - Zorgkaart_details.xlsx")
GEMEENTE_FILE = Path("../20250625 - GemeenteNamen.xlsx")

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

    # Toevoegen van Gemeentenaam
    # Laden van dataframe met Gemeentenamen
    gem_df = pd.read_excel(GEMEENTE_FILE)

    # Plaatsnaam Bergen veranderen
    deduplicated_df.loc[deduplicated_df['plaats'] == 'Bergen', 'plaats'] = deduplicated_df.loc[deduplicated_df['plaats'] == 'Bergen'].apply(
        lambda row: 'Bergen (NH)' if str(row['postcode']).startswith('18') else 'Bergen L',
        axis=1
    )

    # Toevoegen kolom GemeenteNaam
    deduplicated_df = deduplicated_df.merge(
        gem_df[['Value', 'StringValue']],
        left_on='plaats',
        right_on='Value',
        how='left'
    )
    deduplicated_df.rename(columns={'StringValue': 'GemeenteNaam'}, inplace=True)
    deduplicated_df.drop(columns=['Value'], inplace=True)

    # Schrijf resultaat naar Excel
    deduplicated_df.to_excel(OUTPUT_EXCEL, index=False)
    print(f"Excel-bestand bijgewerkt met {len(deduplicated_df)} unieke rijen: {OUTPUT_EXCEL}")
else:
    print(f"Bestand niet gevonden: {DETAILS_JSON}")
