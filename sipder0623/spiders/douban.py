import scrapy
from scrapy import Selector

from sipder0623.items import MovieItem


class DoubanSpider(scrapy.Spider):
    name = "douban"
    allowed_domains = ["movie.douban.com"]
    start_urls = ["https://movie.douban.com/top250"]

    def parse(self, response):
        sel = Selector(response)
        list_item = sel.css('#content > div > div.article > ol > li')
        for list_item in list_item:
            move_item = MovieItem()
            move_item['title'] = list_item.css('span.title::text').get()
            move_item['rank'] = list_item.css('span.rating_num::text').get()
            move_item['subject'] = list_item.css('p.quote span::text').get()
            yield move_item
