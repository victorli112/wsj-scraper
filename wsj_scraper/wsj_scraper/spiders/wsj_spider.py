from bs4 import BeautifulSoup
import scrapy
from scrapy_selenium import SeleniumRequest
from wsj_scraper.items import WsjScraperItem

BASE_WSJ = "https://www.wsj.com"
# do the same as scrape_prh.py but with scrapy
class spiders(scrapy.Spider):
    handle_httpstatus_list = [401]
    custom_settings = {
        "handle_httpstatus_list": [401],
    }
    name = "wsj-scraper"
    start_urls = ["https://www.wsj.com/news/archive/years"]
    
    def parse(self, response):
        soup = BeautifulSoup(response.body, 'lxml')
        div_block = soup.find('div', class_='WSJTheme--news-archive-index--M_Cc80sW')

        # Get all the hrefs in the div block
        hrefs = [a['href'] for a in div_block.find_all('a', href=True)]
        
        for href in hrefs:
            yield scrapy.Request(BASE_WSJ + href, callback=self.parse_monthly_links)
            break
    
    # ex input link: https://www.wsj.com/news/archive/2021/january
    def parse_monthly_links(self, response):
        soup = BeautifulSoup(response.body, 'lxml')
        block = soup.find('ul', class_='WSJTheme--dates--3oHB2Rwn')

        hrefs = [a['href'] for a in block.find_all('a', href=True)]
        for href in hrefs:
            yield scrapy.Request(BASE_WSJ + href, callback=self.parse_daily_links)
            break
    
    # ex input link: https://www.wsj.com/news/archive/2021/01/01
    def parse_daily_links(self, response):
        request_url = response.request.url
        date = f'{request_url.split("/")[-3]}-{request_url.split("/")[-2]}-{request_url.split("/")[-1]}'
        soup = BeautifulSoup(response.body, 'lxml')
        # find all articles in the page
        articles = soup.find_all('div', class_='WSJTheme--overflow-hidden--qJmlzHgO')
        for article in articles:
            title = article.find('span', class_='WSJTheme--headlineText--He1ANr9C').text
            section = article.find('div', class_='WSJTheme--articleType--34Gt-vdG').text
            date = date
            article_link = article.find('span', class_='WSJTheme--headlineText--He1ANr9C').parent['href']
            yield SeleniumRequest(url=article_link, callback=self.parse_article, meta={'title': title, 'section': section, 'date': date})
            break
        
        # if there is a next page, go to it
        next_page = soup.find('span', text='Next Page')
        if next_page:
            next_page_link = next_page.parent['href']
            yield scrapy.Request(BASE_WSJ + next_page_link, callback=self.parse_daily_links)

    def parse_article(self, response):
        if response.status == 401:
            print("---------- ERROR -----------")
            print(response.body)
            
        soup = BeautifulSoup(response.body, 'lxml')
        text = soup.find('article').text
        yield WsjScraperItem(title=response.meta['title'], section=response.meta['section'], date=response.meta['date'], text=text)