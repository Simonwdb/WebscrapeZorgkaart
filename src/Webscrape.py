import time
import requests
import bs4
import re
import json

from typing import Dict, List, Union, Tuple, Optional


class Webscrape:
    def __init__(self, base_url: str) -> None:
        self.base_url: str = base_url
        self.headers: dict[str, str] = {
            'User-Agent': (
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                'AppleWebKit/537.36 (KHTML, like Gecko) '
                'Chrome/114.0.0.0 Safari/537.36'
            )
        }
    
    def get_page_total(self, facility: str) -> Union[int, None]:
        temp_url: str = f'{self.base_url}/{facility.lower()}'
        response = requests.get(url=temp_url, headers=self.headers)

        if response.status_code != 200:
            return None
        
        soup = bs4.BeautifulSoup(response.content, 'lxml')
        uls = soup.find('ul', class_='pagination justify-content-center')
        links = uls.find_all('a', class_='page-link')
        result = links[-1]
        int_result = int(result.get_text(strip=True))
        return int_result

    
    def get_filter_result(self, facility: str, page_id: int = 1) -> Union[List[bs4.element.Tag], None]:
        temp_url: str = f'{self.base_url}/{facility.lower()}/pagina{page_id}'
        response = requests.get(url=temp_url, headers=self.headers)

        if response.status_code != 200:
            return None
        
        soup = bs4.BeautifulSoup(response.content, 'lxml')
        filter_results = soup.find('div', class_='filter-results')
        result = filter_results.find_all('div', class_='filter-result')
        return result
    
    def get_filter_links(self, results: List[bs4.element.Tag]) -> Dict[str, str]:
        result_dict: Dict[str, str] = {}
        item: bs4.element.Tag
        for item in results:
            name_tag = item.find('a', class_='filter-result__name')
            if name_tag:
                name = name_tag.get_text(strip=True)
                href = name_tag.get('href')
                if href:
                    full_url = f'{self.base_url}{href}'
                    result_dict[name] = full_url
        
        return result_dict

    @staticmethod
    def split_address(full_address: str) -> Tuple[str, Optional[str], Optional[str]]:
        match = re.match(r'^(.+?)\s(\d+)\s?([a-zA-Z]*)$', full_address.strip())
        if match:
            street: str = match.group(1)
            number: str = match.group(2)
            addition: Optional[str] = match.group(3) if match.group(3) else None
            return street, number, addition
        else:
            return full_address, None, None
    
    def get_facility_info(self, facility_url: str) -> Union[Dict[str, str], None]:
        response = requests.get(url=facility_url, headers=self.headers)

        if response.status_code != 200:
            return None
        
        soup = bs4.BeautifulSoup(response.content, 'html.parser')
        script = soup.find('script', type='application/ld+json')
        data = json.loads(script.string)
        address = data.get('address')
        place = address.get('addressLocality')
        postal_code = address.get('postalCode')
        street_address = address.get('streetAddress')
        address_split = self.split_address(full_address=street_address)
        result = {
            'plaats': place,
            'postcode': postal_code,
            'straat': address_split[0],
            'huisnummer': address_split[1],
            'toevoeging': address_split[2]
        }

        return result


