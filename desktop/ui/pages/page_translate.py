"""Single image translation page."""

import shutil
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
    QApplication,
    QMessageBox,
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QClipboard, QImage
from core.config import COLORS, HISTORY_DB, OUTPUT_DIR, TRANSLATOR_ENGINES
from core.history_manager import HistoryEntry, HistoryManager
from core.translator import translate_image
from desktop.thread_worker import Worker
from desktop.ui.widgets.drop_zone import DropZone
from desktop.ui.widgets.image_viewer import ImageViewer
from desktop.ui.widgets.lang_selector import SourceLangSelector, TargetLangSelector
from desktop.ui.widgets.toast import Toast
from security.keystore import get_keystore
from utils.file_utils import safe_output_path


class PageTranslate(QWidget):
    """Page for single image manga/manhwa translation."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.history_manager = HistoryManager(HISTORY_DB)
        self.keystore = get_keystore()
        self._worker: Worker | None = None
        self._current_input_path: Path | None = None
        self._current_output_path: Path | None = None
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(14)

        # Title & Subheading
        header_box = QVBoxLayout()
        header_box.setSpacing(4)
        title = QLabel("Terjemahkan Gambar", self)
        title.setObjectName("heading")
        sub = QLabel("Unggah halaman manga atau manhwa untuk diterjemahkan secara otomatis", self)
        sub.setObjectName("subheading")
        header_box.addWidget(title)
        header_box.addWidget(sub)
        layout.addLayout(header_box)

        # Controls bar
        controls_layout = QHBoxLayout()
        controls_layout.setSpacing(12)

        # Source Lang
        lbl_src = QLabel("Sumber:", self)
        self.combo_source = SourceLangSelector(self)
        controls_layout.addWidget(lbl_src)
        controls_layout.addWidget(self.combo_source)

        # Target Lang
        lbl_tgt = QLabel("Target:", self)
        self.combo_target = TargetLangSelector(self)
        controls_layout.addWidget(lbl_tgt)
        controls_layout.addWidget(self.combo_target)

        # Engine
        lbl_eng = QLabel("Engine:", self)
        self.combo_engine = QComboBox(self)
        for key, name in TRANSLATOR_ENGINES.items():
            self.combo_engine.addItem(name, userData=key)
        controls_layout.addWidget(lbl_eng)
        controls_layout.addWidget(self.combo_engine)

        controls_layout.addStretch()

        # Translate Button
        self.btn_translate = QPushButton("Terjemahkan", self)
        self.btn_translate.setObjectName("primary_button")
        self.btn_translate.clicked.connect(self._on_translate_clicked)
        controls_layout.addWidget(self.btn_translate)

        layout.addLayout(controls_layout)

        # Progress bar
        self.progress_bar = QProgressBar(self)
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.hide()
        layout.addWidget(self.progress_bar)

        # Main workspace: Split Left (DropZone) & Right (ImageViewer)
        content_box = QHBoxLayout()
        content_box.setSpacing(16)

        self.drop_zone = DropZone(self)
        self.drop_zone.file_selected.connect(self._on_file_selected)
        content_box.addWidget(self.drop_zone, 1)

        self.viewer = ImageViewer(self)
        content_box.addWidget(self.viewer, 1)

        layout.addLayout(content_box, 1)

        # Bottom Actions bar
        actions_bar = QHBoxLayout()
        actions_bar.setSpacing(10)

        self.status_info = QLabel("", self)
        self.status_info.setStyleSheet(f"color: {COLORS['text_secondary']};")
        actions_bar.addWidget(self.status_info)

        actions_bar.addStretch()

        self.btn_save = QPushButton("💾 Simpan Hasil", self)
        self.btn_save.setEnabled(False)
        self.btn_save.clicked.connect(self._on_save_clicked)
        actions_bar.addWidget(self.btn_save)

        self.btn_copy = QPushButton("📋 Salin ke Clipboard", self)
        self.btn_copy.setEnabled(False)
        self.btn_copy.clicked.connect(self._on_copy_clicked)
        actions_bar.addWidget(self.btn_copy)

        layout.addLayout(actions_bar)

        # Toast overlay
        self.toast = Toast(self)

    def _on_file_selected(self, path: Path):
        self._current_input_path = path
        self._current_output_path = None
        self.viewer.set_images(path, None)
        self.status_info.setText(f"File dipilih: {path.name}")
        self.btn_save.setEnabled(False)
        self.btn_copy.setEnabled(False)

    def _on_translate_clicked(self):
        if not self._current_input_path:
            QMessageBox.warning(self, "Peringatan", "Silakan pilih gambar terlebih dahulu!")
            return

        engine_key = self.combo_engine.currentData()
        api_key = None
        if engine_key in ("deepl", "openai"):
            api_key = self.keystore.get(engine_key)
            if not api_key:
                QMessageBox.warning(
                    self,
                    "Kunci API Diperlukan",
                    f"Anda belum memasukkan API Key untuk {TRANSLATOR_ENGINES[engine_key]}.\n"
                    "Silakan buka tab Pengaturan untuk memasukkan kunci API.",
                )
                return

        output_filename = f"translated_{self._current_input_path.name}"
        output_path = safe_output_path(OUTPUT_DIR, output_filename)

        self.btn_translate.setEnabled(False)
        self.btn_translate.setText("Menerjemahkan...")
        self.progress_bar.setValue(10)
        self.progress_bar.show()
        self.status_info.setText("Memulai proses...")

        self._worker = Worker(
            translate_image,
            input_path=self._current_input_path,
            source_lang=self.combo_source.get_selected_code(),
            target_lang=self.combo_target.get_selected_code(),
            engine=engine_key,
            output_path=output_path,
            api_key=api_key,
        )
        self._worker.progress.connect(self._on_worker_progress)
        self._worker.finished.connect(self._on_worker_finished)
        self._worker.error.connect(self._on_worker_error)
        self._worker.start()

    def _on_worker_progress(self, current: int, total: int, msg: str):
        self.progress_bar.setValue(current)
        if msg:
            self.status_info.setText(msg)

    def _on_worker_finished(self, result: tuple[Path, float]):
        output_path, duration = result
        self._current_output_path = output_path

        self.viewer.set_images(self._current_input_path, self._current_output_path)
        self.btn_translate.setEnabled(True)
        self.btn_translate.setText("Terjemahkan")
        self.progress_bar.hide()
        self.btn_save.setEnabled(True)
        self.btn_copy.setEnabled(True)
        self.status_info.setText(f"Selesai dalam {duration:.2f} detik")

        # Save to history
        self.history_manager.add(
            HistoryEntry(
                input_path=str(self._current_input_path),
                output_path=str(self._current_output_path),
                source_lang=self.combo_source.get_selected_code(),
                target_lang=self.combo_target.get_selected_code(),
                engine=self.combo_engine.currentData(),
                duration=duration,
                success=True,
            )
        )

        self.toast.show_message("Terjemahan berhasil selesai!")

    def _on_worker_error(self, error_msg: str):
        self.btn_translate.setEnabled(True)
        self.btn_translate.setText("Terjemahkan")
        self.progress_bar.hide()
        self.status_info.setText("Gagal.")

        # Record failure in history
        if self._current_input_path:
            self.history_manager.add(
                HistoryEntry(
                    input_path=str(self._current_input_path),
                    output_path=None,
                    source_lang=self.combo_source.get_selected_code(),
                    target_lang=self.combo_target.get_selected_code(),
                    engine=self.combo_engine.currentData(),
                    duration=0.0,
                    success=False,
                    error=error_msg,
                )
            )

        QMessageBox.critical(self, "Kesalahan Terjemahan", f"Terjadi kesalahan:\n{error_msg}")

    def _on_save_clicked(self):
        if not self._current_output_path or not self._current_output_path.exists():
            return

        dest_file, _ = QFileDialog.getSaveFileName(
            self,
            "Simpan Gambar Hasil",
            self._current_output_path.name,
            "Images (*.png *.jpg *.webp)",
        )
        if dest_file:
            shutil.copy2(self._current_output_path, dest_file)
            self.toast.show_message("Gambar berhasil disimpan!")

    def _on_copy_clicked(self):
        if not self._current_output_path or not self._current_output_path.exists():
            return

        image = QImage(str(self._current_output_path))
        if not image.isNull():
            clipboard = QApplication.clipboard()
            clipboard.setImage(image)
            self.toast.show_message("Disalin ke clipboard!")
