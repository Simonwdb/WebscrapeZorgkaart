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

        try:
            with open(start_urls_file, "r", encoding="utf-8") as f:
                all_items = json.load(f)
        except Exception as e:
            self.logger.error(f"Fout bij laden start_urls bestand: {e}")
            all_items = []

        for item in all_items:
            try:
                aantal = item.get("aantal")
                count = item.get("scraped_count", 0)

                if isinstance(aantal, int) and count >= aantal:
                    self.logger.info(f"Overslaan: {item['organisatietype']} (volledig gescrapet)")
                    continue

                start_page = ceil(count / 20) + 1
                item["start_page"] = start_page
                self.start_urls.append(item)

            except Exception as e:
                self.logger.warning(f"Fout bij verwerken item: {e}")

        try:
            self.max_page = int(max_page) if max_page is not None else None
        except Exception as e:
            self.logger.error(f"Kon max_page niet omzetten naar int: {e}")
            self.max_page = None

        self.logger.info(f"{len(self.start_urls)} organisatietypes opgenomen voor scraping.")

    async def start(self) -> AsyncGenerator[Request, None]:
        for entry in self.start_urls:
            url: str = entry.get("url")
            organisatietype: str = entry.get("organisatietype", "onbekend")
            start_page: int = entry.get("start_page", 1)

            if url:
                pagina_url = f"{url}/pagina{start_page}" if start_page > 1 else url
                yield scrapy.Request(
                    url=pagina_url,
                    callback=self.parse,
                    meta={"organisatietype": organisatietype, "page": start_page},
                    errback=self.error_handler
                )

    def parse(self, response: Response) -> Generator[Dict[str, Any], None, None]:
        organisatietype = response.meta["organisatietype"]
        current_page = response.meta["page"]
        self.logger.info(f"[{organisatietype}] Pagina {current_page} geladen: {response.url}")

        resultaten = 0
        for item in response.css('div.filter-result'):
            naam = item.css('a.filter-result__name::text').get()
            relatieve_link = item.css('a.filter-result__name::attr(href)').get()

            if naam and relatieve_link:
                resultaten += 1
                yield {
                    "organisatietype": organisatietype,
                    "naam": naam.strip(),
                    "url": response.urljoin(relatieve_link.strip())
                }

        if resultaten == 0:
            self.logger.warning(f"[{organisatietype}] Geen resultaten gevonden op pagina {current_page}")

        if self.max_page is not None and current_page >= self.max_page:
            self.logger.info(f"[{organisatietype}] Max pagina bereikt ({self.max_page})")
            return

        if response.css('ul.pagination a.page-link')[-1:]:
            base_url = response.url.split("/pagina")[0]
            next_page_url = f"{base_url}/pagina{current_page + 1}"
            yield scrapy.Request(
                url=next_page_url,
                callback=self.parse,
                meta={"organisatietype": organisatietype, "page": current_page + 1},
                errback=self.error_handler,
                dont_filter=True
            )

    def error_handler(self, failure: Failure) -> None:
        request = failure.request
        organisatietype = request.meta.get("organisatietype", "onbekend")
        self.logger.error(f"[{organisatietype}] Fout bij ophalen {request.url} → {repr(failure.value)}")
