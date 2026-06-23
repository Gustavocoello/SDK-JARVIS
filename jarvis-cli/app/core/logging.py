"""
app/core/logging_config.py — Silencia todo el ruido de librerías de terceros,
dejando solo lo que vos loggeás explícitamente con logger.info/error propio.
"""

import logging


def setup_logging():
    # Nivel base: solo WARNING o peor se muestra en general
    logging.basicConfig(level=logging.WARNING)
    loggers_silenciosos = [
        "markdown_it",
        "urllib3",
        "urllib3.connectionpool",
        "asyncio",
        "httpx",
        "httpcore",
        "langchain_core",
        "langgraph",
        "watchfiles",
    ]
    for nombre in loggers_silenciosos:
        logging.getLogger(nombre).setLevel(logging.ERROR)
        

def silenciar_logs_para_cli():
    """
    logging.disable() es un interruptor GLOBAL: ignora cualquier log
    de nivel <= el que le pases, sin importar qué logger lo emitió ni
    cómo esté configurado (pisa hasta el dictConfig del backend).
    """
    logging.disable(logging.WARNING)
    #    Esto bloquea DEBUG, INFO y WARNING de TODOS los loggers
    #    (backend.engine, urllib3, markdown_it, asyncio, etc.)
    #    pero deja pasar ERROR y CRITICAL — si el agente falla feo,
    #    igual te vas a enterar