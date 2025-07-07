import json
import scrapy
import numpy as np

from pathlib import Path
from typing import Generator, Dict, Any, List


class ZorgkaartNumberSpiderSpider(scrapy.Spider):
    name = "zorgkaart_number"
    allowed_domains = ["zorgkaartnederland.nl"]
    custom_settings = {
        "FEEDS": {}
    }

    def __init__(self, target: str = "Tandartsenpraktijk", job_title: str = "Tandarts", limit: int = None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.target = target
        self.job_title = job_title
        self.limit = int(limit) if limit is not None else None
        safe_job_title = self.job_title.lower().replace(" ", "_")
        self.EXISTING_PATH = Path(f"data\\zorgkaart_number_{safe_job_title}.json")
        with self.EXISTING_PATH.open(encoding='utf-8') as f:
            self.number_data: List[Dict] = json.load(f)
  
    def start_requests(self) -> Generator[scrapy.Request, None, None]:
        json_path = Path("data/zorgkaart_details_update.json")

        if not json_path.exists():
            print("❌ Bestand niet gevonden:", json_path)
            return

        with json_path.open(encoding="utf-8") as f:
            organisaties = json.load(f)

        print(f"{len(self.number_data)} bestaande URL(s) gevonden in outputbestand")
        
        target_organisaties = [data for data in organisaties if data['organisatietype'] == self.target]

        url_lookup = {
            (item['url']): item for item in self.number_data
        }

        target_organisaties_filtered = []

        for item in target_organisaties:
            key = (item['url'])
            match = url_lookup.get(key)
            if not match:
                target_organisaties_filtered.append(item)

        print(f"Length filtered target_organisaties: {len(target_organisaties_filtered)}")

        if self.limit is not None:
            target_organisaties_filtered = target_organisaties_filtered[:self.limit]

        for item in target_organisaties_filtered:
            url = item.get("url")
            if url:
                full_url = url + "/specialisten"
                print(f"▶ Start scraping: {full_url}")
                yield scrapy.Request(
                    url=full_url,
                    callback=self.parse,
                    meta={
                        "base_url": url,
                        "organisatietype": self.target}
                )

    def parse(self, response: scrapy.http.Response) -> Generator[Dict[str, Any], None, None]:
        base_url = response.meta['base_url']
        organisatietype = response.meta['organisatietype']

        try:
            count = None
            a_tags = response.css("div.filter__aside__item a")

            for a_tag in a_tags:
                a_tag_title = a_tag.css("::attr(title)").get(default="").strip().lower()
                if a_tag_title == self.job_title.lower():
                    count_text = a_tag.css("span.filter-radio__counter::text").get()
                    count = int(count_text.strip("() \n")) if count_text else None
                    break
            else:
                count = None

            message = f"✅ {base_url}/specialisten → {count if count is not None else 'no'} specialists ({self.job_title}) found"
            print(message)

            item = {
                "organisatietype": organisatietype,
                "url": base_url,
                "job_title": self.job_title,
                "specialisten_count": count
            }

            self._append_to_file(item)
            yield item

        except Exception as e:
            print(f"⚠️ Fout bij parsen {response.url}: {e}")
    

    def _append_to_file(self, item: Dict[str, Any]) -> None:
        """Voeg nieuw item toe aan bestaand bestand (append-manier)"""
        self.number_data.append(item)

        with self.EXISTING_PATH.open("w", encoding='utf-8') as f:
            json.dump(self.number_data, f, indent=2, ensure_ascii=False)
