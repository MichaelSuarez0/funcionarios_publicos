from dataclasses import dataclass

import scrapy
from scrapy.http import Response
from twisted.internet import reactor


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

    xpaths = FuncionarioXPaths()

    total_links = 0
    total_funcionarios = 0
    max_sheet = None

    MAX_RETRIES = 4
    _pausado = False

    # ---------- manejo de bloqueo ----------
    def bloqueado(self, response: Response) -> bool:
        cuerpo = response.body[:5000]
        return b"Verification Required" in cuerpo or b"too frequent" in cuerpo

    def _reanudar(self):
        self.logger.info("▶ Reanudando crawl")
        self._pausado = False
        self.crawler.engine.unpause()

    def reintentar(self, response: Response):
        req = response.request
        n = req.meta.get("block_retries", 0) + 1
        if n > self.MAX_RETRIES:
            self.logger.error(f"Se rindió tras {self.MAX_RETRIES} intentos: {req.url}")
            return None

        espera = min(60 * 1.5 ** (n - 1), 600)
        self.logger.warning(f"Bloqueo en {req.url} (intento {n}). Pausa de {espera}s")

        # El bloqueo es por IP: se pausa TODO el crawl, no solo esta request
        if not self._pausado:
            self._pausado = True
            self.crawler.engine.pause()
            reactor.callLater(espera, self._reanudar)

        return req.replace(dont_filter=True, meta={**req.meta, "block_retries": n})

    # ---------- inicio ----------
    async def start(self):
        yield scrapy.Request(
            "https://www.gob.pe/funcionariospublicos?sheet=1",
            callback=self.parse_first,
        )

    # ---------- callbacks ----------
    def parse_first(self, response: Response):
        ultima = response.css('a[aria-label*="Última página"]::text').get()
        self.max_sheet = int(ultima.strip())
        self.total_funcionarios = self.max_sheet * 20
        self.logger.info(f"Total de páginas: {self.max_sheet}")

        # Procesa la página 1 y programa las demás
        yield from self.parse(response)
        for n in range(2, self.max_sheet + 1):
            yield scrapy.Request(
                f"https://www.gob.pe/funcionariospublicos?sheet={n}",
                callback=self.parse,
            )

    def parse(self, response: Response):
        links = response.xpath(
            '//a[contains(@href, "/institucion/") and contains(@href, "/funcionarios/")]/@href'
        ).getall()

        # Bloqueo explícito, o página sin links (no debería ocurrir)
        if self.bloqueado(response) or not links:
            r = self.reintentar(response)
            if r:
                yield r
            return

        for href in links:
            yield response.follow(href, callback=self.parse_item)

    def parse_item(self, response: Response):
        nombre = response.xpath(self.xpaths.nombre).get()

        if self.bloqueado(response) or not nombre:
            r = self.reintentar(response)
            if r:
                yield r
            return

        url = response.url
        self.total_links += 1
        self.logger.info(f"{self.total_links}/{self.total_funcionarios} -> {url}")

        resumen = response.xpath(self.xpaths.resumen).getall()
        resumen_limpio = " ".join(
            t.strip().replace("\xa0", " ") for t in resumen if t.strip()
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
