from pathlib import Path
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from .url_spider import URLSpider
from . import settings as pkg_settings


def scrapear_urls(output_path: str | Path = "salida.jsonl"):
    """
    Ejecuta la spider HeadingsSpider para extraer contenido de URLs y guarda los resultados.
    
    Esta función configura y ejecuta un crawler de Scrapy para extraer títulos H1 y párrafos
    de contenido de una lista de URLs proporcionadas. Los datos extraídos se guardan en 
    formato JSON con estructura anidada por URL.
    
    Parameters
    ----------
    urls : str, list, or tuple
        URLs a procesar. Puede ser:
        - str: Lista de URLs separadas por comas, o ruta a archivo .txt con URLs
        - list/tuple: Lista de URLs como strings
    output_path : str or Path, optional
        Ruta del archivo donde guardar los resultados extraídos.
        Por defecto es "salida.jsonl"
        
    Returns
    -------
    None
        La función no retorna valores, pero genera un archivo JSON con los datos extraídos.
        
    Notes
    -----
    El archivo de salida tendrá la siguiente estructura por cada URL procesada:
    
    .. code-block:: json
    
        {
            "url": {
                "status": 200,
                "h1": ["Título principal"],
                "paragraphs": ["Párrafo con más de 100 caracteres..."]
            }
        }
        
    La función utiliza las siguientes configuraciones de Scrapy:
    - Carga settings del paquete pkg_settings
    - Configura FEEDS para exportar directamente a JSON
    - Usa formato JSON con encoding UTF-8 e indentación de 4 espacios
    - Sobrescribe el archivo de salida si existe
    
    Examples
    --------
    Procesar URLs desde lista:
    
    >>> urls = ["https://example1.com", "https://example2.com"]
    >>> scrapear_urls(urls, "resultados.json")
    
    Procesar URLs desde string separado por comas:
    
    >>> urls_str = "https://example1.com,https://example2.com"
    >>> scrapear_urls(urls_str, "noticias.json")
    
    Procesar URLs desde archivo de texto:
    
    >>> scrapear_urls("urls_lista.txt", "contenido_extraido.json")
    
    Warnings
    --------
    - La función es bloqueante y no retorna hasta completar el crawling
    - Solo extrae párrafos con más de 100 caracteres
    - Sobrescribe el archivo de salida sin confirmación
    - Requiere que estén disponibles las dependencias: scrapy, w3lib
    """
    s = get_project_settings()
    # cargar settings del paquete (sin necesidad de scrapy.cfg)
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
                "format": "jsonlines",
                "encoding": "utf-8",
                "indent": 4,
                "overwrite": True,
            }
        },
        priority="project",
    )

    process = CrawlerProcess(settings=s)
    process.crawl(URLSpider)
    process.start()  # bloquea hasta terminar
