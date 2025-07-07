import json
import scrapy
import datetime

from pathlib import Path
from typing import Generator, Dict, Any


class ZorgkaartNumberSpiderSpider(scrapy.Spider):
    name = "zorgkaart_number_spider"
    allowed_domains = ["zorgkaartnederland.nl"]

    def start_requests(self):
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

    def parse(self, response):
        pass
