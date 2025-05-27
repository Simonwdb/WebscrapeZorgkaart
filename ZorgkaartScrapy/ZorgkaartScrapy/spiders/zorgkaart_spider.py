import scrapy
import json
import re


class ZorgkaartSpider(scrapy.Spider):
    name = "zorgkaart"
    allowed_domains = ["zorgkaartnederland.nl"]
    start_urls = ["https://www.zorgkaartnederland.nl/overzicht/organisatietypes"]

    def parse(self, response):
        links = response.css('div.search-list a::attr(href)').getall()
        for link in links:
            facility = link.strip('/')
            yield scrapy.Request(
                url=response.urljoin(link),
                callback=self.parse_facility_pages,
                meta={'facility': facility, 'page': 1}
            )

    def parse_facility_pages(self, response):
        facility = response.meta['facility']
        current_page = response.meta['page']

        # Process current page
        result_blocks = response.css('div.filter-result')
        for block in result_blocks:
            href = block.css('a.filter-result__name::attr(href)').get()
            name = block.css('a.filter-result__name::text').get()
            if href:
                yield response.follow(
                    href,
                    callback=self.parse_facility_info,
                    meta={'name': name}
                )

        # Pagination handling
        last_page_link = response.css('ul.pagination a.page-link::text')[-1].get()
        try:
            last_page = int(last_page_link)
        except (TypeError, ValueError, IndexError):
            last_page = 1

        if current_page < last_page:
            next_page = current_page + 1
            next_url = f"https://www.zorgkaartnederland.nl/{facility}/pagina{next_page}"
            yield scrapy.Request(
                url=next_url,
                callback=self.parse_facility_pages,
                meta={'facility': facility, 'page': next_page}
            )

    def parse_facility_info(self, response):
        name = response.meta.get('name')
        script_tag = response.css('script[type="application/ld+json"]::text').get()
        if not script_tag:
            return

        try:
            data = json.loads(script_tag)
            address = data.get('address', {})
            street, number, addition = self.split_address(address.get('streetAddress', ''))

            yield {
                'naam': name,
                'plaats': address.get('addressLocality'),
                'postcode': address.get('postalCode', '').replace(' ', ''),
                'straat': street,
                'huisnummer': int(number) if number else None,
                'toevoeging': addition
            }
        except Exception as e:
            self.logger.warning(f"Fout bij verwerken JSON van {name}: {e}")

    def split_address(self, full_address):
        match = re.match(r'^(.*?)\s(\d+)\s*(.*)$', full_address.strip())
        if match:
            straat = match.group(1).strip()
            nummer = match.group(2).strip()
            toevoeging_raw = match.group(3).strip()
            toevoeging = toevoeging_raw.lstrip(', ').strip() if toevoeging_raw else None
            return straat, nummer, toevoeging
        else:
            return full_address.strip(), None, None
