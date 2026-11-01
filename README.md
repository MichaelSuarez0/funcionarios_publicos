<div align="center">

# 🏛️ Peru Public Officials Scraper (`funcionarios_publicos`)

*Extractor automatizado de alto rendimiento para extraer datos de más de **40,000 funcionarios públicos peruanos** del [Directorio Nacional de Funcionarios Públicos](https://www.gob.pe/funcionariospublicos)*

[![Python Version](https://img.shields.io/badge/python-3.11%2B-blue.svg)](https://www.python.org/)
[![Scrapy](https://img.shields.io/badge/Scrapy-2.19%2B-orange.svg)](https://scrapy.org/)
[![Package Manager](https://img.shields.io/badge/uv-managed-purple.svg)](https://github.com/astral-sh/uv)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

</div>

## 🚀 Sobre el Proyecto

Este proyecto es un scraper desarrollado en **Python** y **Scrapy** para extraer de forma automatizada y estructurada la información de más de 40,000 funcionarios públicos del Perú, completando el proceso en **~2 horas**.

Además, cuenta con una automatización en **GitHub Actions** configurada para ejecutarse **todos los domingos**, guardando un nuevo archivo CSV con su respectiva fecha en cada corrida, para preservar un registro histórico de los datos a lo largo del tiempo.

## 🛢️ ¿Buscas solo los datos?

**¡No necesitas ejecutar el scraper!** Puedes acceder directamente a la carpeta [**`data`**](./data), donde encontrarás los datasets limpios en formato **CSV** (delimitados por punto y coma `;`), ordenados y fechados por cada ejecución automática para facilitar tus análisis, investigaciones o auditorías.

## 🛠️ Stack Tecnológico

- **Lenguaje:** [Python 3.11+](https://www.python.org/)
- **Web Scraping:** [Scrapy](https://scrapy.org/)
- **Gestión de Entorno y Paquetes:** [uv](https://github.com/astral-sh/uv)
- **Automatización:** [GitHub Actions](https://github.com/features/actions)

## 💻 Ejecución Local (para desarrolladores)

Si deseas ejecutar el scraper por tu cuenta en lugar de usar los datos pregenerados, sigue estos pasos:

### ⚙️ Requisitos Previos

Asegúrate de tener instalado [uv](https://github.com/astral-sh/uv) en tu sistema:
- **Python** >= 3.11

### 📥 Instalación y Uso

1. **Clonar el repositorio:**
   ```bash
   git clone https://github.com/MichaelSuarez0/funcionarios_publicos.git
   cd funcionarios_publicos
   ```

2. **Instalar dependencias con `uv`:**
   ```bash
   uv sync
   ```

3. **Ejecutar el Scraper:**
   ```bash
   uv run main.py
   ```
