# -*- coding: utf-8 -*-
import scrapy
from copy import deepcopy
import json
import urllib.parse


class JdSpider(scrapy.Spider):
    name = 'jd'
    allowed_domains = ['jd.com']
    start_urls = ['https://book.jd.com/booksort.html']

    def parse(self, response):
        dt_list = response.xpath("//div[@class='mc']/dl/dt")  # 大分类列表
        for dt in dt_list:
            item = {}
            item['n_cate'] = dt.xpath("./a/text()").extract_first()
            em_list = dt.xpath("./following-sibling::dd[1]/em")  # 小分类列表
            for em in em_list:
                item["s_href"] = em.xpath("./a/@href").extract_first()
                item["s_cate"] = em.xpath("./a/text()").extract_first()
                if item["s_href"] is not None:
                    item["s_href"] = "https:" + item["s_href"]
                    yield scrapy.Request(
                        item["s_href"],
                        callback=self.parse_book_list,
                        meta={"item": item}
                    )

    def parse_book_list(self, response):  # 解析列表页
        item = response.meta["item"]
        li_list = response.xpath("//div[@id='plist']/ul/li")
        for li in li_list:
            item["book_img"] = li.xpath(".//div[@class='p-img']//img/@src").extract_first()
            item["book_name"] = li.xpath(".//div[@class='p-name']/a/em/text()").extract_first().strip()
            item["book_author"] = li.xpath(".//span[@class='author_type_1']/a/text()").extract_first()
            item["book_press"] = li.xpath(".//span[@class='p-bi-store']/a/@title").extract_first()
            item["book_publish_date"] = li.xpath(".//span[@class='p-bi-date']/text()").extract_first().strip()
            # item["book_sku"] = li.xpath("./div/@data-sku").extract_first()
            # price_url = "https://p.3.cn/prices/mgets?skuIds=J_{param}".format(param=item["book_sku"]),
            # print(1, type(item["book_sku"]), item["book_sku"], type(price_url), price_url, 2)
            # yield scrapy.Request(
            #     price_url,
            #     callback=self.parse_book_price,
            #     meta = {"item": deepcopy(item)}
            # )
            print(item)

        # 列表页翻页
        next_url = response.xpath("//a[@class='pn-next']/@href").extract_first()
        if next_url is not None:
            next_url = urllib.parse.urljoin(response.url, next_url)
            yield scrapy.Request(
                next_url,
                callback=self.parse_book_list,
                meta={"item": item}
            )

    def parse_book_price(self, response):
        print('lalala')
        item = response.meta["item"]
        item["book_price"] = json.loads(response.body.decode())[0].get("op")
        print(item)

