import scrapy
from scrapy.core.scraper import Response
from dataclasses import dataclass

@dataclass(frozen=True)
class FuncionarioXPaths:
    nombre: str = '//h1[@class="text-2xl leading-8"]/text()'
    institucion: str = '//h2[contains(@class, "text-base")]//a/text()'
    cargo: str = '//h1/following-sibling::div[@class="mt-2"][1]/text()'
    fecha_inicio: str = '//span[@class="ml-1"]/text()'
    correo: str = '//span[contains(text(), "@")]/text()'
    telefono: str = '//a[@aria-label[contains(.,"Llamar al número")]]/text()'
    resolucion: str = '//div[contains(@class, "mt-3 font-bold")]//div/text()[normalize-space()]'
    resumen: str = '//div[@class="leading-6"]//text()'

class FuncionariosSpider(scrapy.Spider):
    name = "directorio"
    allowed_domains = ["gob.pe"]
    start_urls = [
        "https://www.gob.pe/funcionariospublicos",
        "https://www.gob.pe/funcionariospublicos?sheet=1",
    ]

    xpaths = FuncionarioXPaths()

    total_links = 0
    total_pages = 0

    def parse(self, response: Response):
        # Extraer número aproximado de funcionarios según el número de páginas
        self.total_pages = response.css('a[aria-label*="Última página"]::text').get()
        self.total_funcionarios = int(self.total_pages) * 20

        # Extraer todos los URLs de los funcionarios
        links = response.css(
            "a.link-transition.flex.hover\\:no-underline.justify-between.items-center.mt-8::attr(href)"
        ).getall()
        page_links = 0

        for href in links:
            if "/institucion/" in href and "/funcionarios/" in href:
                page_links += 1
                yield response.follow(href, callback=self.parse_item)

        # Si encontramos funcionarios en esta página, probamos la siguiente
        if page_links > 0:
            try:
                current_sheet = int(response.url.split("sheet=")[-1])
            except ValueError:
                return
            next_sheet = current_sheet + 1
            next_url = f"https://www.gob.pe/funcionariospublicos?sheet={next_sheet}"
            self.logger.info(f"➡️  Siguiente página: {next_sheet}")
            yield scrapy.Request(next_url, callback=self.parse)

    def parse_item(self, response: Response):
        url = response.url
        self.total_links += 1
        self.logger.info(f"{self.total_links}/{self.total_funcionarios} -> {url}")

        resumen = response.xpath('//div[@class="leading-6"]//text()').getall()
        # Limpiar espacios, saltos y \xa0
        resumen_limpio = " ".join(
            [t.strip().replace("\xa0", " ") for t in resumen if t.strip()]
        )

        yield {
            "nombre": response.xpath(self.xpaths.nombre).get(),
            "institucion": response.xpath(self.xpaths.institucion).get(),
            "cargo": response.xpath(self.xpaths.cargo).get(),
            "fecha_inicio": response.xpath(self.xpaths.fecha_inicio).get(),
            "correo": response.xpath(self.xpaths.correo).get(),
            "telefono": response.xpath(self.xpaths.telefono).get(),
            "resolucion": response.xpath(self.xpaths.resolucion).get(),
            "url": url,
            "resumen": resumen_limpio
        }
