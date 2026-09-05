"""Batch translation page processing folders of manga/manhwa chapters."""

from pathlib import Path
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QComboBox,
    QFileDialog,
    QProgressBar,
    QMessageBox,
)
from core.batch_processor import BatchItem, BatchProcessor
from core.config import COLORS, HISTORY_DB, TRANSLATOR_ENGINES
from core.history_manager import HistoryManager
from desktop.thread_worker import Worker
from desktop.ui.widgets.batch_table import BatchTable
from desktop.ui.widgets.lang_selector import SourceLangSelector, TargetLangSelector
from desktop.ui.widgets.toast import Toast
from security.keystore import get_keystore


class PageBatch(QWidget):
    """Page for batch-processing entire chapters or folders of images."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.history_manager = HistoryManager(HISTORY_DB)
        self.keystore = get_keystore()
        self.processor: BatchProcessor | None = None
        self._worker: Worker | None = None
        self._selected_dir: Path | None = None
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(14)

        # Header
        header = QVBoxLayout()
        header.setSpacing(4)
        title = QLabel("Proses Batch", self)
        title.setObjectName("heading")
        sub = QLabel("Terjemahkan seluruh folder gambar manga atau manhwa sekaligus", self)
        sub.setObjectName("subheading")
        header.addWidget(title)
        header.addWidget(sub)
        layout.addLayout(header)

        # Controls bar
        controls = QHBoxLayout()
        controls.setSpacing(10)

        self.btn_select_dir = QPushButton("📁 Pilih Folder", self)
        self.btn_select_dir.clicked.connect(self._on_select_dir)
        controls.addWidget(self.btn_select_dir)

        self.lbl_folder_path = QLabel("Belum ada folder yang dipilih", self)
        self.lbl_folder_path.setStyleSheet(f"color: {COLORS['text_secondary']};")
        controls.addWidget(self.lbl_folder_path)

        controls.addStretch()

        controls.addWidget(QLabel("Sumber:", self))
        self.combo_source = SourceLangSelector(self)
        controls.addWidget(self.combo_source)

        controls.addWidget(QLabel("Target:", self))
        self.combo_target = TargetLangSelector(self)
        controls.addWidget(self.combo_target)

        controls.addWidget(QLabel("Engine:", self))
        self.combo_engine = QComboBox(self)
        for k, v in TRANSLATOR_ENGINES.items():
            self.combo_engine.addItem(v, userData=k)
        controls.addWidget(self.combo_engine)

        layout.addLayout(controls)

        # Queue table
        self.table = BatchTable(self)
        layout.addWidget(self.table, 1)

        # Overall Progress Bar & status
        prog_box = QVBoxLayout()
        prog_box.setSpacing(4)
        self.lbl_progress_status = QLabel("0 / 0 selesai", self)
        self.lbl_progress_status.setStyleSheet(f"color: {COLORS['text_secondary']};")
        self.progress_bar = QProgressBar(self)
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        prog_box.addWidget(self.lbl_progress_status)
        prog_box.addWidget(self.progress_bar)
        layout.addLayout(prog_box)

        # Action Buttons
        btn_bar = QHBoxLayout()
        btn_bar.setSpacing(10)

        self.btn_start = QPushButton("Mulai Batch", self)
        self.btn_start.setObjectName("primary_button")
        self.btn_start.setEnabled(False)
        self.btn_start.clicked.connect(self._on_start_batch)
        btn_bar.addWidget(self.btn_start)

        self.btn_pause = QPushButton("Jeda", self)
        self.btn_pause.setEnabled(False)
        self.btn_pause.clicked.connect(self._on_pause_batch)
        btn_bar.addWidget(self.btn_pause)

        self.btn_cancel = QPushButton("Batal", self)
        self.btn_cancel.setEnabled(False)
        self.btn_cancel.clicked.connect(self._on_cancel_batch)
        btn_bar.addWidget(self.btn_cancel)

        btn_bar.addStretch()

        self.btn_export_log = QPushButton("Ekspor Log (.txt)", self)
        self.btn_export_log.setEnabled(False)
        self.btn_export_log.clicked.connect(self._on_export_log)
        btn_bar.addWidget(self.btn_export_log)

        layout.addLayout(btn_bar)

        self.toast = Toast(self)

    def _on_select_dir(self):
        dir_path = QFileDialog.getExistingDirectory(self, "Pilih Folder Berisi Gambar")
        if not dir_path:
            return

        self._selected_dir = Path(dir_path)
        self.lbl_folder_path.setText(self._selected_dir.name)

        # Initialize processor to scan items
        engine_key = self.combo_engine.currentData()
        self.processor = BatchProcessor(
            input_dir=self._selected_dir,
            source_lang=self.combo_source.get_selected_code(),
            target_lang=self.combo_target.get_selected_code(),
            engine=engine_key,
            history_manager=self.history_manager,
        )

        self.table.populate(self.processor.items)
        total = len(self.processor.items)
        self.lbl_progress_status.setText(f"0 / {total} selesai")
        self.progress_bar.setValue(0)
        self.btn_start.setEnabled(total > 0)
        self.btn_export_log.setEnabled(False)

        if total == 0:
            QMessageBox.information(
                self,
                "Folder Kosong",
                "Tidak ditemukan file gambar (JPG, PNG, WebP, AVIF) di folder ini.",
            )

    def _on_start_batch(self):
        if not self.processor or not self.processor.items:
            return

        engine_key = self.combo_engine.currentData()
        api_key = self.keystore.get(engine_key) if engine_key in ("deepl", "openai") else None

        if engine_key in ("deepl", "openai") and not api_key:
            QMessageBox.warning(
                self,
                "API Key Dibutuhkan",
                f"Silakan atur API Key untuk {TRANSLATOR_ENGINES[engine_key]} di Pengaturan terlebih dahulu.",
            )
            return

        self.processor.engine = engine_key
        self.processor.api_key = api_key
        self.processor.source_lang = self.combo_source.get_selected_code()
        self.processor.target_lang = self.combo_target.get_selected_code()

        self.btn_start.setEnabled(False)
        self.btn_pause.setEnabled(True)
        self.btn_cancel.setEnabled(True)
        self.btn_select_dir.setEnabled(False)

        # Worker for batch run
        self._worker = Worker(self.processor.run, item_progress_callback=self._on_item_progress)
        self._worker.finished.connect(self._on_batch_finished)
        self._worker.error.connect(self._on_batch_error)
        self._worker.start()

    def _on_item_progress(self, current_idx: int, total: int, item: BatchItem):
        row = current_idx - 1
        if 0 <= row < len(self.processor.items):
            self.table.update_row(row, item)

        percent = int((current_idx / total) * 100) if total > 0 else 0
        self.progress_bar.setValue(percent)
        completed = sum(1 for i in self.processor.items if i.status in ("success", "error", "skipped"))
        self.lbl_progress_status.setText(f"{completed} / {total} selesai")

    def _on_pause_batch(self):
        if not self.processor:
            return
        if self.processor.is_paused():
            self.processor.resume()
            self.btn_pause.setText("Jeda")
            self.toast.show_message("Batch dilanjutkan")
        else:
            self.processor.pause()
            self.btn_pause.setText("Lanjut")
            self.toast.show_message("Batch dijeda")

    def _on_cancel_batch(self):
        if self.processor:
            self.processor.cancel()
            self.toast.show_message("Membatalkan antrean batch...")

    def _on_batch_finished(self, items: list[BatchItem]):
        self.btn_start.setEnabled(True)
        self.btn_pause.setEnabled(False)
        self.btn_pause.setText("Jeda")
        self.btn_cancel.setEnabled(False)
        self.btn_select_dir.setEnabled(True)
        self.btn_export_log.setEnabled(True)
        self.toast.show_message("Pemrosesan batch selesai!")

    def _on_batch_error(self, err_msg: str):
        self.btn_start.setEnabled(True)
        self.btn_pause.setEnabled(False)
        self.btn_cancel.setEnabled(False)
        self.btn_select_dir.setEnabled(True)
        self.btn_export_log.setEnabled(True)
        QMessageBox.critical(self, "Kesalahan Batch", f"Batch gagal: {err_msg}")

    def _on_export_log(self):
        if not self.processor:
            return
        dest, _ = QFileDialog.getSaveFileName(
            self, "Simpan Laporan Batch", "batch_report.txt", "Text Files (*.txt)"
        )
        if dest:
            self.processor.export_log(Path(dest))
            self.toast.show_message("Laporan berhasil diekspor!")
