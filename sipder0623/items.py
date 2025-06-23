# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class MovieItem(scrapy.Item):
    title = scrapy.Field()
    rank = scrapy.Field()
    subject = scrapy.Field()  # 添加 subject 字段


# js新闻
class NewsItem(scrapy.Item):
    site = scrapy.Field()
    source = scrapy.Field()
    url = scrapy.Field()
    news_time = scrapy.Field()
    foreign_title = scrapy.Field()
    chinese_title = scrapy.Field()
    foreign_content = scrapy.Field()
    chinese_content = scrapy.Field()
    content = scrapy.Field()