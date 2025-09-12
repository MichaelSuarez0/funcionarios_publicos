from pathlib import Path
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from _funcionarios_spider import FuncionariosSpider
import _settings as pkg_settings


def main_scrapy(output_path: str | Path = "salida.csv", concurrent_requests: int = 50):
    """
    Ejecuta la spider `FuncionariosPublicos` y guarda los items exportados en un archivo CSV
    en la ruta señalada en output_path.

    Parameters
    ----------
    output_path : str or pathlib.Path, default "salida.csv"
        Ruta del archivo de salida. Se exporta en formato **CSV** con codificación UTF-8 y
        delimitador `;`. Si el archivo existe, se sobreescribe.
    concurrent_requests : int, default 50
        Número máximo de solicitudes concurrentes que usará Scrapy (`CONCURRENT_REQUESTS`).
        Valores altos aceleran el scraping pero pueden incrementar timeouts/ban y carga del sitio.

    Returns
    -------
    None
        La función es bloqueante y retorna solo cuando el proceso de crawling finaliza o se cancela.

    Examples
    --------
    Ejecutar con la configuración por defecto (50 requests concurrentes) y salida en `salida.csv`:

    >>> main_scrapy()

    Cambiar la ruta de salida y usar menor concurrencia:

    >>> main_scrapy(output_path="funcionarios_ceplan.csv", concurrent_requests=32)

    Notes
    --------
    - Habilita logging a nivel `INFO`,
    - El archivo de salida se **sobrescribe** sin confirmación.
    - Un nivel alto de concurrencia puede provocar errores en el sitio de destino.
    """
    # cargar settings del paquete
    s = get_project_settings()
    for k, v in pkg_settings.__dict__.items():
        if k.isupper():
            s.set(k, v, priority="project")
    
    # Configuración del log (por defecto en INFO)
    s.set("LOG_ENABLED", True, priority="project")
    s.set("LOG_LEVEL", "INFO", priority="project")  # opciones: DEBUG, INFO, WARNING, ERROR, CRITICAL

    # FEEDS para exportar sin pipeline de DB
    s.set(
        "FEEDS",
        {
            str(output_path): {
                "format": "csv",
                "encoding": "utf-8-sig",
                "overwrite": True,
                "delimiter": ";"
            }
        },
        priority="project",
    )
    s.set("CONCURRENT_REQUESTS", concurrent_requests)

    process = CrawlerProcess(settings=s)
    process.crawl(FuncionariosSpider)
    process.start()
