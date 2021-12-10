import scrapy
from scrapy import Request
from scrapy.loader import ItemLoader
from property import Property
import re
class LondonrelocationSpider(scrapy.Spider):
    name = 'londonrelocation'
    allowed_domains = ['londonrelocation.com']
    start_urls = ['https://londonrelocation.com/properties-to-rent/']
    allPages = []
    def clean_price(self, price):
        parser = str(price)
        if ('pcm' in parser):
            return int(re.findall('\d+', parser)[0])
        elif('pw' in parser):
            return int(re.findall('\d+', parser)[0])*4    
    def parse(self, response):
        for start_url in self.start_urls:
            yield Request(url=start_url,
                          callback=self.parse_area)

    def parse_area(self, response):
        area_urls = response.xpath('.//div[contains(@class,"area-box-pdh")]//h4/a/@href').extract()
        for area_url in area_urls:
            yield Request(url=area_url,
                          callback=self.parse_area_pages)
          
    def parse_area_pages(self, response):
        page_1_url = response.xpath('//a[contains(@href,"pageset=1")]/@href').extract_first()
        page_2_url = response.xpath('//a[contains(@href,"pageset=2")]/@href').extract_first()
        LondonrelocationSpider.allPages.append(page_1_url)
        
        if (page_2_url is not None):
            LondonrelocationSpider.allPages.append(page_2_url)
        for url in LondonrelocationSpider.allPages:
            yield Request(url = url, callback=self.parse_properties)

    def parse_properties(self, response):
        main_domain = 'https://londonrelocation.com'
        property_urls = response.xpath('.//div[contains(@class, "test-inline")]//h4/a/@href').getall()
        
        for url in property_urls:
            yield Request(url = main_domain+url,
                          callback = self.parse_content)

    
        
    def parse_content(self, response):
        property = ItemLoader(item=Property())
        property.add_value('title', response.xpath('.//div[contains(@class, "content")]//h1/text()').getall())
        property.add_value('price', str(self.clean_price(response.xpath('.//div[contains(@class, "content")]//h3/text()').getall())))
        property.add_value('url', response.request.url) 
        return property.load_item()

    
        # an example for adding a property to the json list:
        # property = ItemLoader(item=Property())
        # property.add_value('title', '2 bedroom flat for rental')
        # property.add_value('price', '1680') # 420 per week
        # property.add_value('url', 'https://londonrelocation.com/properties-to-rent/properties/property-london/534465-2-bed-frognal-hampstead-nw3/')
        # return property.load_item()