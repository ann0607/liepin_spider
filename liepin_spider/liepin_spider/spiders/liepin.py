# -*- coding: utf-8 -*-
import re
from urllib.parse import quote

import scrapy

from liepin_spider.items import LiepinSpiderItem


class LiepinSpider(scrapy.Spider):
    name = "liepin"
    allowed_domains = ["liepin.com"]
    start_urls = ['http://www.liepin.com/']

    def parse(self, response):
        keywords = self.settings['KEYWORDS']
        for keyword in keywords:
            url = f'https://www.liepin.com/zhaopin/?sfrom=click-pc_homepage-centre_searchbox-search_new&d_sfrom=search_fp&key={quote(keyword)}'
            headers = {
                'Referer': 'https://www.liepin.com/'
            }
            yield scrapy.Request(url, headers=headers, callback=self.page_list_urls, meta={'keyword':keyword})

    def page_list_urls(self, response):
        meta = response.meta
        keyword = meta['keyword']
        last_page_url = response.xpath('//div[@class="pagerbar"]/a[@class="last"]/@href').extract_first()
        total_page = int(re.findall(r'&curPage=(\d+)', last_page_url)[0])+1
        for i in range(total_page):
            page_url = f'https://www.liepin.com/zhaopin/?sfrom=click-pc_homepage-centre_searchbox-search_new&d_sfrom=search_fp&key={quote(keyword)}&curPage={i}'
            headers = {
                'Referer': f'https://www.liepin.com/zhaopin/?sfrom=click-pc_homepage-centre_searchbox-search_new&d_sfrom=search_fp&key={quote(keyword)}'
            }
            yield scrapy.Request(page_url, headers=headers, callback=self.job_list_urls, meta=meta)

    def job_list_urls(self, response):
        meta = response.meta
        keyword = meta['keyword']
        job_list = response.xpath('//div[@class="job-info"]/h3[1]/a[1]/@href').extract()
        for j in job_list:
            if 'job' in j:
                job_url = j
            else:
                job_url = 'http://www.liepin.com/' + j
            headers = {
                'Referer': f'https://www.liepin.com/zhaopin/?sfrom=click-pc_homepage-centre_searchbox-search_new&d_sfrom=search_fp&key={quote(keyword)}'
            }
            yield scrapy.Request(job_url, headers=headers, callback=self.job_message, meta=meta)

    def job_message(self, response):
        if response.xpath('//div[@class="title-info"]/h1[1]/@title').extract_first():
            item = LiepinSpiderItem()
            item['job_title'] = response.xpath('//div[@class="title-info"]/h1[1]/@title').extract_first()
            item['company'] = response.xpath('//div[@class="title-info"]/h3[1]/a/text()').extract_first()
            item['experience'] = response.xpath('//div[@class="job-qualifications"]/span[2]/text()').extract_first()
            item['salary'] = response.xpath('//p[@class="job-item-title"]/text()').extract_first().strip()
            item['education'] = response.xpath('//div[@class="job-qualifications"]/span[1]/text()').extract_first()
            item['city'] = response.xpath('//p[@class="basic-infor"]/span[1]/a/text()').extract_first()
            date = response.xpath('//p[@class="basic-infor"]/time[1]/@title').extract_first()
            item['pubdate'] = '{}-{}-{}'.format(date[:4], date[5:7], date[8:10])
            des = response.xpath('//div[@class="job-item main-message job-description"]/div[1]/text()').extract()
            item['description'] = ''.join(des).strip()
            item['keyword'] = response.meta['keyword']
            yield item

