from functools import wraps
import timeit


def medir_tiempo(func):
    """
    Decorador para medir el tiempo de las funciones
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        inicio = timeit.default_timer()
        resultado = func(*args, **kwargs)
        fin = timeit.default_timer()
        tiempo_transcurrido = fin - inicio

        horas = int(tiempo_transcurrido // 3600)
        minutos = int((tiempo_transcurrido % 3600) // 60)
        segundos = tiempo_transcurrido % 60

        horas_name = "horas" if horas != 1 else "hora"
        minutos_name = "minutos" if minutos != 1 else "minuto"

        # Registrar tiempo de ejecución
        #print(f"La función '{func.__name__}' tardó {horas} {horas_name}, {minutos} {minutos_name} y {segundos:.2f} segundos en ejecutarse.") 
        print(f"La función '{func.__name__}' tardó {horas} {horas_name} y {minutos} {minutos_name} en ejecutarse.") 

        return resultado
    return wrapper

# @medir_tiempo
# def prueba():
#     for _ in range(600_000_000_0):
#         pass

# prueba()