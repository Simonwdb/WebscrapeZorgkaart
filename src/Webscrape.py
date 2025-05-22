import time
import requests
import bs4

from typing import Dict, List, Union


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
    
    def get_filter_result(self, facility: str) -> Union[List[bs4.element.Tag], None]:
        temp_url: str = f'{self.base_url}/{facility.lower()}'
        response = requests.get(url=temp_url, headers=self.headers)

        if response.status_code != 200:
            return None
        
        soup = bs4.BeautifulSoup(response.content, 'lxml')
        filter_results = soup.find('div', class_='filter-results')
        result = filter_results.find_all('div', class_='filter-result')
        return result