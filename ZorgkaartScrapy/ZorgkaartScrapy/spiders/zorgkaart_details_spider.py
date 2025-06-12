import json
import re
import scrapy
import datetime
from pathlib import Path
from typing import Dict, Generator, Optional, Tuple, Any


class ZorgkaartDetailsSpider(scrapy.Spider):
    name = "zorgkaart_details"
    allowed_domains = ["zorgkaartnederland.nl"]

    custom_settings = {
        "FEEDS": {
            "data/zorgkaart_details.json": {
                "format": "json",
                "encoding": "utf8",
                "overwrite": True,
            }
        }
    }

    def __init__(self, input_file: str = "data/zorgkaart_organisaties.json", *args: Any, **kwargs: Any):
        super().__init__(*args, **kwargs)
        self.input_file = Path(input_file)
        self.start_data = []

        self.logger.info(f"Details spider gestart met input: {self.input_file}")

        if not self.input_file.exists():
            self.logger.error(f"Bestand niet gevonden: {self.input_file}")
            return

        with self.input_file.open(encoding="utf-8") as f:
            try:
                self.start_data = json.load(f)
                assert isinstance(self.start_data, list)
                self.logger.info(f"{len(self.start_data)} items geladen uit inputbestand.")
            except Exception as e:
                self.logger.error(f"Fout bij laden van input: {e}")

    def start_requests(self) -> Generator[scrapy.Request, None, None]:
        for entry in self.start_data:
            url = entry.get("url")
            if url:
                self.logger.info(f"Bezoek URL: {url}")
                yield scrapy.Request(
                    url=url,
                    callback=self.parse,
                    meta={"base_data": entry}
                )

    def parse(self, response: scrapy.http.Response) -> Generator[Dict[str, Any], None, None]:
        base_data = response.meta.get("base_data", {})
        script_tag = response.xpath('//script[@type="application/ld+json"]/text()').get()

        if not script_tag:
            self.logger.warning(f"Geen JSON-LD gevonden op {response.url}")
            return

        try:
            data = json.loads(script_tag)
            address = data.get("address", {})
            straat_raw = address.get("streetAddress", "").strip()

            if not straat_raw:
                self.logger.warning(f"Geen adres gevonden op {response.url}")
                return

            straat, huisnummer, toevoeging = self.split_address(straat_raw)

            item = {
                **base_data,
                "straat": straat,
                "huisnummer": huisnummer,
                "toevoeging": toevoeging,
                "postcode": address.get("postalCode", "").replace(" ", ""),
                "plaats": address.get("addressLocality", ""),
                "scraped_at": datetime.date.today().isoformat()
            }

            self.logger.info(f"Adres verwerkt voor: {base_data.get('naam', 'onbekend')} → {straat} {huisnummer}")
            yield item

        except Exception as e:
            self.logger.error(f"Fout bij parsen JSON op {response.url}: {e}")

    @staticmethod
    def split_address(full_address: str) -> Tuple[str, Optional[str], Optional[str]]:
        match = re.match(r'^(.*?)\s(\d+)\s*(.*)$', full_address.strip())
        if match:
            straat = match.group(1).strip()
            nummer = match.group(2).strip()
            toevoeging_raw = match.group(3).strip()
            toevoeging = toevoeging_raw.lstrip(', ').strip() if toevoeging_raw else None
            return straat, nummer, toevoeging
        else:
            return full_address.strip(), None, None
