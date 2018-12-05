# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import pymongo


class LiepinSpiderPipeline(object):

    def open_spider(self, spider):
        self.client = pymongo.MongoClient(**spider.settings['MONGODB_CONFIG'])
        self.db = self.client.liepin_spider
        self.coll = self.db.jobs

    def close_spider(self, spider):
        self.client.close()

    # def save_files(self, item, spider):
    #     with open('liepin.txt', 'a', encoding='utf-8') as f:
    #         f.write(item)

    def save_mongodb(self, item, spider):
        self.coll.insert(dict(item))

    def process_item(self, item, spider):
        self.save_mongodb(item, spider)
        return item

