from dataclasses import dataclass

import scrapy
from scrapy.http.response import Response


# TODO: El correo no funciona para todos
@dataclass(frozen=True)
class FuncionarioXPaths:
    nombre: str = '//h1[@class="text-2xl leading-8"]/text()'
    institucion: str = '//h2[contains(@class, "text-base")]//a/text()'
    cargo: str = '//h1/following-sibling::div[@class="mt-2"][1]/text()'
    fecha_inicio: str = '//span[@class="ml-1"]/text()'
    correo: str = '//span[contains(text(), "@")]/text()'
    telefono: str = '//a[@aria-label[contains(.,"Llamar al número")]]/text()'
    resolucion: str = (
        '//div[contains(@class, "mt-3 font-bold")]//div/text()[normalize-space()]'
    )
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
    total_funcionarios = 0

    # ------------------------------------------
    # 1) PRIMERA ENTRADA: redirigir a parse_pages
    # ------------------------------------------
    def parse(self, response: Response):
        return self.parse_pages(response)
        
    # ------------------------------------------
    # 2) MANEJO DE PAGINACIÓN Y EXTRACCIÓN DE URLs
    # ------------------------------------------
    def parse_pages(self, response: Response):
        # Obtener número total de páginas (solo una vez)
        if not self.total_pages:
            last_page = response.css('a[aria-label*="Última página"]::text').get()
            self.total_pages = int(last_page) if last_page else 1
            self.total_funcionarios = self.total_pages * 20

        # Extraer URLs de funcionarios
        links = response.css(
            "a.link-transition.flex.hover\\:no-underline.justify-between.items-center.mt-8::attr(href)"
        ).getall()

        found = 0
        for href in links:
            if "/institucion/" in href and "/funcionarios/" in href:
                found += 1
                yield response.follow(href, callback=self.parse_item)

        # Si se encontraron funcionarios, continuar paginación
        if found > 0:
            # obtener número de página actual
            if "sheet=" in response.url:
                current_page = int(response.url.split("sheet=")[-1])
            else:
                current_page = 0

            next_page = current_page + 1
            next_url = f"https://www.gob.pe/funcionariospublicos?sheet={next_page}"

            self.logger.info(f"➡️  Siguiente página: {next_page}")
            yield scrapy.Request(next_url, callback=self.parse_pages)
            

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
            "resumen": resumen_limpio,
        }
