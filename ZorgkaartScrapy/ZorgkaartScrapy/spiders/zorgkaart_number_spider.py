import json
import scrapy
import numpy as np

from pathlib import Path
from typing import Generator, Dict, Any


class ZorgkaartNumberSpiderSpider(scrapy.Spider):
    name = "zorgkaart_number"
    allowed_domains = ["zorgkaartnederland.nl"]

    def __init__(self, target: str = "Tandartsenpraktijk", job_title: str = "Tandarts", limit: int = None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.target = target
        self.job_title = job_title
        self.limit = limit

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = super().from_crawler(crawler, *args, **kwargs)

        # Dynamische bestandsnaam genereren op basis van job_title
        safe_job_title = spider.job_title.lower().replace(" ", "_")
        feed_path = f"data/zorgkaart_number_{safe_job_title}.json"

        # Override default feed settings
        crawler.settings.set(
            "FEEDS",
            {
                feed_path: {
                    "format": "json",
                    "encoding": "utf8",
                    "overwrite": True
                }
            },
            priority='spider'
        )

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

            yield {
                "organisatietype": organisatietype,
                "base": base_url,
                "job_title": self.job_title,
                "specialisten_count": count
            }

        except Exception as e:
            print(f"⚠️ Fout bij parsen {response.url}: {e}")
