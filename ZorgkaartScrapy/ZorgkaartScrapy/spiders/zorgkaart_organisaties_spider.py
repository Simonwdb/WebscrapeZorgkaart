import json
import scrapy
from math import ceil
from typing import List, Dict, Optional, Generator, Any, AsyncGenerator, Union
from scrapy.http import Response, Request
from twisted.python.failure import Failure


class ZorgkaartOrganisatiesSpider(scrapy.Spider):
    name = "zorgkaart_organisaties"
    allowed_domains = ["zorgkaartnederland.nl"]

    start_urls: List[Dict[str, str]] = []
    max_page: Optional[int] = None

    def __init__(
        self,
        start_urls_file: str = "data/zorgkaart_types_input.json",
        max_page: Optional[Union[str, int]] = None,
        *args: Any,
        **kwargs: Any
    ) -> None:
        super().__init__(*args, **kwargs)
        self.start_urls = []

        print(f"Start met laden van start_urls uit JSON-bestand... -- max_page = {max_page}")

        try:
            with open(start_urls_file, "r", encoding="utf-8") as f:
                all_items = json.load(f)
        except Exception as e:
            self.logger.error(f"Fout bij laden start_urls bestand: {e}")
            all_items = []

        all_items = [item for item in all_items if item['aantal'] != item['scraped_count']]
        
        for item in all_items:
            try:
                aantal = item.get("aantal")
                scraped = item.get("scraped_count", 0)

                if isinstance(aantal, int) and scraped >= aantal:
                    print(f"Overslaan: {item['organisatietype']} (volledig gescrapet)")
                    continue

                start_page = ceil(scraped / 20) + 1
                item["start_page"] = start_page
                item["scrape_limit"] = aantal - scraped
                item["scraped_in_run"] = 0
                self.start_urls.append(item)

            except Exception as e:
                self.logger.error(f"Fout bij verwerken item: {e}")

        try:
            self.max_page = int(max_page) if max_page is not None else None
        except Exception as e:
            self.logger.error(f"Kon max_page niet omzetten naar int: {e}")
            self.max_page = None

        print(f"{len(self.start_urls)} organisatietypes opgenomen voor scraping.")

    async def start(self) -> AsyncGenerator[Request, None]:
        for item in self.start_urls:
            url = item.get("url")
            organisatietype = item.get("organisatietype", "onbekend")
            start_page = item.get("start_page", 1)

            if url:
                pagina_url = f"{url}/pagina{start_page}" if start_page > 1 else url
                print(f"Start scraping voor: {organisatietype} vanaf pagina {start_page} → {pagina_url}")
                yield scrapy.Request(
                    url=pagina_url,
                    callback=self.parse,
                    meta={
                        "organisatietype": organisatietype,
                        "page": start_page,
                        "start_page": start_page,
                        "scrape_limit": item.get("scrape_limit"),
                        "scraped_in_run": 0
                    },
                    errback=self.error_handler
                )

    def parse(self, response: Response) -> Generator[Dict[str, Any], None, None]:
        organisatietype = response.meta["organisatietype"]
        current_page = response.meta["page"]
        start_page = response.meta["start_page"]
        scrape_limit = response.meta["scrape_limit"]
        scraped_in_run = response.meta["scraped_in_run"]

        print(f"[{organisatietype}] Pagina {current_page} geladen: {response.url}")

        resultaten = 0
        for item in response.css('div.filter-result'):
            naam = item.css('a.filter-result__name::text').get()
            relatieve_link = item.css('a.filter-result__name::attr(href)').get()

            if naam and relatieve_link:
                if scraped_in_run >= scrape_limit:
                    print(f"[{organisatietype}] Limiet bereikt ({scrape_limit})")
                    return

                resultaten += 1
                scraped_in_run += 1
                yield {
                    "organisatietype": organisatietype,
                    "naam": naam.strip(),
                    "url": response.urljoin(relatieve_link.strip())
                }

        if resultaten == 0:
            print(f"[{organisatietype}] Geen resultaten gevonden op pagina {current_page}")
            return

        if scrape_limit is not None and scraped_in_run >= scrape_limit:
            print(f"[{organisatietype}] Totale scrape limiet ({scrape_limit}) bereikt")
            return

        if self.max_page is not None and (current_page - start_page) >= self.max_page:
            print(f"[{organisatietype}] Max extra pagina’s ({self.max_page}) bereikt vanaf pagina {start_page}")
            return

        if response.css('ul.pagination a.page-link')[-1:]:
            base_url = response.url.split("/pagina")[0]
            next_page_url = f"{base_url}/pagina{current_page + 1}"
            yield scrapy.Request(
                url=next_page_url,
                callback=self.parse,
                meta={
                    "organisatietype": organisatietype,
                    "page": current_page + 1,
                    "start_page": start_page,
                    "scrape_limit": scrape_limit,
                    "scraped_in_run": scraped_in_run
                },
                errback=self.error_handler,
                dont_filter=True
            )

    def error_handler(self, failure: Failure) -> None:
        request = failure.request
        organisatietype = request.meta.get("organisatietype", "onbekend")
        self.logger.error(f"[{organisatietype}] Fout bij ophalen {request.url} → {repr(failure.value)}")
