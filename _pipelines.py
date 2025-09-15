from datetime import datetime

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


class FechaPipeline:
    def process_item(self, item, spider):
        # Quitar espacios en blanco
        for k, v in item.items():
            if isinstance(v, str):
                item[k] = v.strip()

        # Convertir a fecha
        if "fecha_inicio" in item and item["fecha_inicio"]:
            item["fecha_inicio"] = convertir_fecha(item["fecha_inicio"])
        return item