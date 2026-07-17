"""MGX entry point."""

import logging
import sys

from PyQt6.QtWidgets import QApplication

from core.logging.logger import setup_logging
from gui.windows.main_window import MainWindow


def main() -> int:
    setup_logging(level=logging.INFO)
    logger = logging.getLogger("mgx")
    logger.info("Starting MGX")

    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
