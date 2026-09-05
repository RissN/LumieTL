"""First-run model setup and download manager dialog."""

from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QProgressBar,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
)
from PySide6.QtCore import Qt
from core.config import COLORS, MODEL_DIR
from core.model_manager import MODEL_REGISTRY, download_model, get_missing_models, models_ready
from desktop.thread_worker import Worker


class ModelSetupDialog(QDialog):
    """Initial setup dialog downloading required ONNX models with progress reporting."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("LumieTL — Penyiapan Model AI")
        self.setFixedSize(520, 420)
        self.setWindowFlags(Qt.Dialog | Qt.CustomizeWindowHint | Qt.WindowTitleHint)
        self._worker: Worker | None = None
        self._missing_keys: list[str] = []
        self._current_idx = 0
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(14)

        title = QLabel("Pengunduhan Model Penerjemah", self)
        title.setStyleSheet(f"font-size: 16px; font-weight: bold; color: {COLORS['text_primary']};")
        layout.addWidget(title)

        desc = QLabel(
            "LumieTL memerlukan beberapa model ONNX lokal untuk deteksi balon teks, "
            "OCR, dan pembersihan latar gambar (in-painting). Model diunduh sekali saja.",
            self,
        )
        desc.setWordWrap(True)
        desc.setStyleSheet(f"color: {COLORS['text_secondary']}; line-height: 1.4;")
        layout.addWidget(desc)

        self.list_widget = QListWidget(self)
        self.list_widget.setStyleSheet(
            f"""
            QListWidget {{
                background-color: {COLORS['bg_base']};
                border: 1px solid {COLORS['border']};
                border-radius: 6px;
                padding: 6px;
            }}
            QListWidget::item {{
                padding: 8px;
                border-bottom: 1px solid {COLORS['border']};
            }}
            """
        )
        layout.addWidget(self.list_widget)

        self.status_label = QLabel("Siap mengunduh model...", self)
        self.status_label.setStyleSheet(f"font-size: 12px; color: {COLORS['text_secondary']};")
        layout.addWidget(self.status_label)

        self.progress_bar = QProgressBar(self)
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        layout.addWidget(self.progress_bar)

        # Buttons
        btn_box = QHBoxLayout()
        btn_box.addStretch()

        self.btn_cancel = QPushButton("Keluar", self)
        self.btn_cancel.clicked.connect(self._on_cancel)
        btn_box.addWidget(self.btn_cancel)

        self.btn_start = QPushButton("Unduh Sekarang", self)
        self.btn_start.setObjectName("primary_button")
        self.btn_start.clicked.connect(self._start_download)
        btn_box.addWidget(self.btn_start)

        layout.addLayout(btn_box)

        self._refresh_model_list()

    def _refresh_model_list(self):
        self.list_widget.clear()
        missing = get_missing_models()
        self._missing_keys = [m["key"] for m in missing]

        for key, spec in MODEL_REGISTRY.items():
            is_downloaded = key not in self._missing_keys
            status_text = "✅ Sudah Ada" if is_downloaded else f"⏳ Perlu Diunduh (~{spec['size_mb']} MB)"
            item = QListWidgetItem(f"{spec['description']} ({spec['filename']})\n  Status: {status_text}")
            self.list_widget.addItem(item)

        if not self._missing_keys:
            self.btn_start.setText("Selesai")
            self.status_label.setText("Semua model sudah siap digunakan!")
            self.progress_bar.setValue(100)

    def _start_download(self):
        if not self._missing_keys:
            self.accept()
            return

        self.btn_start.setEnabled(False)
        self.btn_cancel.setText("Batal")
        self._current_idx = 0
        self._download_next()

    def _download_next(self):
        if self._current_idx >= len(self._missing_keys):
            self.status_label.setText("Semua model berhasil diunduh dan diverifikasi!")
            self.btn_start.setEnabled(True)
            self.btn_start.setText("Buka LumieTL")
            self.btn_cancel.setEnabled(False)
            self._refresh_model_list()
            return

        key = self._missing_keys[self._current_idx]
        spec = MODEL_REGISTRY[key]
        self.status_label.setText(f"Mengunduh {spec['description']}...")

        self._worker = Worker(download_model, key, MODEL_DIR)
        self._worker.progress.connect(self._on_progress)
        self._worker.finished.connect(self._on_item_finished)
        self._worker.error.connect(self._on_error)
        self._worker.start()

    def _on_progress(self, current: int, total: int, msg: str):
        self.progress_bar.setValue(current)
        if msg:
            self.status_label.setText(msg)

    def _on_item_finished(self, result):
        self._current_idx += 1
        self._download_next()

    def _on_error(self, error_msg: str):
        self.btn_start.setEnabled(True)
        self.btn_start.setText("Coba Lagi")
        self.btn_cancel.setText("Keluar")
        self.status_label.setText("Pengunduhan gagal.")
        QMessageBox.critical(self, "Kesalahan Unduhan", f"Gagal mengunduh model:\n{error_msg}")

    def _on_cancel(self):
        if self._worker and self._worker.isRunning():
            self._worker.cancel()
            self._worker.wait()
        self.reject()
