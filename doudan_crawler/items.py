# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class DoudanCrawlerItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass


class FilmItem(scrapy.Item):
    # define the fields for your item here like:
    id = scrapy.Field()  # 豆瓣id
    name = scrapy.Field()  # 电影名
    director = scrapy.Field()  # 导演
    screenwriter = scrapy.Field()  # 剧本
    type = scrapy.Field()  # 电影类型
    actor = scrapy.Field()  # 主演
    country = scrapy.Field()  # 制片国家/地区
    score = scrapy.Field()  # 评分
    votes = scrapy.Field()  # 评论人数
    year = scrapy.Field()  # 上映时间
    compare = scrapy.Field()  # 与同类电影对比


class CommentItem(scrapy.Item):
    content = scrapy.Field()  # 评论
    star = scrapy.Field()  # 评分
    votes = scrapy.Field()  # 有用
    film_id = scrapy.Field()  # 电影id
