# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy

class WsjScraperItem(scrapy.Item):
    date = scrapy.Field()
    title = scrapy.Field()
    section = scrapy.Field()
    text = scrapy.Field()

class FailedText(scrapy.Item):
    title = scrapy.Field()
    date = scrapy.Field()
    meta = scrapy.Field()
