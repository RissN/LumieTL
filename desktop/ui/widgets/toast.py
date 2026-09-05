"""Toast notification overlay widget."""

from PySide6.QtWidgets import QLabel
from PySide6.QtCore import Qt, QTimer
from core.config import COLORS


class Toast(QLabel):
    """Floating auto-dismiss toast notification message."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAlignment(Qt.AlignCenter)
        self.setStyleSheet(
            f"""
            QLabel {{
                background-color: {COLORS['bg_elevated']};
                color: {COLORS['text_primary']};
                border: 1px solid {COLORS['accent']};
                border-radius: 8px;
                padding: 10px 20px;
                font-weight: 500;
                font-size: 13px;
            }}
            """
        )
        self.hide()
        self._timer = QTimer(self)
        self._timer.setSingleShot(True)
        self._timer.timeout.connect(self.hide)

    def show_message(self, message: str, duration_ms: int = 3000):
        self.setText(message)
        self.adjustSize()
        if self.parent():
            parent_rect = self.parent().rect()
            x = (parent_rect.width() - self.width()) // 2
            y = parent_rect.height() - self.height() - 40
            self.move(x, y)
        self.show()
        self.raise_()
        self._timer.start(duration_ms)
