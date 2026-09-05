"""Before/after comparison viewer with interactive split slider and zoom."""

from pathlib import Path
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel
from PySide6.QtCore import Qt, QRect, QPoint
from PySide6.QtGui import QPainter, QPixmap, QColor, QPen
from core.config import COLORS


class SplitCanvas(QWidget):
    """Canvas drawing before and after images with interactive vertical divider slider."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMouseTracking(True)
        self._pixmap_before: QPixmap | None = None
        self._pixmap_after: QPixmap | None = None
        self._split_ratio: float = 0.5  # 0.0 (all after) to 1.0 (all before)
        self._dragging_slider: bool = False
        self._scale_factor: float = 1.0

    def set_images(self, before_path: Path | None, after_path: Path | None):
        if before_path and before_path.exists():
            self._pixmap_before = QPixmap(str(before_path))
        else:
            self._pixmap_before = None

        if after_path and after_path.exists():
            self._pixmap_after = QPixmap(str(after_path))
        else:
            self._pixmap_after = None

        self._scale_factor = 1.0
        self.update()

    def set_scale(self, factor: float):
        self._scale_factor = max(0.2, min(5.0, factor))
        self.update()

    def zoom_in(self):
        self.set_scale(self._scale_factor * 1.2)

    def zoom_out(self):
        self.set_scale(self._scale_factor / 1.2)

    def reset_zoom(self):
        self.set_scale(1.0)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            slider_x = int(self.width() * self._split_ratio)
            if abs(event.position().x() - slider_x) <= 15:
                self._dragging_slider = True

    def mouseMoveEvent(self, event):
        slider_x = int(self.width() * self._split_ratio)
        if abs(event.position().x() - slider_x) <= 15 or self._dragging_slider:
            self.setCursor(Qt.SplitHCursor)
        else:
            self.setCursor(Qt.ArrowCursor)

        if self._dragging_slider:
            new_ratio = max(0.02, min(0.98, event.position().x() / self.width()))
            self._split_ratio = new_ratio
            self.update()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._dragging_slider = False

    def wheelEvent(self, event):
        delta = event.angleDelta().y()
        if delta > 0:
            self.zoom_in()
        elif delta < 0:
            self.zoom_out()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setRenderHint(QPainter.SmoothPixmapTransform)

        # Background
        painter.fillRect(self.rect(), QColor(COLORS["bg_surface"]))

        if not self._pixmap_before and not self._pixmap_after:
            painter.setPen(QColor(COLORS["text_secondary"]))
            painter.drawText(
                self.rect(),
                Qt.AlignCenter,
                "Hasil terjemahan akan tampil di sini",
            )
            return

        ref_pix = self._pixmap_after or self._pixmap_before
        if not ref_pix:
            return

        # Calculate fitted scaled dimensions
        base_w = ref_pix.width()
        base_h = ref_pix.height()

        fit_scale = min(self.width() / base_w, self.height() / base_h)
        scaled_w = int(base_w * fit_scale * self._scale_factor)
        scaled_h = int(base_h * fit_scale * self._scale_factor)

        x_off = (self.width() - scaled_w) // 2
        y_off = (self.height() - scaled_h) // 2
        dest_rect = QRect(x_off, y_off, scaled_w, scaled_h)

        split_x = int(self.width() * self._split_ratio)

        # If only one image is available (e.g. before processing or after processing only)
        if not self._pixmap_before or not self._pixmap_after:
            target = self._pixmap_after or self._pixmap_before
            painter.drawPixmap(dest_rect, target)
            return

        # 1. Draw "After" (Right side / background)
        painter.save()
        clip_after = QRect(split_x, 0, self.width() - split_x, self.height())
        painter.setClipRect(clip_after)
        painter.drawPixmap(dest_rect, self._pixmap_after)
        painter.restore()

        # 2. Draw "Before" (Left side / clipped)
        painter.save()
        clip_before = QRect(0, 0, split_x, self.height())
        painter.setClipRect(clip_before)
        painter.drawPixmap(dest_rect, self._pixmap_before)
        painter.restore()

        # 3. Draw Splitter Line & Handle
        painter.setPen(QPen(QColor(COLORS["accent"]), 2))
        painter.drawLine(split_x, 0, split_x, self.height())

        # Handle circle
        center_y = self.height() // 2
        painter.setBrush(QColor(COLORS["accent"]))
        painter.drawEllipse(QPoint(split_x, center_y), 12, 12)

        # Handle label indicators
        painter.setPen(QColor("#FFFFFF"))
        painter.drawText(
            QRect(split_x - 12, center_y - 12, 24, 24), Qt.AlignCenter, "⬌"
        )


class ImageViewer(QWidget):
    """Complete viewer container with controls."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)

        self.canvas = SplitCanvas(self)
        layout.addWidget(self.canvas, 1)

        # Zoom toolbar
        bar = QHBoxLayout()
        bar.setContentsMargins(6, 4, 6, 4)

        self.label_hint = QLabel("Sebelum ◀ | ▶ Sesudah (Geser garis pembatas)", self)
        self.label_hint.setStyleSheet(f"color: {COLORS['text_secondary']}; font-size: 11px;")
        bar.addWidget(self.label_hint)

        bar.addStretch()

        btn_zoom_in = QPushButton("🔍 +", self)
        btn_zoom_in.setFixedWidth(50)
        btn_zoom_in.clicked.connect(self.canvas.zoom_in)

        btn_zoom_out = QPushButton("🔍 -", self)
        btn_zoom_out.setFixedWidth(50)
        btn_zoom_out.clicked.connect(self.canvas.zoom_out)

        btn_reset = QPushButton("Reset Zoom", self)
        btn_reset.clicked.connect(self.canvas.reset_zoom)

        bar.addWidget(btn_zoom_in)
        bar.addWidget(btn_zoom_out)
        bar.addWidget(btn_reset)

        layout.addLayout(bar)

    def set_images(self, before_path: Path | None, after_path: Path | None):
        self.canvas.set_images(before_path, after_path)
