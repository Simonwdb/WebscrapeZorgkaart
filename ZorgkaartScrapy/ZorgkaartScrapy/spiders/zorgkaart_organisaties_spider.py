import scrapy
from typing import List, Dict, Union, Optional, AsyncGenerator, Any, Generator

import scrapy.http

class ZorgkaartOrganisatiesSpider(scrapy.Spider):
    name: str = "zorgkaart_organisaties"
    allowed_domains: List[str] = ["zorgkaartnederland.nl"]

    # Voor nu test je op één type. Later maken we dit dynamisch.
    start_urls: List[str] = [
        "https://www.zorgkaartnederland.nl/tandartsenpraktijk"
    ]

    max_page: Optional[int] = None  # Beperk scraping tot eerste 5 pagina’s

    def __init__(self, max_page: Optional[str] = None, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        if max_page is not None:
            try:
                self.max_page = int(max_page)
            except ValueError:
                self.logger.warning(f"Ongeldige waarde voor max_page: {max_page}. Ignoreren.")
                self.max_page = None

    async def start(self) -> AsyncGenerator[scrapy.Request, None]:
        for url in self.start_urls:
            organisatietype = url.strip("/").split("/")[-1]
            yield scrapy.Request(url, callback=self.parse, meta={"organisatietype": organisatietype})

    def parse(self, response: scrapy.http.Request) -> Generator[Dict[str, any], None, None]:
        organisatietype: str = response.meta["organisatietype"]

        # Alle zorginstellingen op deze pagina
        for item in response.css('div.filter-result'):
            naam: str | None = item.css('a.filter-result__name::text').get()
            relatieve_link: str | None = item.css('a.filter-result__name::attr(href)').get()
            if naam and relatieve_link:
                yield {
                    "organisatietype": organisatietype,
                    "naam": naam.strip(),
                    "url": response.urljoin(relatieve_link.strip())
                }

        # Bepaal huidig paginanummer
        if "pagina" in response.url:
            current_page: int = int(response.url.split("pagina")[-1])
        else:
            current_page = 1

        # Navigeer naar volgende pagina als limiet niet is bereikt
        if current_page < self.max_page:
            base_url: str = response.url.split("/pagina")[0]
            next_page_url: str = f"{base_url}/pagina{current_page + 1}"
            yield scrapy.Request(
                next_page_url,
                callback=self.parse,
                meta={"organisatietype": organisatietype}
            )
