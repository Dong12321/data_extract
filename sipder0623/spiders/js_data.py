import re
from urllib.parse import urlparse
from datetime import datetime
import scrapy
from scrapy import Selector
from sipder0623.items import NewsItem


class JsDataSpider(scrapy.Spider):
    name = "js_data"
    allowed_domains = ["www.middleeasteye.net"]

    def start_requests(self):
        # 抓取第40到60页
        for page_num in range(40, 61):
            url = f"https://www.middleeasteye.net/news?page={page_num}"
            yield scrapy.Request(url, callback=self.parse)

    def parse(self, response):
        sel = Selector(response)
        articles = sel.css('.views-rows .mee-article-tile')

        for article in articles:
            url = article.css('.mee-tile-title::attr(href)').get()
            if url:
                full_url = response.urljoin(url)
                yield scrapy.Request(full_url, callback=self.parse_detail)

    def parse_detail(self, response):
        item = NewsItem()

        # URL
        item['url'] = response.url

        # site
        parsed_url = urlparse(response.url)
        item['site'] = parsed_url.hostname.replace('www.', '') if parsed_url.hostname else ''

        # source
        site_name = response.css('meta[property="og:site_name"]::attr(content)').get()
        item['source'] = site_name.strip() if site_name else ''

        # foreign_title
        title = response.css('.page-title .field-title::text').get()
        item['foreign_title'] = title.strip() if title else ''

        # news_time
        submitted_div = response.css('div.submitted-date')
        date_text_node = submitted_div.xpath('./text()[normalize-space()]').get()
        if date_text_node:
            date_text_node = date_text_node.strip()
            try:
                dt = datetime.strptime(date_text_node, "%d %B %Y %H:%M %Z")
            except ValueError:
                try:
                    dt = datetime.strptime(date_text_node.replace(" BST", ""), "%d %B %Y %H:%M")
                except Exception:
                    dt = None
            item['news_time'] = dt.strftime("%Y-%m-%dT%H:%M:%S") if dt else None
        else:
            item['news_time'] = None

        # foreign_content 格式为 <html>\n <body>\n  <p>\n  ...\n  </p>\n </body>\n</html>
        text_content = response.css('div.field-body *::text').getall()
        clean_lines = [line.strip() for line in text_content if line.strip()]
        joined_text = ' '.join(clean_lines)

        formatted_html = (
            "<html>\n"
            " <body>\n"
            "  <p>\n"
            f"  {joined_text}\n"
            "  </p>\n"
            " </body>\n"
            "</html>"
        )

        item['foreign_content'] = formatted_html

        # content
        text_content = response.css('div.field-body *::text').getall()
        clean_text = ' '.join([t.strip() for t in text_content if t.strip()])
        item['content'] = clean_text

        # 中文字段空
        item['chinese_title'] = ''
        item['chinese_content'] = ''

        yield item
