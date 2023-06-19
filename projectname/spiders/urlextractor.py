import scrapy
from scrapy_selenium import SeleniumRequest
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from urllib.parse import urlparse

class URLSpider(scrapy.Spider):
    name = "url_spider"

    # Replace with the domain you're interested in
    allowed_domains = ["chargebacks911.com"]
    start_urls = ['https://chargebacks911.com/articles/']

    def start_requests(self):
        for url in self.start_urls:
            yield SeleniumRequest(url=url, callback=self.parse)

    def parse(self, response):
        driver = response.request.meta['driver']
        domain_name = urlparse(response.url).netloc

        # Scroll down until no more new content is loaded
        while True:
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            try:
                # Wait for content to load
                WebDriverWait(driver, 5).until(EC.staleness_of(driver.find_element(By.CSS_SELECTOR, "div")))

            except Exception:
                break

        # Get the final HTML and create a new response object
        body = driver.page_source
        new_response = response.replace(body=body)

        # Extract all the URLs from the page
        selectors = ['div.p-articles-resource-buttons__item a::attr(href)',
                     'div.p-articles-main__item a::attr(href)']
                     
        for selector in selectors:
            for href in new_response.css(selector).extract():
                url = new_response.urljoin(href)
                if urlparse(url).netloc == domain_name:
                    yield {
                        'URL': url
                    }
                
        yield SeleniumRequest(url=url, callback=self.parse)

