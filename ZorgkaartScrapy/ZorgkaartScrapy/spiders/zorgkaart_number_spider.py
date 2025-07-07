import json
import scrapy
import numpy as np

from pathlib import Path
from typing import Generator, Dict, Any


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
        self.scraped_urls = set()

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = super().from_crawler(crawler, *args, **kwargs)

        # Dynamische bestandsnaam genereren op basis van job_title
        safe_job_title = spider.job_title.lower().replace(" ", "_")
        spider.output_path = Path(f"data/zorgkaart_number_{safe_job_title}.json")

        # Lees bestaande data als die er is
        if spider.output_path.exists():
            try:
                with spider.output_path.open(encoding="utf-8") as f:
                    existing_data = json.load(f)
                    spider.scraped_urls = {item["url"] for item in existing_data if "url" in item}
                    print(f"⚠️ {len(spider.scraped_urls)} bestaande URL(s) gevonden in outputbestand")
            except json.JSONDecodeError:
                print("⚠️ Kon bestaande JSON niet parsen – bestand wordt genegeerd")

        return spider
   
    def start_requests(self) -> Generator[scrapy.Request, None, None]:
        json_path = Path("data/zorgkaart_details_update.json")

        if not json_path.exists():
            print("❌ Bestand niet gevonden:", json_path)
            return

        with json_path.open(encoding="utf-8") as f:
            organisaties = json.load(f)

        target_organisaties = [data for data in organisaties if data['organisatietype'] == self.target]

        if self.limit is not None:
            target_organisaties = target_organisaties[:self.limit]

        for item in target_organisaties:
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
        existing = []
        if self.output_path.exists():
            try:
                with self.output_path.open("r", encoding="utf-8") as f:
                    existing = json.load(f)
            except json.JSONDecodeError:
                print("⚠️ Kon outputbestand niet inlezen – wordt overschreven")

        existing.append(item)

        with self.output_path.open("w", encoding="utf-8") as f:
            json.dump(existing, f, indent=2, ensure_ascii=False)
