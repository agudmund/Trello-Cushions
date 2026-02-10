# main.py
import sys

from PySide6.QtWidgets import QApplication

from main_window import TrelloCushionsWindow
from utils.logging import log_message

log_message("TRELLO CUSHIONS LAUNCHED")
log_message("Made with one shared braincell 🧠")

if __name__ == "__main__":
    try:
        log_message("Script launched")
        app = QApplication(sys.argv)
        app.setStyle("Fusion")
        window = TrelloCushionsWindow()
        window.show()
        sys.exit(app.exec())
    except Exception as e:
        log_message(f"Startup catastrophically failed: {str(e)}", level="CRITICAL")  # ← we can make logging support levels later if we want
        # Optional extra drama:
        print(f"Trello Cushions has entered the void: {str(e)}", file=sys.stderr)
        sys.exit(1)