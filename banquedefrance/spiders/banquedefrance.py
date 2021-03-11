import scrapy
from scrapy.loader import ItemLoader
from itemloaders.processors import TakeFirst
from datetime import datetime
from banquedefrance.items import Article


class BanquedefranceSpider(scrapy.Spider):
    name = 'banquedefrance'
    start_urls = ['https://blocnotesdeleco.banque-france.fr/']

    def parse(self, response):
        links = response.xpath('//h2/a/@href').getall()
        yield from response.follow_all(links, self.parse_article)

        next_page = response.xpath('//li[@class="pager-next"]/a/@href').get()
        if next_page:
            yield response.follow(next_page, self.parse)

    def parse_article(self, response):
        if 'pdf' in response.url:
            return

        item = ItemLoader(Article())
        item.default_output_processor = TakeFirst()

        title = response.xpath('//h1/text()').get()
        if title:
            title = title.strip()

        date = response.xpath('//div[@class="blog-published-date"]/text()').get()
        if date:
            date = " ".join(date.strip().split()[2:])

        content = response.xpath('//div[@id="block-system-main"]//*[not(@class="item-list")]//text()').getall()
        content = [text for text in content if text.strip()]
        content = "\n".join(content[9:]).strip()

        item.add_value('title', title)
        item.add_value('date', date)
        item.add_value('link', response.url)
        item.add_value('content', content)

        return item.load_item()
