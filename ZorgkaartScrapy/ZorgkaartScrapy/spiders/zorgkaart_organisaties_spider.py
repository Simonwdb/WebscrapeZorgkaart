import ast
import json
import scrapy
from typing import List, Dict, Optional, Generator, Any, AsyncGenerator, Union
from scrapy.http import Response, Request
from twisted.python.failure import Failure


class ZorgkaartOrganisatiesSpider(scrapy.Spider):
    name: str = "zorgkaart_organisaties"
    allowed_domains: List[str] = ["zorgkaartnederland.nl"]

    start_urls: List[Dict[str, str]] = []
    max_page: Optional[int] = None

    def __init__(
        self,
        start_urls: Optional[str] = None,
        start_urls_file: Optional[str] = None,
        max_page: Optional[Union[str, int]] = None,
        *args: Any,
        **kwargs: Any
    ) -> None:
        super().__init__(*args, **kwargs)

        # --- Laad vanuit bestand ---
        if start_urls_file:
            try:
                with open(start_urls_file, "r", encoding="utf-8") as f:
                    self.start_urls = json.load(f)
                    assert isinstance(self.start_urls, list)
                self.logger.info(f"start_urls geladen vanuit bestand: {start_urls_file}")
            except Exception as e:
                self.logger.error(f"Fout bij laden start_urls bestand: {e}")
                self.start_urls = []

        # --- Of direct via argument ---
        elif start_urls:
            try:
                self.start_urls = json.loads(start_urls)
            except json.JSONDecodeError:
                try:
                    self.start_urls = ast.literal_eval(start_urls)
                except Exception as e:
                    self.logger.error(f"Kon start_urls niet parsen: {e}")
                    self.start_urls = []

        # --- max_page optioneel meegeven ---
        try:
            self.max_page = int(max_page) if max_page is not None else None
        except Exception as e:
            self.logger.error(f"Kon max_page niet omzetten naar int: {e}")
            self.max_page = None

        self.logger.info(f"start_urls ontvangen: {self.start_urls}")
        self.logger.info(f"max_page ingesteld op: {self.max_page}")

    async def start(self) -> AsyncGenerator[Request, None]:
        for entry in self.start_urls:
            url: str = entry.get("url")
            organisatietype: str = entry.get("organisatietype", "onbekend")

            if url:
                yield scrapy.Request(
                    url=url,
                    callback=self.parse,
                    meta={"organisatietype": organisatietype, "page": 1},
                    errback=self.error_handler
                )

    def parse(self, response: Response) -> Generator[Dict[str, Any], None, None]:
        organisatietype: str = response.meta["organisatietype"]
        current_page: int = response.meta["page"]
        page_url: str = response.url

        self.logger.info(f"[{organisatietype}] Pagina {current_page} geladen: {page_url}")
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

        # Volgende pagina
        if response.css('ul.pagination a.page-link')[-1:]:
            base_url = response.url.split("/pagina")[0]
            next_page_url = f"{base_url}/pagina{current_page + 1}"
            self.logger.info(f"[{organisatietype}] Volgende pagina: {next_page_url}")
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
        self.logger.error(f"[{organisatietype}] FOUT bij ophalen {request.url} → {repr(failure.value)}")
