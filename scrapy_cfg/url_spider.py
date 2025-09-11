# src/vigilancia_prospectiva/spiders/headings_spider.py
import scrapy
from scrapy.spiders import Spider
from scrapy.core.scraper import Response


class URLSpider(Spider):
    name = "headings"
    allowed_domains = ["gob.pe"]
    start_urls = ["https://www.gob.pe/funcionariospublicos?sheet=1"]
    total_links = 0
    total_pages = 0

    def parse(self, response: Response):
        # Extraer número aproximado de funcionarios según el número de páginas
        self.total_pages = response.css('a[aria-label*="Última página"]::text').get()
        self.total_funcionarios = int(self.total_pages)*40
        
        # Extraer todos los URLs de los funcionarios
        links = response.css("a.link-transition.flex.hover\\:no-underline.justify-between.items-center.mt-8::attr(href)").getall()
        page_links = 0

        for href in links:
            if "/institucion/" in href and "/funcionarios/" in href:
                page_links += 1
                yield response.follow(href, callback=self.parse_item)

        # Si encontramos funcionarios en esta página, probamos la siguiente
        if page_links > 0:
            current_sheet = int(response.url.split("sheet=")[-1])
            next_sheet = current_sheet + 1
            next_url = f"https://www.gob.pe/funcionariospublicos?sheet={next_sheet}"
            self.logger.info(f"➡️  Siguiente página: {next_sheet}")
            yield scrapy.Request(next_url, callback=self.parse)

    def parse_item(self, response: Response):
        url = response.url
        self.total_links += 1
        self.logger.info(f"{self.total_links}/{self.total_funcionarios} -> {url}")
        yield {"url": url}

        
