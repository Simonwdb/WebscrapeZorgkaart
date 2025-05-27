import ast
import scrapy
import json
from typing import List, Dict, Optional, Generator, Any, AsyncGenerator
import scrapy.http


class ZorgkaartOrganisatiesSpider(scrapy.Spider):
    name: str = "zorgkaart_organisaties"
    allowed_domains: List[str] = ["zorgkaartnederland.nl"]

    start_urls: List[str] = []
    max_page: Optional[int] = None

    def __init__(
        self,
        start_urls: Optional[str] = None,
        max_page: Optional[str] = None,
        *args: Any,
        **kwargs: Any
    ) -> None:
        super().__init__(*args, **kwargs)

        try:
            self.start_urls = json.loads(start_urls)
        except json.JSONDecodeError:
            try:
                self.start_urls = ast.literal_eval(start_urls)  # ondersteunt ook enkele quotes
            except Exception as e:
                self.logger.error(f"Kon start_urls niet parsen: {e}")
                self.start_urls = []

        try:
            self.max_page = int(max_page) if max_page is not None else None
        except Exception as e:
            self.logger.error(f"Kon max_page niet omzetten naar int: {e}")
            self.max_page = None

        self.logger.info(f"start_urls ontvangen: {self.start_urls}")
        self.logger.info(f"max_page ingesteld op: {self.max_page}")

    async def start(self) -> AsyncGenerator[scrapy.Request, None]:
        for url in self.start_urls:
            organisatietype: str = url.strip("/").split("/")[-1]
            yield scrapy.Request(
                url=url,
                callback=self.parse,
                meta={"organisatietype": organisatietype, "page": 1}
            )

    def parse(self, response: scrapy.http.Response) -> Generator[Dict[str, Any], None, None]:
        organisatietype: str = response.meta["organisatietype"]
        current_page: int = response.meta["page"]

        for item in response.css('div.filter-result'):
            naam: Optional[str] = item.css('a.filter-result__name::text').get()
            relatieve_link: Optional[str] = item.css('a.filter-result__name::attr(href)').get()

            if naam and relatieve_link:
                yield {
                    "organisatietype": organisatietype,
                    "naam": naam.strip(),
                    "url": response.urljoin(relatieve_link.strip())
                }

        if self.max_page is not None and current_page >= self.max_page:
            return

        next_page_exists = response.css('ul.pagination a.page-link')[-1:]
        if next_page_exists:
            base_url: str = response.url.split("/pagina")[0]
            next_page_url: str = f"{base_url}/pagina{current_page + 1}"
            yield scrapy.Request(
                url=next_page_url,
                callback=self.parse,
                meta={"organisatietype": organisatietype, "page": current_page + 1}
            )
