# main.py
import sys
import os

from PySide6.QtWidgets import QApplication

from main_window import TrelloCushionsWindow
from utils.logging import setup_logging

appname = "Trello Cushions"

if __name__ == "__main__":
    logger = setup_logging()   # initializes AppLogger + returns standard logger

    try:
        logger.info(f"{appname} launched (debug mode: {os.getenv('COZY_DEBUG', '0') == '1'})")
        app = QApplication(sys.argv)
        app.setStyle("Fusion")
        window = TrelloCushionsWindow()
        window.show()
        sys.exit(app.exec())
    except Exception as e:
        logger.critical(f"Startup catastrophically failed", exc_info=True)
        print(f"{appname} has entered the void: {str(e)}", file=sys.stderr)
        sys.exit(1)