import logging
from bs4 import BeautifulSoup
import requests
from icecream import ic
import timeit
from functools import wraps
from typing import Callable, Any, TypeVar
from lxml import html
import concurrent.futures
import pandas as pd
import os

script_dir = os.path.abspath(os.path.dirname(__file__))
log_path = os.path.join(script_dir, 'funcionarios.log')

# Configuración básica del logging
logging.basicConfig(
    level=logging.INFO,  # Nivel de registro (INFO, DEBUG, WARNING, ERROR, CRITICAL)
    format='%(asctime)s - %(levelname)s - %(message)s',  
    handlers=[
    logging.FileHandler(log_path, mode='a', encoding='utf-8'),  # Archivo en UTF-8
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


# Crear decorador para medir el tiempo
def medir_tiempo(func: F) -> F:
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


# Definir funciones subordinadas
def obtener_urls_funcionarios(paginas: int)-> list:
    urls = []

    for pagina in range(1, paginas + 1):  # Recorre desde la página 1 hasta n_paginas
        url = f"https://www.gob.pe/funcionariospublicos?sheet={pagina}"
        response = requests.get(url, headers=headers)
        
        # Verificar si la solicitud fue exitosa
        if response.status_code != 200:
            logging.warning(f"Error al acceder a la página {pagina}. Código de estado: {response.status_code}")
            continue
        
        soup = BeautifulSoup(response.content, "html.parser")
        enlaces_funcionarios = soup.find_all("a", attrs={"class": "link-transition flex hover:no-underline justify-between items-center mt-8"})
        
        for enlace_funcionario in enlaces_funcionarios:
            href = enlace_funcionario.get("href")
            if href:
                url_completa = base_url + href
                urls.append(url_completa)
    
    return urls


# TODO: Formatear adecuadamente la fecha (en datetime)
def obtener_datos_funcionario(url: str) -> dict:
    """
    Extrae la información de un funcionario a partir de su URL usando XPath.
    """
    try:
        # Obtener el contenido HTML de la página
        response = requests.get(url)
        response.raise_for_status()  # Lanza una excepción si la solicitud no fue exitosa
        tree = html.fromstring(response.content.decode('utf-8', errors='replace'))

        datos = {}

        # XPaths para extraer la información
        xpaths = {
            "institucion": '//h1[contains(@class, "text-base")]//a/text()',
            "nombre": '//h2[@class="md:text-4xl mt-3"]/text()',
            "cargo": '//div[@class="mt-4"]/text()',
            "fecha_inicio": '//span[@class="ml-1"]/text()',
            "correo": '//a[contains(@class, "track-ga-click")]//span/text()',
            "telefono": '//a[contains(@class, "icon-text") and starts-with(@href, "tel:")]/text()',
            "resolucion": '//div[contains(@class, "mt-3 font-bold")]//div/text()[normalize-space()]',
            "resumen": '//div[@id="biography-showhide"]//text()',
        }

        # Extraer los datos usando los XPaths
        for clave, xpath in xpaths.items():
            resultado: list = tree.xpath(xpath)
            if resultado:
                if clave in ["correo", "telefono"]:
                    datos[clave] = resultado[0].strip()
                else:
                    datos[clave] = " ".join(resultado).strip()
            else:
                datos[clave] = None

        return datos

    except requests.RequestException as e:
        logging.error(f"Error al acceder a la URL {url}: {e}")
        return {}
    

# TODO: Formatear adecuadamente el excel exportado
def guardar_en_excel(datos: list[dict], nombre_archivo: str = "funcionarios_publicos.xlsx"):
    df = pd.DataFrame(datos)
    ruta = os.path.join(script_dir, nombre_archivo)
    df.to_excel(ruta, index=False, engine="openpyxl")
    logging.info(f"Datos guardados en {nombre_archivo}")


# Definir función principal ----------------------------------------------
@medir_tiempo
def main_sync(paginas: int = 3) -> list[dict] :
    datos_funcionarios: list = [] # Lista de diccionarios final
    urls_funcionarios: list = obtener_urls_funcionarios(paginas=paginas)  

    for url_funcionario in urls_funcionarios:
        dato_funcionario = obtener_datos_funcionario(url_funcionario)
        datos_funcionarios.append(dato_funcionario)

    logging.info(f'Se han obtenido datos de {len(datos_funcionarios)} funcionarios')    
    return datos_funcionarios


@medir_tiempo
def main_threads(paginas: int = 3, workers: int = 10) -> list[dict] :
    datos_funcionarios: list = [] # Lista de diccionarios final
    urls_funcionarios: list = obtener_urls_funcionarios(paginas=paginas)  

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
            datos_funcionarios.append(dato_funcionario)

    logging.info(f'Se han obtenido datos de {len(datos_funcionarios)} funcionarios')    
    return datos_funcionarios


# Ejemplo de uso
if __name__ == "__main__":
    #datos = main_sync()
    datos = main_threads(paginas=1879, workers=20)  # Máximo de páginas: 1879
    guardar_en_excel(datos)
    