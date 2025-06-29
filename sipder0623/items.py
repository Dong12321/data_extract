# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class MovieItem(scrapy.Item):
    title = scrapy.Field()
    rank = scrapy.Field()
    subject = scrapy.Field()  # 添加 subject 字段
    # 新增字段
    director = scrapy.Field()  # 导演
    actors = scrapy.Field()    # 主演
    year = scrapy.Field()      # 年份
    country = scrapy.Field()   # 国家/地区
    genre = scrapy.Field()     # 类型
    rating_people = scrapy.Field()  # 评价人数
    movie_url = scrapy.Field()      # 电影详情页链接


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