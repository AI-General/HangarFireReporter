import logging
from colorlog import ColoredFormatter

logging.getLogger("httpx").setLevel(logging.WARNING)

def get_color_logger(name: str = "color_logger") -> logging.Logger:
    logger = logging.getLogger(name)
    if logger.hasHandlers():
        logger.handlers.clear()
    
    # Disable the root logger handler to avoid duplicate logs
    logging.getLogger().handlers.clear()
    
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    formatter = ColoredFormatter(
        "%(log_color)s[%(levelname)s]%(reset)s %(message_log_color)s%(message)s",
        log_colors={
            'DEBUG':    'cyan',
            'INFO':     'green',
            'WARNING':  'yellow',
            'ERROR':    'red',
            'CRITICAL': 'bold_red',
        },
        secondary_log_colors={
            'message': {
                'DEBUG':    'white',
                'INFO':     'bold_green',
                'WARNING':  'bold_yellow',
                'ERROR':    'bold_red',
                'CRITICAL': 'bold_red',
            }
        },
        style='%'
    )
    ch.setFormatter(formatter)
    logger.addHandler(ch)
    logger.setLevel(logging.DEBUG)
    return logger 