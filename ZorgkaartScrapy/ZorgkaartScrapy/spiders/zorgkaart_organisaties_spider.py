import scrapy


class ZorgkaartOrganisatiesSpider(scrapy.Spider):
    name = "zorgkaart_organisaties"
    allowed_domains = ["zorgkaartnederland.nl"]

    # Voor nu test je op één type. Later maken we dit dynamisch.
    start_urls = [
        "https://www.zorgkaartnederland.nl/tandartsenpraktijk"
    ]

    max_page = 5  # Beperk scraping tot eerste 5 pagina’s

    async def start(self):
        for url in self.start_urls:
            organisatietype = url.strip("/").split("/")[-1]
            yield scrapy.Request(url, callback=self.parse, meta={"organisatietype": organisatietype})

    def parse(self, response):
        organisatietype = response.meta["organisatietype"]

        # Alle zorginstellingen op deze pagina
        for item in response.css('div.filter-result'):
            naam = item.css('a.filter-result__name::text').get()
            relatieve_link = item.css('a.filter-result__name::attr(href)').get()
            if naam and relatieve_link:
                yield {
                    "organisatietype": organisatietype,
                    "naam": naam.strip(),
                    "url": response.urljoin(relatieve_link.strip())
                }

        # Bepaal huidig paginanummer
        if "pagina" in response.url:
            current_page = int(response.url.split("pagina")[-1])
        else:
            current_page = 1

        # Navigeer naar volgende pagina als limiet niet is bereikt
        if current_page < self.max_page:
            base_url = response.url.split("/pagina")[0]
            next_page_url = f"{base_url}/pagina{current_page + 1}"
            yield scrapy.Request(
                next_page_url,
                callback=self.parse,
                meta={"organisatietype": organisatietype}
            )
