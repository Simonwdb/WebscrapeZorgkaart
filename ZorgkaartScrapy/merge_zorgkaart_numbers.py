import json
from pathlib import Path

# Pad naar map en bestandspatroon
input_dir = Path("data")
pattern = "zorgkaart_number_*.json"
output_file = input_dir / "zorgkaart_number.json"

all_items = []

# Zoek alle relevante bestanden
for file_path in input_dir.glob(pattern):
    if file_path.name == output_file.name:
        continue  # Sla doelbestand over als het al bestaat

    try:
        with file_path.open(encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, list):
                all_items.extend(data)
            else:
                print(f"⚠️ Bestand {file_path.name} bevat geen lijst — overgeslagen")
    except Exception as e:
        print(f"❌ Fout bij inlezen {file_path.name}: {e}")

# Wegschrijven naar samengevoegd bestand
with output_file.open("w", encoding="utf-8") as f_out:
    json.dump(all_items, f_out, ensure_ascii=False, indent=2)

print(f"✅ Samengevoegd bestand opgeslagen als: {output_file} ({len(all_items)} items)")
