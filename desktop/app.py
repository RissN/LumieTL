"""QApplication initialization, DPI configuration, and stylesheet application."""

import sys
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QIcon
from PySide6.QtCore import Qt
from core.config import APP_NAME, APP_VERSION, ASSETS_DIR
from desktop.ui.styles.theme import DARK_THEME_QSS


def create_application() -> QApplication:
    """Initialize and configure the Qt application."""
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )

    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)

    app.setApplicationName(APP_NAME)
    app.setApplicationVersion(APP_VERSION)
    app.setStyleSheet(DARK_THEME_QSS)

    icon_path = ASSETS_DIR / "icon.ico"
    if icon_path.exists():
        app.setWindowIcon(QIcon(str(icon_path)))

    return app
