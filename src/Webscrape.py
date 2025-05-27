import re
import bs4
import json
import time
import requests
import pandas as pd

from Facility import Facility
from typing import Dict, List, Union, Tuple, Optional


class Webscrape:
    def __init__(self, base_url: str) -> None:
        self.base_url: str = base_url
        self.session: requests.Session = requests.Session()
        self.session.headers.update({
            'User-Agent': (
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                'AppleWebKit/537.36 (KHTML, like Gecko) '
                'Chrome/114.0.0.0 Safari/537.36'
            )
        })
    
    def get_all_facilities(self) -> List[str]:
        endpoint: str = 'overzicht/organisatietypes'
        temp_url: str = f'{self.base_url}/{endpoint}'
        response = self.session.get(url=temp_url)

        if response.status_code != 200:
            return []
        
        soup = bs4.BeautifulSoup(response.content, 'html.parser')
        search_list = soup.find('div', class_='search-list')
        
        if not search_list:
            return []

        facility_tags = search_list.find_all('a', href=True)
        facilities = [tag['href'].lstrip('/') for tag in facility_tags]

        return facilities

    
    def get_page_total(self, facility: str) -> Union[int, None]:
        temp_url: str = f'{self.base_url}/{facility.lower()}'
        response = self.session.get(url=temp_url)

        if response.status_code != 200:
            return None
        
        soup = bs4.BeautifulSoup(response.content, 'lxml')
        pagination = soup.find('ul', class_='pagination justify-content-center')

        if not pagination:
            return 1

        links = pagination.find_all('a', class_='page-link')
        try:
            return int(links[-1].get_text(strip=True))
        except (IndexError, ValueError):
            return None

    
    def get_filter_result(self, facility: str, page_id: int = 1) -> Union[List[bs4.element.Tag], None]:
        temp_url: str = f'{self.base_url}/{facility.lower()}/pagina{page_id}'
        response = self.session.get(url=temp_url)

        if response.status_code != 200:
            return None
        
        soup = bs4.BeautifulSoup(response.content, 'lxml')
        results_container = soup.find('div', class_='filter-results')
        
        if not results_container:
            return None

        return results_container.find_all('div', class_='filter-result')
    
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
        match = re.match(r'^(.*?)\s(\d+)\s*(.*)$', full_address.strip())
        if match:
            street: str = match.group(1).strip()
            number: str = match.group(2).strip()
            addition_raw: str = match.group(3).strip()
            addition: Optional[str] = addition_raw.lstrip(', ').strip() if addition_raw else None
            return street, number, addition
        else:
            return full_address.strip(), None, None
    
    def get_facility_info(self, facility_url: str) -> Union[Dict[str, str], None]:
        response = self.session.get(url=facility_url)

        if response.status_code != 200:
            return None
        
        soup = bs4.BeautifulSoup(response.content, 'html.parser')
        script = soup.find('script', type='application/ld+json')

        if script is None or not script.string:
            return None

        data = json.loads(script.string)
        address = data.get('address')
        street_address = address.get('streetAddress')

        if not street_address:
            return None

        address_split = self.split_address(full_address=street_address)

        result = {
            'plaats': address.get('addressLocality'),
            'postcode': address.get('postalCode', '').replace(' ', ''),
            'straat': address_split[0],
            'huisnummer': int(address_split[1]),
            'toevoeging': address_split[2]
        }

        return result
    
    @staticmethod
    def write_to_excel_file(data: Union[List[Dict[str, str]], List[List[str]]],
                            file_name: str,
                            col_names: List[str] = None) -> None:
        if isinstance(data, list) and data and isinstance(data[0], dict):
            df = pd.DataFrame(data)
        elif isinstance(data, list) and col_names:
            df = pd.DataFrame(data, columns=col_names)
        else:
            raise ValueError("Invalid data format. Provide either a list of dicts or list of lists with column names.")

        df.to_excel(file_name, index=False)
        print(f'Data successfully written to file: {file_name}')

