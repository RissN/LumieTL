"""Settings and preferences page."""

import os
import subprocess
import sys
from pathlib import Path
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QGridLayout,
    QLabel,
    QPushButton,
    QLineEdit,
    QComboBox,
    QSpinBox,
    QCheckBox,
    QFileDialog,
    QMessageBox,
)
from core.config import (
    APP_DATA_DIR,
    COLORS,
    OUTPUT_DIR,
    SETTINGS_FILE,
    TRANSLATOR_ENGINES,
)
from core.model_manager import get_missing_models, models_ready
from desktop.ui.widgets.lang_selector import SourceLangSelector, TargetLangSelector
from desktop.ui.widgets.model_setup_dialog import ModelSetupDialog
from desktop.ui.widgets.toast import Toast
from security.keystore import get_keystore
from security.settings_crypto import load_settings, save_settings


class PageSettings(QWidget):
    """Page for configuring application settings, API keys, fonts, and directories."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.keystore = get_keystore()
        self._setup_ui()
        self._load_saved_settings()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)

        # Header
        header = QVBoxLayout()
        header.setSpacing(4)
        title = QLabel("Pengaturan", self)
        title.setObjectName("heading")
        sub = QLabel("Konfigurasi bahasa default, kredensial API, dan penyimpanan berkas", self)
        sub.setObjectName("subheading")
        header.addWidget(title)
        header.addWidget(sub)
        layout.addLayout(header)

        grid = QGridLayout()
        grid.setVerticalSpacing(12)
        grid.setHorizontalSpacing(16)
        row = 0

        # Section: Default Languages
        lbl_lang_sec = QLabel("Preferensi Bahasa & Engine", self)
        lbl_lang_sec.setStyleSheet(f"font-weight: bold; color: {COLORS['accent']};")
        grid.addWidget(lbl_lang_sec, row, 0, 1, 2)
        row += 1

        grid.addWidget(QLabel("Bahasa Sumber Default:", self), row, 0)
        self.combo_source = SourceLangSelector(self)
        grid.addWidget(self.combo_source, row, 1)
        row += 1

        grid.addWidget(QLabel("Bahasa Target Default:", self), row, 0)
        self.combo_target = TargetLangSelector(self)
        grid.addWidget(self.combo_target, row, 1)
        row += 1

        grid.addWidget(QLabel("Engine Terjemahan Default:", self), row, 0)
        self.combo_engine = QComboBox(self)
        for k, v in TRANSLATOR_ENGINES.items():
            self.combo_engine.addItem(v, userData=k)
        grid.addWidget(self.combo_engine, row, 1)
        row += 1

        # Section: API Keys
        lbl_api_sec = QLabel("Kredensial API (Disimpan Aman)", self)
        lbl_api_sec.setStyleSheet(f"font-weight: bold; color: {COLORS['accent']}; margin-top: 10px;")
        grid.addWidget(lbl_api_sec, row, 0, 1, 2)
        row += 1

        grid.addWidget(QLabel("DeepL API Key:", self), row, 0)
        self.input_deepl = QLineEdit(self)
        self.input_deepl.setEchoMode(QLineEdit.Password)
        self.input_deepl.setPlaceholderText("Masukkan API Key DeepL")
        grid.addWidget(self.input_deepl, row, 1)
        row += 1

        grid.addWidget(QLabel("OpenAI API Key:", self), row, 0)
        self.input_openai = QLineEdit(self)
        self.input_openai.setEchoMode(QLineEdit.Password)
        self.input_openai.setPlaceholderText("sk-proj-...")
        grid.addWidget(self.input_openai, row, 1)
        row += 1

        # Section: Performance & Rendering
        lbl_perf_sec = QLabel("Performa & Rendering Teks", self)
        lbl_perf_sec.setStyleSheet(f"font-weight: bold; color: {COLORS['accent']}; margin-top: 10px;")
        grid.addWidget(lbl_perf_sec, row, 0, 1, 2)
        row += 1

        grid.addWidget(QLabel("Akselerasi GPU (CUDA):", self), row, 0)
        self.check_gpu = QCheckBox("Gunakan GPU jika tersedia", self)
        grid.addWidget(self.check_gpu, row, 1)
        row += 1

        grid.addWidget(QLabel("Ukuran Font Render:", self), row, 0)
        self.spin_font_size = QSpinBox(self)
        self.spin_font_size.setRange(8, 48)
        self.spin_font_size.setValue(14)
        grid.addWidget(self.spin_font_size, row, 1)
        row += 1

        # Section: Paths & Storage
        lbl_path_sec = QLabel("Penyimpanan & Model", self)
        lbl_path_sec.setStyleSheet(f"font-weight: bold; color: {COLORS['accent']}; margin-top: 10px;")
        grid.addWidget(lbl_path_sec, row, 0, 1, 2)
        row += 1

        grid.addWidget(QLabel("Folder Output Default:", self), row, 0)
        out_layout = QHBoxLayout()
        self.input_output_dir = QLineEdit(self)
        self.input_output_dir.setText(str(OUTPUT_DIR))
        out_layout.addWidget(self.input_output_dir)
        btn_browse = QPushButton("Jelajahi...", self)
        btn_browse.clicked.connect(self._on_browse_output_dir)
        out_layout.addWidget(btn_browse)
        grid.addLayout(out_layout, row, 1)
        row += 1

        grid.addWidget(QLabel("Kelola Model AI:", self), row, 0)
        self.btn_check_models = QPushButton("Cek & Unduh Ulang Model", self)
        self.btn_check_models.clicked.connect(self._on_check_models)
        grid.addWidget(self.btn_check_models, row, 1)
        row += 1

        layout.addLayout(grid)
        layout.addStretch()

        # Bottom Buttons
        btn_bar = QHBoxLayout()
        btn_bar.setSpacing(10)

        self.btn_open_appdata = QPushButton("📁 Buka Folder AppData", self)
        self.btn_open_appdata.clicked.connect(self._on_open_appdata)
        btn_bar.addWidget(self.btn_open_appdata)

        self.btn_reset = QPushButton("Reset Pengaturan", self)
        self.btn_reset.setStyleSheet(f"color: {COLORS['error']};")
        self.btn_reset.clicked.connect(self._on_reset)
        btn_bar.addWidget(self.btn_reset)

        btn_bar.addStretch()

        self.btn_save = QPushButton("Simpan Pengaturan", self)
        self.btn_save.setObjectName("primary_button")
        self.btn_save.clicked.connect(self._on_save_settings)
        btn_bar.addWidget(self.btn_save)

        layout.addLayout(btn_bar)
        self.toast = Toast(self)

    def _load_saved_settings(self):
        saved = load_settings(SETTINGS_FILE)

        src = saved.get("default_source_lang", "auto")
        self.combo_source.set_by_code(src)

        tgt = saved.get("default_target_lang", "ID")
        self.combo_target.set_by_code(tgt)

        eng = saved.get("default_engine", "google")
        idx = self.combo_engine.findData(eng)
        if idx >= 0:
            self.combo_engine.setCurrentIndex(idx)

        self.check_gpu.setChecked(bool(saved.get("gpu_enabled", False)))
        self.spin_font_size.setValue(int(saved.get("font_size", 14)))
        self.input_output_dir.setText(saved.get("output_dir", str(OUTPUT_DIR)))

        # Load API keys from Keystore
        deepl_k = self.keystore.get("deepl")
        if deepl_k:
            self.input_deepl.setText(deepl_k)

        openai_k = self.keystore.get("openai")
        if openai_k:
            self.input_openai.setText(openai_k)

    def _on_browse_output_dir(self):
        chosen = QFileDialog.getExistingDirectory(self, "Pilih Folder Output")
        if chosen:
            self.input_output_dir.setText(chosen)

    def _on_open_appdata(self):
        if sys.platform == "win32":
            os.startfile(str(APP_DATA_DIR))
        else:
            subprocess.run(["xdg-open", str(APP_DATA_DIR)])

    def _on_check_models(self):
        dialog = ModelSetupDialog(self)
        dialog.exec()

    def _on_reset(self):
        confirm = QMessageBox.question(
            self,
            "Reset Pengaturan",
            "Apakah Anda yakin ingin mengembalikan semua pengaturan ke default?",
            QMessageBox.Yes | QMessageBox.No,
        )
        if confirm == QMessageBox.Yes:
            self.combo_source.set_by_code("auto")
            self.combo_target.set_by_code("ID")
            self.combo_engine.setCurrentIndex(0)
            self.check_gpu.setChecked(False)
            self.spin_font_size.setValue(14)
            self.input_output_dir.setText(str(OUTPUT_DIR))
            self.toast.show_message("Pengaturan dikembalikan ke default")

    def _on_save_settings(self):
        data = {
            "default_source_lang": self.combo_source.get_selected_code(),
            "default_target_lang": self.combo_target.get_selected_code(),
            "default_engine": self.combo_engine.currentData(),
            "gpu_enabled": self.check_gpu.isChecked(),
            "font_size": self.spin_font_size.value(),
            "output_dir": self.input_output_dir.text().strip(),
        }

        # Save encrypted settings
        save_settings(data, SETTINGS_FILE)

        # Save API keys securely in keystore
        deepl_val = self.input_deepl.text().strip()
        if deepl_val:
            self.keystore.save("deepl", deepl_val)
        else:
            self.keystore.delete("deepl")

        openai_val = self.input_openai.text().strip()
        if openai_val:
            self.keystore.save("openai", openai_val)
        else:
            self.keystore.delete("openai")

        self.toast.show_message("Pengaturan berhasil disimpan!")
