# python
import logging

logger = logging.getLogger("game_logger")
logger.setLevel(logging.INFO)

# Truncate `game.log` at startup by opening it in write mode
file_handler = logging.FileHandler("game.log", mode="w", encoding="utf-8")
file_handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))

# Avoid adding duplicate handlers if this module is re-imported
if not logger.handlers:
    logger.addHandler(file_handler)
