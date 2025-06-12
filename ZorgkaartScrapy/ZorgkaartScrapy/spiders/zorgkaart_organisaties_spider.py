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
            print(f"Fout bij laden start_urls bestand: {e}")
            all_items = []

        for item in all_items:
            try:
                aantal = item.get("aantal")
                count = item.get("scraped_count", 0)

                if isinstance(aantal, int) and count >= aantal:
                    print(f"Overslaan: {item['organisatietype']} (volledig gescrapet)")
                    continue

                start_page = ceil(count / 20) + 1
                item["start_page"] = start_page
                self.start_urls.append(item)

            except Exception as e:
                print(f"Fout bij verwerken item: {e}")

        try:
            self.max_page = int(max_page) if max_page is not None else None
        except Exception as e:
            print(f"Kon max_page niet omzetten naar int: {e}")
            self.max_page = None

        print(f"{len(self.start_urls)} organisatietypes opgenomen voor scraping.")

    async def start(self) -> AsyncGenerator[Request, None]:
        for entry in self.start_urls:
            url: str = entry.get("url")
            organisatietype: str = entry.get("organisatietype", "onbekend")
            start_page: int = entry.get("start_page", 1)

            if url:
                pagina_url = f"{url}/pagina{start_page}" if start_page > 1 else url
                print(f"Start scraping voor: {organisatietype} vanaf pagina {start_page} → {pagina_url}")
                yield scrapy.Request(
                    url=pagina_url,
                    callback=self.parse,
                    meta={
                        "organisatietype": organisatietype,
                        "page": start_page,
                        "start_page": start_page
                    },
                    errback=self.error_handler
                )

    def parse(self, response: Response) -> Generator[Dict[str, Any], None, None]:
        organisatietype = response.meta["organisatietype"]
        current_page = response.meta["page"]
        start_page = response.meta["start_page"]

        print(f"[{organisatietype}] Pagina {current_page} geladen: {response.url}")

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
            print(f"[{organisatietype}] Geen resultaten gevonden op pagina {current_page}")

        # Nieuwe max_page logica: max aantal extra pagina’s
        if self.max_page is not None and (current_page - start_page) >= self.max_page:
            print(f"[{organisatietype}] Max aantal extra pagina’s ({self.max_page}) bereikt vanaf pagina {start_page}")
            return

        # Check of er een volgende pagina beschikbaar is
        if response.css('ul.pagination a.page-link')[-1:]:
            base_url = response.url.split("/pagina")[0]
            next_page_url = f"{base_url}/pagina{current_page + 1}"
            print(f"[{organisatietype}] Volgende pagina: {next_page_url}")
            yield scrapy.Request(
                url=next_page_url,
                callback=self.parse,
                meta={
                    "organisatietype": organisatietype,
                    "page": current_page + 1,
                    "start_page": start_page
                },
                errback=self.error_handler,
                dont_filter=True
            )

    def error_handler(self, failure: Failure) -> None:
        request = failure.request
        organisatietype = request.meta.get("organisatietype", "onbekend")
        print(f"[{organisatietype}] FOUT bij ophalen {request.url} → {repr(failure.value)}")
