# wsj-scraper

Requirements are in `requirements.txt`

To run the scraper, run `scrapy crawl wsj-scraper` in the root directory.

To run in batches in Linux,

1. use `screen -S 1wsj` to create a new screen that can run in the background
2. Modify `NUM_BATCHES` and `CURRENT_BATCH` in `batch_settings.py`
3. Start with the first batch with `scrapy crawl wsj-scraper`
4. Press Ctrl+A+D to exit the screen
5. use `screen -S 2wsj` to create a second screen
6. modify batch settings
7. run the scraper
8. continue as many times as wished

When data is done scraping:
Combine the xlsx documents with `python3 util.py <file1> <file2> ...`
