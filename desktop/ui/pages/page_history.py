"""Translation history page with filtering, deletion, and file opening."""

import os
import subprocess
import sys
from pathlib import Path
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QComboBox,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QMessageBox,
)
from PySide6.QtCore import Qt
from core.config import COLORS, HISTORY_DB, TRANSLATOR_ENGINES
from core.history_manager import HistoryEntry, HistoryManager
from desktop.ui.widgets.toast import Toast


class PageHistory(QWidget):
    """Page displaying historical translation records stored in SQLite."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.history_manager = HistoryManager(HISTORY_DB)
        self._entries: list[HistoryEntry] = []
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(14)

        # Header
        header = QVBoxLayout()
        header.setSpacing(4)
        title = QLabel("Riwayat Terjemahan", self)
        title.setObjectName("heading")
        sub = QLabel("Daftar terjemahan yang telah selesai atau gagal", self)
        sub.setObjectName("subheading")
        header.addWidget(title)
        header.addWidget(sub)
        layout.addLayout(header)

        # Filters & Actions bar
        filter_bar = QHBoxLayout()
        filter_bar.setSpacing(10)

        filter_bar.addWidget(QLabel("Filter Engine:", self))
        self.combo_filter_engine = QComboBox(self)
        self.combo_filter_engine.addItem("Semua Engine", userData=None)
        for k, v in TRANSLATOR_ENGINES.items():
            self.combo_filter_engine.addItem(v, userData=k)
        self.combo_filter_engine.currentIndexChanged.connect(self.load_history)
        filter_bar.addWidget(self.combo_filter_engine)

        filter_bar.addWidget(QLabel("Status:", self))
        self.combo_filter_status = QComboBox(self)
        self.combo_filter_status.addItem("Semua Status", userData=None)
        self.combo_filter_status.addItem("Berhasil", userData=True)
        self.combo_filter_status.addItem("Gagal", userData=False)
        self.combo_filter_status.currentIndexChanged.connect(self.load_history)
        filter_bar.addWidget(self.combo_filter_status)

        filter_bar.addStretch()

        self.btn_refresh = QPushButton("Segarkan", self)
        self.btn_refresh.clicked.connect(self.load_history)
        filter_bar.addWidget(self.btn_refresh)

        self.btn_clear = QPushButton("Hapus Semua", self)
        self.btn_clear.setStyleSheet(f"color: {COLORS['error']};")
        self.btn_clear.clicked.connect(self._on_clear_all)
        filter_bar.addWidget(self.btn_clear)

        layout.addLayout(filter_bar)

        # History Table
        self.table = QTableWidget(self)
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels(
            ["Tanggal", "File Sumber", "Bahasa", "Engine", "Durasi", "Status", "Aksi"]
        )
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(5, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(6, QHeaderView.ResizeToContents)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.verticalHeader().setVisible(False)
        layout.addWidget(self.table, 1)

        self.toast = Toast(self)
        self.load_history()

    def load_history(self):
        engine = self.combo_filter_engine.currentData()
        status = self.combo_filter_status.currentData()

        self._entries = self.history_manager.get_all(limit=200, engine=engine, success=status)
        self.table.setRowCount(len(self._entries))

        for row, entry in enumerate(self._entries):
            # Timestamp
            self.table.setItem(row, 0, QTableWidgetItem(entry.timestamp))

            # Input filename
            name = Path(entry.input_path).name
            self.table.setItem(row, 1, QTableWidgetItem(name))

            # Lang
            lang_str = f"{entry.source_lang} ➔ {entry.target_lang}"
            self.table.setItem(row, 2, QTableWidgetItem(lang_str))

            # Engine
            eng_str = TRANSLATOR_ENGINES.get(entry.engine, entry.engine)
            self.table.setItem(row, 3, QTableWidgetItem(eng_str))

            # Duration
            dur_str = f"{entry.duration:.2f}s" if entry.duration > 0 else "—"
            item_dur = QTableWidgetItem(dur_str)
            item_dur.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(row, 4, item_dur)

            # Status
            status_text = "✅ Selesai" if entry.success else "❌ Gagal"
            self.table.setItem(row, 5, QTableWidgetItem(status_text))

            # Action button
            action_btn = QPushButton("Buka Hasil" if entry.output_path else "Hapus", self)
            action_btn.clicked.connect(lambda checked=False, e=entry: self._on_action_clicked(e))
            self.table.setCellWidget(row, 6, action_btn)

    def _on_action_clicked(self, entry: HistoryEntry):
        if entry.output_path and Path(entry.output_path).exists():
            out_file = Path(entry.output_path)
            if sys.platform == "win32":
                os.startfile(str(out_file))
            else:
                subprocess.run(["xdg-open", str(out_file)])
        else:
            # Delete record
            if entry.id:
                self.history_manager.delete(entry.id)
                self.load_history()
                self.toast.show_message("Item riwayat dihapus")

    def _on_clear_all(self):
        confirm = QMessageBox.question(
            self,
            "Konfirmasi Hapus",
            "Apakah Anda yakin ingin menghapus seluruh riwayat terjemahan?",
            QMessageBox.Yes | QMessageBox.No,
        )
        if confirm == QMessageBox.Yes:
            self.history_manager.clear_all()
            self.load_history()
            self.toast.show_message("Riwayat berhasil dibersihkan!")
