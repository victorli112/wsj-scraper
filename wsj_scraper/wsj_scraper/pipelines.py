# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from openpyxl import Workbook
import pandas as pd

from wsj_scraper.items import FailedText


class WsjScraperPipeline:
    def open_spider(self, spider):
        # open excel 
        self.df = pd.DataFrame(columns=['Date', 'Title', 'Section', 'Text'])
        self.no_archived_article = 0
        
    def close_spider(self, spider):
        # save df to excel
        self.df.to_excel('wsj_data.xlsx', index=False)
        print(f"Number of articles scraped: {len(self.df)}")
        print(f"Number of articles not archived: {self.no_archived_article}")
    
    def process_item(self, item, spider):
        if isinstance(item, FailedText):
            self.no_archived_article += 1
            return item
        
        new_df = pd.DataFrame({
            'Date': item['date'], 
            'Title': item['title'], 
            'Section': item['section'], 
            'Text': item['text']
            }, index=[0])
        self.df = pd.concat([self.df, new_df], ignore_index=True)