import pandas as pd


class ExcelExportPipeline:
    def __init__(self):
        self.items = []

    def process_item(self, item, spider):
        # Voeg het item toe aan de lijst
        self.items.append(dict(item))
        return item

    def close_spider(self, spider):
        # Sla alles op in een Excel-bestand bij het afsluiten van de spider
        df = pd.DataFrame(self.items)
        df.to_excel("zorgkaart_output.xlsx", index=False)
        spider.logger.info(f"Excel-bestand succesvol geschreven: zorgkaart_output.xlsx")
