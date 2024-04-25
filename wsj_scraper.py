from bs4 import BeautifulSoup
from selenium import webdriver
import lxml
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
import time

URL = "https://www.wsj.com/news/archive/years" 
BASE_WSJ = "https://www.wsj.com"
SELENIUM_OPTIONS = Options()
SELENIUM_OPTIONS.add_argument("--window-size=1920,1080")
SELENIUM_OPTIONS.add_argument("--start-maximized")
SELENIUM_OPTIONS.add_argument("user-data-dir=/tmp/wsj_login")
# SELENIUM_OPTIONS.add_argument("--enable-javascript")
# SELENIUM_OPTIONS.add_argument("--headless=new")
SELENIUM_OPTIONS.binary_location = "/usr/bin/chromium-browser"
SELENIUM_OPTIONS.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36")

class WSJ_Scraper:
    def __init__(self):
        self.driver = webdriver.Chrome(options=SELENIUM_OPTIONS)
        self.data = []
        #print(self.get_free_proxies())
        self.login_wsj()

    def login_wsj(self):
        self.driver.get("https://www.wsj.com/login")
        time.sleep(120)
        
    def get_archived_data(self, url):
        self.driver.get(url)
        soup = BeautifulSoup(self.driver.page_source, 'lxml')
        div_block = soup.find('div', class_='WSJTheme--news-archive-index--M_Cc80sW')

        # Get all the hrefs in the div block
        hrefs = [a['href'] for a in div_block.find_all('a', href=True)]
        
        for href in hrefs:
            self.parse_monthly_links(BASE_WSJ + href)
            break
        
    # ex input link: https://www.wsj.com/news/archive/2021/january
    def parse_monthly_links(self, url):
        self.driver.get(url)
        soup = BeautifulSoup(self.driver.page_source, 'lxml')
        block = soup.find('ul', class_='WSJTheme--dates--3oHB2Rwn')

        hrefs = [a['href'] for a in block.find_all('a', href=True)]
        for href in hrefs:
            self.parse_daily_links(BASE_WSJ + href)
            break
    
    # ex input link: https://www.wsj.com/news/archive/2021/01/01
    def parse_daily_links(self, url):
        date = f'{url.split("/")[-3]}-{url.split("/")[-2]}-{url.split("/")[-1]}'
        self.driver.get(url)
        soup = BeautifulSoup(self.driver.page_source, 'lxml')
        # find all articles in the page
        articles = soup.find_all('div', class_='WSJTheme--overflow-hidden--qJmlzHgO')
        for article in articles:
            title = article.find('span', class_='WSJTheme--headlineText--He1ANr9C').text
            section = article.find('div', class_='WSJTheme--articleType--34Gt-vdG').text
            date = date
            article_link = article.find('span', class_='WSJTheme--headlineText--He1ANr9C').parent['href']
            self.parse_article(BASE_WSJ + article_link, title, section, date)
            break
        
        # if there is a next page, go to it
        next_page = soup.find('span', text='Next Page')
        if next_page:
            next_page_link = next_page.parent['href']
            self.parse_daily_links(BASE_WSJ + next_page_link)

    def parse_article(self, url, title, section, date):
        self.driver.get(url)
        soup = BeautifulSoup(self.driver.page_source, 'lxml')
        text = soup.find('article').text
        self.data.append({'title': title, 'section': section, 'date': date, 'text': text})

wsj = WSJ_Scraper()
# wsj.get_archived_data()