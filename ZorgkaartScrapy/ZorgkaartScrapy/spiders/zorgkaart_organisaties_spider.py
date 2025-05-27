import scrapy


class ZorgkaartOrganisatiesSpider(scrapy.Spider):
    name = "zorgkaart_organisaties"
    allowed_domains = ["zorgkaartnederland.nl"]

    # Voor nu test je op één type. Later maken we dit dynamisch.
    start_urls = [
        "https://www.zorgkaartnederland.nl/tandartsenpraktijk"
    ]
    max_page = 5

    def parse(self, response):
        organisatietype = response.url.strip("/").split("/")[-1]

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

        # Huidig paginanummer bepalen
        if "pagina" in response.url:
            current_page = int(response.url.split("pagina")[-1])
        else:
            current_page = 1

        if current_page < self.max_page:
            next_page_url = f"https://www.zorgkaartnederland.nl/{organisatietype}/pagina{current_page + 1}"
            yield scrapy.Request(next_page_url, callback=self.parse)
