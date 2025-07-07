import json
import scrapy
import datetime
import numpy as np

from pathlib import Path
from typing import Generator, Dict, Any


class ZorgkaartNumberSpiderSpider(scrapy.Spider):
    name = "zorgkaart_number_spider"
    allowed_domains = ["zorgkaartnederland.nl"]

    def start_requests(self) -> Generator[scrapy.Request, None, None]:
        json_path = Path("data/zorgkaart_details_update.json")

        if not json_path.exists():
            print("❌ Bestand niet gevonden:", json_path)
            return
        

        with json_path.open(encoding="utf-8") as f:
            organisaties = json.load(f)

        target_organisaties = [data for data in organisaties if data['organisatietype'] == 'Tandartsenpraktijk']

        for item in target_organisaties:
            url = item.get("url")
            if url:
                full_url = url + "/specialisten"
                print(f"▶ Start scraping: {full_url}")
                yield scrapy.Request(
                    url=full_url,
                    callback=self.parse,
                    meta={"base_url": url}
                )
            break # for now, just only scrape the first item from target_organisaties

    def parse(self, response: scrapy.http.Response) -> Generator[Dict[str, Any], None, None]:
        base_url = response.meta['base_url']

        try:
            a_tags = response.css("div.filter__asside__item a")
            if len(a_tags) > 1:
                a_tag = a_tags[1]
                count_text = a_tag.css("span.filter-radio__counter::text").get()
                count = int(count_text.strip("() \n")) if count_text else None
            else:
                count = None
            
            print(f"✅ {base_url}/specialisten → {count if count is not None else "geen"} specialisten gevonden")
            yield {
                "base_url": base_url,
                "specialisten_count": count
            }

        except Exception as e:
            print(f"⚠️ Fout bij parsen {response.url}: {e}")

