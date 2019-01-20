import json
import scrapy


class SephoraSpider(scrapy.Spider):
    name = 'sephora'
    allowed_domains = ['sephora.com']
    root_url = "https://www.sephora.com"
    all_item_url_suffix = "/all?pageSize=300"
    start_urls = ['https://www.sephora.com/brands-list']

    # Class name may vary
    brand_class = "css-d84rnc "

    def __init__(self):
        self.declare_xpath()

    def declare_xpath(self):
        self.getAllListXpath = "//a[@class='" + self.brand_class + "']"


    def parse(self, response):
        for article in response.xpath(self.getAllListXpath):
            brand_url = article.xpath("@href").extract()[0]
            # Testing for only one brand
            if brand_url != "/brand/la-mer":
                continue
            request = scrapy.Request(self.root_url + brand_url + self.all_item_url_suffix, callback=self.parse_one_brand_each_item);
            request.meta['brand_url'] = brand_url
            request.meta['brand_name'] = article.xpath("text()").extract()[0]
            yield request

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
                    item_url = self.root_url + value["targetUrl"]
                    request = scrapy.Request(item_url, callback=self.parse_one_item)
                    request.meta['brand_url'] = brand_url
                    request.meta['brand_name'] = brand_name
                    request.meta['item_url'] = item_url
                    yield request
                break

    # Information required:
    # brand_name
    # product name (use displayName?)
    # category 1/2/3
    # item_url
    # image_url
    # # of reviews
    # # of likes
    # Details
    # Ingredients
    # 10 reviews
    def parse_one_item(self, response):
        article = response.xpath("/html/body/script")[0]
        if article.xpath("@data-comp").extract()[0] != "PageJSON":
            return
        page_json_list = article.xpath("text()").extract()[0]
        values_outwrap = json.loads(page_json_list)
        for values_inwrap in values_outwrap:
            if values_inwrap["class"] == "RegularProductTop":
                value = values_inwrap["props"]
                if value["currentProduct"]["displayName"] != "The Moisturizing Soft Cream" and value["currentProduct"]["displayName"] != "The Treatment Lotion":
                    continue
                yield {
                    'brand_name': value["currentProduct"]["brand"]["displayName"],
                    'product_name': value["currentProduct"]["displayName"],
                    'category_1': value["currentProduct"]["parentCategory"]["parentCategory"]["parentCategory"]["displayName"],
                    'category_2': value["currentProduct"]["parentCategory"]["parentCategory"]["displayName"],
                    'category_3': value["currentProduct"]["parentCategory"]["displayName"],
                    'item_url': self.root_url + value["currentProduct"]["currentSku"]["targetUrl"],
                    'image_url': self.root_url + value["currentProduct"]["currentSku"]["skuImages"]["image450"],
                    'reviews': value["currentProduct"]["reviews"],
                    'rating': value["currentProduct"]["rating"],
                    'loves': value["currentProduct"]["lovesCount"],
                    'Details': value["currentProduct"]["longDescription"],
                    'Ingredients': value["currentProduct"]["currentSku"]["ingredientDesc"],
                    'review_contents': ""
                }
