import scrapy
from typing import Generator, Dict, Any


class ZorgkaartOrganisatietypesSpider(scrapy.Spider):
    name = "zorgkaart_organisatietypes"
    allowed_domains = ["zorgkaartnederland.nl"]
    start_urls = ["https://www.zorgkaartnederland.nl/overzicht/organisatietypes"]

    custom_settings = {
        "FEEDS": {
            "data/organisatietypes.json": {
                "format": "json",
                "encoding": "utf8",
                "overwrite": True,
            }
        }
    }

    def parse(self, response: scrapy.http.Response) -> Generator[Dict[str, Any], None, None]:
        for li in response.css("ul.overview-list li.overview-list__item"):
            link = li.css("a::attr(href)").get()
            text = li.css("a::text").get()

            if link and text:
                # Scheid organisatietype en aantal, bijv. "Fysiotherapiepraktijk (6107)"
                if "(" in text and text.endswith(")"):
                    name_part, count_part = text.rsplit("(", 1)
                    organisatietype = name_part.strip()
                    try:
                        aantal = int(count_part.strip(") "))
                    except ValueError:
                        aantal = None
                else:
                    organisatietype = text.strip()
                    aantal = None

                yield {
                    "organisatietype": organisatietype,
                    "url": response.urljoin(link),
                    "aantal": aantal
                }
