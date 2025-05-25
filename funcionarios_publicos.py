import logging
from bs4 import BeautifulSoup
import requests
import timeit
from functools import wraps
from typing import Callable, Any, TypeVar
from lxml import html
import concurrent.futures
import threading
import pandas as pd
from pathlib import Path
from tqdm import tqdm
from datetime import datetime

# ============================================================
#  0. Configuraciones básicas
# ============================================================
SCRIPT_DIR = Path(__file__).parent
LOG_PATH = SCRIPT_DIR / 'log' / 'directorio_funcionarios.log'
LOG_PATH.parent.mkdir(parents=True, exist_ok=True)

# Configuración básica del logging
logging.basicConfig(
    level=logging.INFO,  # Nivel de registro (INFO, DEBUG, WARNING, ERROR, CRITICAL)
    format='%(asctime)s - %(levelname)s - %(message)s',  
    handlers=[
    logging.FileHandler(LOG_PATH, mode='a', encoding='utf-8'),  # Archivo en UTF-8
    logging.StreamHandler()  # También mostrar logs en la consola
    ]
)

# Definir un tipo genérico para el retorno de la función
F = TypeVar("F", bound=Callable[..., Any])

# Variables
base_url = "https://www.gob.pe"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

# ============================================================
#  1. Definir funciones subordinadas
# ============================================================

def convertir_fecha(fecha_texto: str):
    """Convierte una fecha en formato 'dd mmm yyyy' a datetime en formato estándar."""
    meses = {
        "ene": "Jan", "feb": "Feb", "mar": "Mar", "abr": "Apr",
        "may": "May", "jun": "Jun", "jul": "Jul", "ago": "Aug",
        "set": "Sep", "sep": "Sep", "oct": "Oct", "nov": "Nov", "dic": "Dec"
    }
    # Reemplazar el nombre del mes en español por su equivalente en inglés
    for mes_es, mes_en in meses.items():
        if mes_es in fecha_texto:
            fecha_texto = fecha_texto.replace(mes_es, mes_en)
            break

    try:
        return datetime.strptime(fecha_texto, "%d %b %Y").strftime("%Y-%m-%d")
    except ValueError:
        return None 


def medir_tiempo(func: F) -> F:
    """
    Decorador para medir el tiempo de las funciones
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        inicio = timeit.default_timer()
        resultado = func(*args, **kwargs)
        fin = timeit.default_timer()
        tiempo_transcurrido = fin - inicio
        minutos = tiempo_transcurrido // 60 if tiempo_transcurrido > 60 else 0
        segundos = tiempo_transcurrido % 60

        # Registrar tiempo de ejecución
        logging.info(f"La función '{func.__name__}' tardó {minutos} minutos y {segundos:.2f} segundos en ejecutarse.")

        # Registrar 'workers' si la función tiene dicho parámetro
        if 'workers' in kwargs:
            logging.info(f"Número de workers utilizados: {kwargs['workers']}")
        else:
            # Si no está en kwargs, buscar en args
            import inspect
            signature = inspect.signature(func)
            parameters = signature.parameters

            if 'workers' in parameters:
                workers_index = list(parameters.keys()).index('workers')
                if workers_index < len(args):
                    logging.info(f"Número de workers utilizados: {args[workers_index]}")

        return resultado
    return wrapper


def obtener_urls_pagina(url_pagina: str)-> list:
    """
    Extraer las URLs de los funcionarios de una sola página.
    """
    urls = []
    try:
        response = requests.get(url_pagina, headers=headers)
        response.raise_for_status()  # Raise an exception for bad status codes
    except requests.RequestException as e:
        logging.warning(f"Error al acceder a la página {url_pagina}: {e}")
        return urls  # Return an empty list if the request fails
    
    # Verificar si la solicitud fue exitosa
    if response.status_code != 200:
        logging.warning(f"Error al acceder a la página {url_pagina}. Código de estado: {response.status_code}")
    
    soup = BeautifulSoup(response.content, "html.parser")
    enlaces_funcionarios = soup.find_all("a", attrs={"class": "link-transition flex hover:no-underline justify-between items-center mt-8"})
    
    for enlace_funcionario in enlaces_funcionarios:
        href = enlace_funcionario.get("href")
        if href:
            url_completa = base_url + href
            urls.append(url_completa)

    return urls


def obtener_datos_funcionario(url: str) -> dict:
    """
    Extraer la información de un funcionario a partir de su URL usando XPath.
    """
    try:
        # Obtener el contenido HTML de la página
        response = requests.get(url)
        response.raise_for_status()  # Lanza una excepción si la solicitud no fue exitosa
        tree = html.fromstring(response.content.decode('utf-8', errors='replace'))

        datos = {}

        # XPaths para extraer la información
        xpaths = {
            "nombre": '//h1[@class="text-2xl leading-8"]/text()',
            "institucion": '//h2[contains(@class, "text-base")]//a/text()',
            "cargo": '//h1/following-sibling::div[@class="mt-2"][1]/text()',
            "fecha_inicio": '//span[@class="ml-1"]/text()',
            "correo": '//span[contains(text(), "@")]/text()',
            "telefono": '//a[contains(@class, "icon-text") and starts-with(@href, "tel:")]/text()',
            "resolucion": '//div[contains(@class, "mt-3 font-bold")]//div/text()[normalize-space()]',
            "resumen": '//div[@id="biography-showhide"]//text()',
        }

        # Extraer los datos usando los XPaths
        for clave, xpath in xpaths.items():
            resultado: list = tree.xpath(xpath)
            if resultado:
                if clave == "telefono":
                    datos[clave] = resultado[0].strip()
                elif clave == "fecha_inicio":
                    datos[clave] = convertir_fecha(resultado[0].strip())  # Convertir fecha
                else:
                    datos[clave] = " ".join(resultado).strip()
            else:
                datos[clave] = None

        return datos

    except requests.RequestException as e:
        logging.error(f"Error al acceder a la URL {url}: {e}")
        return {}
    

# TODO: Formatear adecuadamente el excel exportado
def guardar_en_excel(datos: list[dict]):
    date = datetime.now()
    date_formatted = date.strftime("%Y%m%d")
    df = pd.DataFrame(datos)
    nombre_archivo = f"funcionarios_publicos_{date_formatted}.xlsx"
    ruta = SCRIPT_DIR, "funcionarios", nombre_archivo

    df.to_excel(ruta, index=False, engine="openpyxl")
    logging.info(f"Datos guardados en {nombre_archivo}")


# ================================================================
#  2. Definir función principal
# ================================================================
# TODO: Adaptar para el nuevo obtener_urls_pagina
@medir_tiempo
def main_sync(paginas: int = 3) -> list[dict] :
    datos_funcionarios: list = [] # Lista de diccionarios final
    urls_funcionarios: list = obtener_urls_pagina(paginas=paginas)  

    for url_funcionario in urls_funcionarios:
        dato_funcionario = obtener_datos_funcionario(url_funcionario)
        datos_funcionarios.append(dato_funcionario)

    logging.info(f'Se han obtenido datos de {len(datos_funcionarios)} funcionarios')    
    return datos_funcionarios


# =================================================================
#  3. Función principal optimizada con Threading
# =================================================================
@medir_tiempo
def main_threads(paginas: int | None = None, workers: int = 9) -> list[dict]:
    datos_funcionarios: list[dict] = [] # Lista de diccionarios final
    urls_funcionarios: list[str] = [] # Lista de urls de los funcionarios
    lock = threading.Lock() # Lock to prevent race conditions when appending to list

    logging.info("=" * 90) 

    if not paginas:
        url_inicial = "https://www.gob.pe/funcionariospublicos"
        initial_page = requests.get(url_inicial, headers=headers)
        soup = BeautifulSoup(initial_page.content, "html.parser")
        paginas = int(soup.find("span", attrs={"class": "last"}).get_text())
    
    logging.info(f"Se obtendrán datos de aproximadamente {paginas*20} funcionarios")

    # First progress bar
    with tqdm(total = paginas, desc= "Obteniendo URLS", unit = "pages") as pbar_pages:
        with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as executor:
            futures = []
            for pagina in range(1, paginas + 1):  # Recorre desde la página 1 hasta n_paginas
                url_pagina = f"https://www.gob.pe/funcionariospublicos?sheet={pagina}"
                future = executor.submit(obtener_urls_pagina, url_pagina)
                futures.append(future)
            # Recolectar resultados a medida que se completa
            for future in concurrent.futures.as_completed(futures):
                lista_urls_pagina = future.result()
                with lock:
                    urls_funcionarios.extend(lista_urls_pagina)
                pbar_pages.update(1)
    
    total_urls = len(urls_funcionarios) 

    # Second progress bar
    with tqdm(total = total_urls, desc= "Obteniendo funcionarios", unit = "URLs") as pbar_data:
        # Usar ThreadPoolExecutor para paralelizar las solicitudes HTTP
        with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as executor:
            # Mapear las URLs a futures
            futures = []
            for url in urls_funcionarios:
                future = executor.submit(obtener_datos_funcionario, url)
                futures.append(future)

            # Recolectar resultados a medida que se completan
            for future in concurrent.futures.as_completed(futures):
                dato_funcionario = future.result()
                with lock:
                    datos_funcionarios.append(dato_funcionario)
                pbar_data.update(1)

    logging.info(f'Se han obtenido datos de {len(datos_funcionarios)} funcionarios')    
    return datos_funcionarios


# =====================================================================
#  4. Correr el script
# =====================================================================
#  Tiempo estimado para 1940 paginas, 9 workers: ~88 min
#  Número de páginas recomendado para probar: 40 (~2min)
#  NOTA: No utilizar más de 10 workers para evitar data races
# =====================================================================

# TODO: encontrar número de páginas dinámicamente
if __name__ == "__main__":
    datos = main_threads(workers=9) 
    guardar_en_excel(datos)