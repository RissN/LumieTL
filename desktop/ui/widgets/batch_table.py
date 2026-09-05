"""Table widget for batch queue display."""

from PySide6.QtWidgets import QTableWidget, QTableWidgetItem, QHeaderView
from PySide6.QtCore import Qt
from core.batch_processor import BatchItem
from core.config import COLORS


class BatchTable(QTableWidget):
    """Queue table displaying batch items, processing states, and execution durations."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self):
        self.setColumnCount(4)
        self.setHorizontalHeaderLabels(["Nama File", "Status", "Durasi", "Keterangan"])
        self.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.horizontalHeader().setSectionResizeMode(3, QHeaderView.Stretch)
        self.setSelectionBehavior(QTableWidget.SelectRows)
        self.setEditTriggers(QTableWidget.NoEditTriggers)
        self.verticalHeader().setVisible(False)

    def populate(self, items: list[BatchItem]):
        self.setRowCount(len(items))
        for row, item in enumerate(items):
            self.update_row(row, item)

    def update_row(self, row: int, item: BatchItem):
        # File name
        item_name = QTableWidgetItem(item.input_path.name)
        item_name.setForeground(Qt.white)

        # Status badge
        status_map = {
            "pending": ("⏸ Menunggu", COLORS["text_secondary"]),
            "processing": ("⏳ Memproses", COLORS["accent"]),
            "success": ("✅ Selesai", COLORS["success"]),
            "error": ("❌ Gagal", COLORS["error"]),
            "skipped": ("⏭ Dilewati", COLORS["warning"]),
        }
        text, color_hex = status_map.get(item.status, (item.status, COLORS["text_secondary"]))
        item_status = QTableWidgetItem(text)

        # Duration
        dur_text = f"{item.duration:.2f}s" if item.duration > 0 else "—"
        item_dur = QTableWidgetItem(dur_text)
        item_dur.setTextAlignment(Qt.AlignCenter)

        # Error / details
        item_err = QTableWidgetItem(item.error or "")

        self.setItem(row, 0, item_name)
        self.setItem(row, 1, item_status)
        self.setItem(row, 2, item_dur)
        self.setItem(row, 3, item_err)
