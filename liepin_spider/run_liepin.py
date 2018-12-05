from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

from liepin_spider.spiders.liepin import LiepinSpider

settings = get_project_settings()
process = CrawlerProcess(settings=settings)

process.crawl(LiepinSpider)

process.start()