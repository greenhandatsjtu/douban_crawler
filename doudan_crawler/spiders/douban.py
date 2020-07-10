# -*- coding: utf-8 -*-
import re

from scrapy import Request
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule

from ..items import FilmItem, CommentItem
from .. import settings


class FilmSpider(CrawlSpider):
    custom_settings = {
        'ITEM_PIPELINES': {
            'doudan_crawler.pipelines.FilmPipeline': 300,
        }
    }
    name = 'film'
    allowed_domains = ['douban.com']
    start_urls = settings.start_urls

    # extract film link
    rules = (
        # 豆列翻页
        Rule(LinkExtractor(allow='/doulist/\d+/\??', restrict_css='span.next>a[href]')),
        # 电影详情页
        Rule(LinkExtractor(allow='subject/\d+/', restrict_css='.bd.doulist-subject > div.title > a[href]'),
             callback='parse_film',
             follow=False),
    )

    def parse_film(self, response):
        item = FilmItem()

        # douban id
        item['id'] = int(re.findall('\d+', response.url)[0])

        # 电影名
        item['name'] = response.css('span[property="v:itemreviewed"]::text').get()

        # 评分
        item['score'] = float(response.css(".rating_num::text").get())

        # 评论人数
        item['votes'] = int(response.css('span[property="v:votes"]::text').get())

        # 制片国家/地区 需要考虑合拍电影
        country = response.css('#info').re_first('制片国家/地区:</span>(.*?)<br>').strip()
        raw_countries = country.split('/')
        countries = []
        for value in raw_countries:
            countries.append(value.strip())
        item['country'] = ','.join(countries)

        # 导演
        director = response.css('a[rel="v:directedBy"]::text').getall()
        item['director'] = ','.join(director[:5])  # 只取前5个

        # 编剧
        text = response.css('#info>span').re_first(".*编剧.*")
        # 有些电影没有编剧，需要进行判断
        if text:
            screenwriter = re.findall("<a.*?>(.*?)</a>", text)
            item['screenwriter'] = ','.join(screenwriter[:5])  # 只取前5个
        else:
            item['screenwriter'] = str()

        # 只选取重要主演
        actors = response.css('span>a[rel="v:starring"]::text').getall()
        item['actor'] = ','.join(actors[:10])
        # 类型
        _types = response.css('span[property="v:genre"]::text').getall()
        item['type'] = ','.join(_types)

        # 上映时间
        item['year'] = int(response.css('span.year::text').get().strip('()'))

        # 与同类电影对比
        better_than = response.css("div.rating_betterthan>a::text").re("\d+")
        compare = 0
        # 有些电影没有对比，需要进行判断
        if len(better_than):
            for value in better_than:
                compare += float(value)
            item['compare'] = compare / len(better_than)
        else:
            item['compare'] = 0
        yield item


class CommentSpider(CrawlSpider):
    custom_settings = {
        'ITEM_PIPELINES': {
            'doudan_crawler.pipelines.CommentPipeline': 300,
        }
    }
    name = 'comment'
    allowed_domains = ['douban.com']
    start_urls = settings.start_urls

    # extract film link
    rules = (
        # 豆列翻页
        Rule(LinkExtractor(allow='/doulist/\d+/', restrict_css='span.next>a[href]'), follow=True),
        # 电影详情页
        Rule(LinkExtractor(allow='subject/\d+/', restrict_css='.bd.doulist-subject > div.title > a[href]'),
             callback='get_comment_url',
             follow=False),
        # 评论页
        # Rule(LinkExtractor(allow='/subject/\d+/comments',
        #                    restrict_css='#comments-section span.pl > a[href]'), callback='parse_comment',
        #      follow=False),
        # 评论翻页
        # Rule(LinkExtractor(allow='/subject/\d+/comments', restrict_css='a.next[href]'),
        #      callback='parse_comment', follow=True),
    )

    # 获取评论链接
    def get_comment_url(self, response):
        url = response.css('#comments-section span.pl > a[href]').attrib['href']
        if url:
            yield Request(url=url, callback=self.parse_comment)

    # 提取短评信息
    def parse_comment(self, response):
        item = CommentItem()
        _id = int(re.findall('\d+', response.url)[0])
        comments = response.css('.comment')
        for comment in comments:
            item['film_id'] = _id
            # 评论
            item['content'] = comment.css('span.short::text').get()
            # 评分
            try:
                item['star'] = comment.css('span.rating').attrib['title']
            except KeyError:
                item['star'] = 0
            # 有用
            item['votes'] = int(comment.css('.votes::text').get())
            yield item
        try:
            url = response.css('a.next[href]').attrib['href']
            if url:
                # 限制爬取评论数
                if int(re.findall('start=(\d+)', url)[0]) >= 200:
                    return
                url = re.sub('\?.*', '', response.url) + url
                yield Request(url=url, callback=self.parse_comment)
        except AttributeError:
            pass
