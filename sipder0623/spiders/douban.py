import scrapy
from scrapy import Selector
import re

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
            
            # 基本信息
            move_item['title'] = list_item.css('span.title::text').get()
            move_item['rank'] = list_item.css('span.rating_num::text').get()
            move_item['subject'] = list_item.css('p.quote span::text').get()
            
            # 获取电影详情页链接
            movie_link = list_item.css('.hd a::attr(href)').get()
            move_item['movie_url'] = movie_link
            
            # 获取评价人数
            # 尝试多种可能的选择器来获取评价人数
            rating_people_text = None
            
            # 方法1: 尝试获取评分后面的评价人数
            rating_people_text = list_item.css('span.rating_num + span::text').get()
            
            # 方法2: 如果方法1失败，尝试其他可能的选择器
            if not rating_people_text:
                rating_people_text = list_item.css('.star .rating_num + span::text').get()
            
            # 方法3: 尝试获取所有包含"人评价"的文本
            if not rating_people_text:
                all_spans = list_item.css('span::text').getall()
                for span_text in all_spans:
                    if '人评价' in span_text:
                        rating_people_text = span_text
                        break
            
            # 方法4: 尝试从评分区域获取
            if not rating_people_text:
                rating_div = list_item.css('.star')
                if rating_div:
                    rating_people_text = rating_div.css('span::text').getall()[-1] if rating_div.css('span::text').getall() else None
            
            if rating_people_text:
                # 提取数字，格式如 "(123456人评价)" 或 "123456人评价"
                people_match = re.search(r'(\d+)', rating_people_text)
                if people_match:
                    move_item['rating_people'] = people_match.group(1)
                else:
                    move_item['rating_people'] = ''
            else:
                move_item['rating_people'] = ''
            
            # 获取电影信息（导演、主演、年份、国家、类型）
            info_text = list_item.css('.bd p:first-child::text').getall()
            if info_text:
                # 清理文本
                info_clean = [text.strip() for text in info_text if text.strip()]
                if info_clean:
                    info_str = ' '.join(info_clean)
                    
                    # 清理特殊字符
                    info_str_clean = info_str.replace('\xa0', ' ').replace('\n', ' ')
                    
                    # 提取导演 - 查找"导演:"后面的内容
                    director_match = re.search(r'导演:\s*([^主\n]+?)(?:\s*主演:|$)', info_str_clean)
                    if director_match:
                        director_text = director_match.group(1).strip()
                        # 清理多余的字符
                        director_text = re.sub(r'\s*主.*$', '', director_text).strip()
                        move_item['director'] = director_text
                    else:
                        # 如果第一种方法失败，尝试更宽松的匹配
                        director_match = re.search(r'导演:\s*([^/\n]+?)(?:\s*\d{4}|$)', info_str_clean)
                        if director_match:
                            director_text = director_match.group(1).strip()
                            # 清理多余的字符
                            director_text = re.sub(r'\s*主.*$', '', director_text).strip()
                            move_item['director'] = director_text
                        else:
                            # 第三种方法：直接提取导演后面的内容直到遇到年份
                            director_match = re.search(r'导演:\s*([^0-9]+?)(?=\d{4})', info_str_clean)
                            if director_match:
                                director_text = director_match.group(1).strip()
                                # 清理多余的字符
                                director_text = re.sub(r'\s*主.*$', '', director_text).strip()
                                move_item['director'] = director_text
                            else:
                                move_item['director'] = ''
                    
                    # 提取主演 - 查找"主演:"后面的内容
                    actors_match = re.search(r'主演:\s*([^/\n]+?)(?:\s*\d{4}|$)', info_str_clean)
                    if actors_match:
                        move_item['actors'] = actors_match.group(1).strip()
                    else:
                        move_item['actors'] = ''
                    
                    # 提取年份
                    year_match = re.search(r'(\d{4})', info_str_clean)
                    if year_match:
                        move_item['year'] = year_match.group(1)
                    else:
                        move_item['year'] = ''
                    
                    # 提取国家/地区 - 查找年份后面的国家信息
                    country_match = re.search(r'\d{4}\s*/\s*([^/\n]+?)(?:\s*/\s*|$)', info_str_clean)
                    if country_match:
                        move_item['country'] = country_match.group(1).strip()
                    else:
                        move_item['country'] = ''
                    
                    # 提取类型 - 查找最后一个"/"后面的内容
                    genre_match = re.search(r'/\s*([^/\n]+?)(?:\s*$)', info_str_clean)
                    if genre_match:
                        move_item['genre'] = genre_match.group(1).strip()
                    else:
                        move_item['genre'] = ''
                else:
                    move_item['director'] = ''
                    move_item['actors'] = ''
                    move_item['year'] = ''
                    move_item['country'] = ''
                    move_item['genre'] = ''
            else:
                move_item['director'] = ''
                move_item['actors'] = ''
                move_item['year'] = ''
                move_item['country'] = ''
                move_item['genre'] = ''
            
            yield move_item
