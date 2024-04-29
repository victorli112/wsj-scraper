# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from openpyxl import Workbook
import pandas as pd

from batch_settings import CURRENT_BATCH
from wsj_scraper.items import FailedText


class WsjScraperPipeline:
    def open_spider(self, spider):
        # open excel 
        self.data = []
        self.seen = set()
        self.no_archived_article = 0
        
    def close_spider(self, spider):
        print(f"Number of articles scraped: {len(self.data)}")
        print(f"Number of articles not archived: {self.no_archived_article}")
        print("Saving...")
        df = pd.DataFrame(self.data)
        df.to_excel(f"wsj_data{CURRENT_BATCH}.xlsx", index=False)
    
    def process_item(self, item, spider):
        if (item['title'],item['date']) in self.seen:
            return item
        self.seen.add((item['title'],item['date']))
        
        if isinstance(item, FailedText):
            print(f"[ARCHIVING-F] Total: {self.no_archived_article} | Failed to scrape article: {item['title']} | Link {item['meta']}")
            self.no_archived_article += 1
            return item
        
        print(f"[ARCHIVING] Total: {len(self.seen)} | Scraped article: {item['title']}")
        self.data.append({
            'date': item['date'], 
            'title': item['title'], 
            'section': item['section'], 
            'text': item['text']
        })
