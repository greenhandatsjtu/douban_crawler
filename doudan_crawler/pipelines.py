# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html

import pymysql

from . import settings


class FilmPipeline:
    def __init__(self):
        # 使用pymysql驱动连接数据库
        self.conn = pymysql.connect(
            host=settings.MYSQL_HOST,
            db=settings.MYSQL_DBNAME,
            user=settings.MYSQL_USER,
            passwd=settings.MYSQL_PASSWD,
            charset='utf8',
            use_unicode=True)
        self.cursor = self.conn.cursor()

    def process_item(self, item, spider):
        self.cursor.execute("""INSERT INTO film (id,`name`,director,screenwriter,`type`,actor,country,score,compare,`year`,votes)  
                                                        VALUES ("%d","%s", "%s", "%s", "%s","%s","%s","%f","%f","%d","%d")""" % (
            item['id'], pymysql.escape_string(item['name']), pymysql.escape_string(item['director']),
            pymysql.escape_string(item['screenwriter']), item['type'], pymysql.escape_string(item['actor']),
            item['country'], item['score'], item['compare'], item['year'], item['votes']))
        self.conn.commit()  # commit是必须的
        return item

    def spider_closed(self, spider):
        self.conn.close()  # close database


class CommentPipeline:
    def __init__(self):
        # 使用pymysql驱动连接数据库
        self.conn = pymysql.connect(
            host=settings.MYSQL_HOST,
            db=settings.MYSQL_DBNAME,
            user=settings.MYSQL_USER,
            passwd=settings.MYSQL_PASSWD,
            charset='utf8',
            use_unicode=True)
        self.cursor = self.conn.cursor()
        self.star_dict = {
            '很差': 1,
            '较差': 2,
            '还行': 3,
            '推荐': 4,
            '力荐': 5,
        }

    def process_item(self, item, spider):
        # str->int map
        try:
            item['star'] = self.star_dict[item['star']]
        except KeyError:
            item['star'] = 0

        self.cursor.execute("""INSERT INTO comment (film_id,content,star,votes)  
                                                        VALUES ("%d", "%s", "%d", "%d")""" % (
            item['film_id'], pymysql.escape_string(item['content']), item['star'], item['votes']))
        self.conn.commit()  # commit是必须的
        return item

    def spider_closed(self, spider):
        self.conn.close()  # close database
