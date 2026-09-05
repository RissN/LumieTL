"""Drag & drop image upload area widget."""

from pathlib import Path
from PySide6.QtWidgets import QFrame, QVBoxLayout, QLabel, QFileDialog
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QDragEnterEvent, QDropEvent
from core.config import COLORS, ALLOWED_EXTENSIONS


class DropZone(QFrame):
    """Interactive drag and drop frame supporting image selection."""

    file_selected = Signal(Path)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)
        self.setCursor(Qt.PointingHandCursor)
        self._current_path: Path | None = None
        self._setup_ui()

    def _setup_ui(self):
        self.setObjectName("drop_zone")
        self.setStyleSheet(
            f"""
            QFrame#drop_zone {{
                border: 2px dashed {COLORS['border']};
                border-radius: 12px;
                background-color: {COLORS['bg_surface']};
                min-height: 280px;
            }}
            QFrame#drop_zone:hover {{
                border-color: {COLORS['accent']};
                background-color: {COLORS['bg_elevated']};
            }}
            """
        )

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(10)

        self.icon_label = QLabel("📥", self)
        self.icon_label.setAlignment(Qt.AlignCenter)
        self.icon_label.setStyleSheet("font-size: 36px; background: transparent;")

        self.text_label = QLabel(
            "Seret & lepas gambar di sini\natau klik untuk memilih berkas", self
        )
        self.text_label.setAlignment(Qt.AlignCenter)
        self.text_label.setStyleSheet(
            f"font-size: 14px; font-weight: 500; color: {COLORS['text_primary']}; background: transparent;"
        )

        self.hint_label = QLabel("JPG · PNG · WebP · AVIF (Maks. 50MB)", self)
        self.hint_label.setAlignment(Qt.AlignCenter)
        self.hint_label.setStyleSheet(
            f"font-size: 12px; color: {COLORS['text_secondary']}; background: transparent;"
        )

        layout.addWidget(self.icon_label)
        layout.addWidget(self.text_label)
        layout.addWidget(self.hint_label)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._browse_file()

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            for url in event.mimeData().urls():
                p = Path(url.toLocalFile())
                if p.suffix.lower() in ALLOWED_EXTENSIONS:
                    event.acceptProposedAction()
                    self.setStyleSheet(
                        f"""
                        QFrame#drop_zone {{
                            border: 2px solid {COLORS['accent']};
                            border-radius: 12px;
                            background-color: {COLORS['bg_elevated']};
                        }}
                        """
                    )
                    return
        event.ignore()

    def dragLeaveEvent(self, event):
        self._reset_style()

    def dropEvent(self, event: QDropEvent):
        self._reset_style()
        for url in event.mimeData().urls():
            path = Path(url.toLocalFile())
            if path.is_file() and path.suffix.lower() in ALLOWED_EXTENSIONS:
                self.set_file(path)
                break

    def _browse_file(self):
        ext_filter = "Gambar (" + " ".join(f"*{ext}" for ext in ALLOWED_EXTENSIONS) + ")"
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Pilih Gambar Manga / Manhwa", "", ext_filter
        )
        if file_path:
            self.set_file(Path(file_path))

    def set_file(self, path: Path):
        self._current_path = path
        self.text_label.setText(path.name)
        self.hint_label.setText(f"Ukuran: {path.stat().st_size // 1024} KB")
        self.file_selected.emit(path)

    def get_file(self) -> Path | None:
        return self._current_path

    def reset(self):
        self._current_path = None
        self.text_label.setText("Seret & lepas gambar di sini\natau klik untuk memilih berkas")
        self.hint_label.setText("JPG · PNG · WebP · AVIF (Maks. 50MB)")
        self._reset_style()

    def _reset_style(self):
        self.setStyleSheet(
            f"""
            QFrame#drop_zone {{
                border: 2px dashed {COLORS['border']};
                border-radius: 12px;
                background-color: {COLORS['bg_surface']};
                min-height: 280px;
            }}
            QFrame#drop_zone:hover {{
                border-color: {COLORS['accent']};
                background-color: {COLORS['bg_elevated']};
            }}
            """
        )
