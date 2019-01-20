import json
import scrapy


class SephoraSpider(scrapy.Spider):
    name = 'sephora'
    allowed_domains = ['sephora.com']
    root_url = "https://www.sephora.com"
    all_item_url_suffix = "/all"
    start_urls = ['https://www.sephora.com/brands-list']

    # Class name may vary
    brand_class = "css-d84rnc "
    brand_see_all_class = "css-oftl0u "
    brand_see_each_class = "css-ix8km1"

    def __init__(self):
        self.declare_xpath()

    def declare_xpath(self):
        self.getAllListXpath = "//a[@class='" + self.brand_class + "']"
        self.getOneBrandAllItemXpath = "//a[@class='" + self.brand_see_all_class + "']"
        self.getOneBrandEachItemXpath = "//a[@class='" + self.brand_see_each_class + "']"


    def parse(self, response):
        for article in response.xpath(self.getAllListXpath):
            brand_url = article.xpath("@href").extract()[0]
            # Testing for only one brand
            # if brand_url != "/brand/estee-lauder":
            #     continue
            request = scrapy.Request(self.root_url + brand_url + self.all_item_url_suffix, callback=self.parse_one_brand_each_item);
            request.meta['brand_url'] = brand_url
            request.meta['brand_name'] = article.xpath("text()").extract()[0]
            yield request

    # def parse_one_brand(self, response):
    #     brand_url = response.meta['brand_url']
    #     brand_name = response.meta['brand_name']
    #     brand_all_item_url = response.xpath(self.getOneBrandAllItemXpath)[0].xpath("@href").extract()
    #     yield {
    #         'brand_name': brand_name,
    #         'brand_url': brand_url,
    #         'brand_all_item_url': brand_all_item_url
    #     }

    def parse_one_brand_each_item(self, response):
        brand_url = response.meta['brand_url']
        brand_name = response.meta['brand_name']
        article = response.xpath("/html/body/script")[0]
        if article.xpath("@data-comp").extract()[0] != "PageJSON":
            return
        page_json_list = article.xpath("text()").extract()[0]
        values_outwrap = json.loads(page_json_list)
        for values_inwrap in values_outwrap:
            if values_inwrap["class"] == "CatalogPage":
                values = values_inwrap["props"]["products"]
                for value in values:
                    yield {
                        'brand_name': brand_name,
                        'brand_url': brand_url,
                        'item_url': self.root_url + value["targetUrl"]
                    }
                break

    def parse_one_item(self, response):
        brand_name = response.meta['brand_name']
        item_url = response.meta['item_url']
        yield {
            'brand_name': brand_name,
            'item_url': item_url
        }
