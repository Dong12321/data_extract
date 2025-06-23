import scrapy


class JsDataSpider(scrapy.Spider):
    name = "js_data"
    allowed_domains = ["www.middleeasteye.net"]
    start_urls = ["https://www.middleeasteye.net/"]

    def parse(self, response):
        pass
