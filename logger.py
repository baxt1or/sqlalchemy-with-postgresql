import logging
from colorama import Fore, Style, init
from sqlalchemy import create_engine

# Initialize colorama
init(autoreset=True)

# Custom formatter for colored logging
class ColorFormatter(logging.Formatter):
    LEVEL_COLORS = {
        logging.DEBUG: Fore.CYAN,
        logging.INFO: Fore.GREEN,
        logging.WARNING: Fore.YELLOW,
        logging.ERROR: Fore.RED,
        logging.CRITICAL: Fore.RED + Style.BRIGHT
    }

    def format(self, record):
        log_color = self.LEVEL_COLORS.get(record.levelno, Fore.WHITE)
        log_message = super().format(record)
        return f"{log_color}{log_message}{Style.RESET_ALL}"

# Set up the logger
logger = logging.getLogger("db_logger")
logger.setLevel(logging.DEBUG)

console_handler = logging.StreamHandler()
formatter = ColorFormatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)