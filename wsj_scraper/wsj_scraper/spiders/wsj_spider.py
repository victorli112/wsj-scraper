from bs4 import BeautifulSoup
import scrapy
from wsj_scraper.items import FailedText, WsjScraperItem

BASE_WSJ = "https://www.wsj.com"
ARCHIVE_URL = "https://archive.is/"

# do the same as scrape_prh.py but with scrapy
class spiders(scrapy.Spider):
    name = "wsj-scraper"
    start_urls = ["https://www.wsj.com/news/archive/years"]
    
    def parse(self, response):
        soup = BeautifulSoup(response.body, 'lxml')
        div_block = soup.find('div', class_='WSJTheme--news-archive-index--M_Cc80sW')

        # Get all the hrefs in the div block
        hrefs = [a['href'] for a in div_block.find_all('a', href=True)]
        
        for href in hrefs[len(hrefs)//2 - 10:]:
            yield scrapy.Request(BASE_WSJ + href, callback=self.parse_monthly_links)
    
    # ex input link: https://www.wsj.com/news/archive/2021/january
    def parse_monthly_links(self, response):
        soup = BeautifulSoup(response.body, 'lxml')
        block = soup.find('ul', class_='WSJTheme--dates--3oHB2Rwn')

        hrefs = [a['href'] for a in block.find_all('a', href=True)]
        for href in hrefs:
            yield scrapy.Request(BASE_WSJ + href, callback=self.parse_daily_links)
        
    
    # ex input link: https://www.wsj.com/news/archive/2021/01/01
    def parse_daily_links(self, response):
        request_url = response.request.url
        date = f'{request_url.split("/")[-3]}-{request_url.split("/")[-2]}-{request_url.split("/")[-1]}'
        if '?' in date:
            date = date.split('?')[0]
        soup = BeautifulSoup(response.body, 'lxml')
        # find all articles in the page
        articles = soup.find_all('div', class_='WSJTheme--overflow-hidden--qJmlzHgO')
        for article in articles:
            try:
                title = article.find('span', class_='WSJTheme--headlineText--He1ANr9C').text
                section_block = article.find('div', class_='WSJTheme--articleType--34Gt-vdG')
                if section_block:
                    section = section_block.text
                else:
                    section = ""
                date = date
                article_link = article.find('span', class_='WSJTheme--headlineText--He1ANr9C').parent['href']
                # old links have 
                # we need to change http to https, remove replace online with www, and remove html, and replace article with articles
                if "online" in article_link:
                    article_link = article_link.replace("online", "www").replace("http", "https").replace(".html", "").replace("article", "articles")
            except: 
                print("failed parsing data, saved data to log txt")
                f = open("log.txt", "a")
                f.write(f"Failed to parse data: {response.request.url}\n{article}\n\n")
                continue    
            yield scrapy.Request(url=f'{ARCHIVE_URL}{article_link}', callback=self.find_archived_text, meta={'title': title, 'section': section, 'date': date})
            
        # if there is a next page, go to it
        next_page = soup.find('span', text='Next Page')
        if next_page:
            next_page_link = next_page.parent['href']
            yield scrapy.Request(BASE_WSJ + next_page_link, callback=self.parse_daily_links)

    # search archive.ph for the article
    def find_archived_text(self, response):
        soup = BeautifulSoup(response.body, 'lxml')
        first_row = soup.find('div', id='row0')
        if not first_row:
            yield FailedText(title=response.meta['title'], date=response.meta['date'], meta=response.request.url)
        else:
            archived_link = first_row.find('a')['href']
            yield scrapy.Request(callback=self.parse_archived_article, url = archived_link, meta={'title': response.meta['title'], 'section': response.meta['section'], 'date': response.meta['date']})
    
    def parse_archived_article(self, response):
        soup = BeautifulSoup(response.body, 'lxml')
        all_paragraphs = soup.find_all('div', attrs={'data-type': 'paragraph'})
        text = ""
        for paragraph in all_paragraphs:
            text += paragraph.text
        yield WsjScraperItem(title=response.meta['title'], section=response.meta['section'], date=response.meta['date'], text=text)
