import logging
import sys

def setup_logging():
    # Configuración básica
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        handlers=[
            logging.StreamHandler(sys.stdout) # Esto permite que Vercel capture los logs
        ]
    )

logger = logging.getLogger("portafolio_api")