import os
import pandas as pd


class ExcelExportPipeline:
    def __init__(self):
        self.items = []

    def process_item(self, item, spider):
        self.items.append(dict(item))
        return item

    def close_spider(self, spider):
        os.makedirs('data', exist_ok=True)
        filename = os.path.join('data', f'{spider.name}.xlsx')
        df = pd.DataFrame(self.items)
        df.to_excel(filename, index=False)
        spider.logger.info(f"Excel-bestand succesvol geschreven: {filename}")
