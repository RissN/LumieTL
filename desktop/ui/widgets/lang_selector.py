"""Language selection dropdown widgets."""

from PySide6.QtWidgets import QComboBox
from core.config import SOURCE_LANGS, TARGET_LANGS


class SourceLangSelector(QComboBox):
    """Combobox for choosing the source language."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumWidth(160)
        for code, name in SOURCE_LANGS.items():
            self.addItem(name, userData=code)

    def get_selected_code(self) -> str:
        return self.currentData()

    def set_by_code(self, code: str):
        idx = self.findData(code)
        if idx >= 0:
            self.setCurrentIndex(idx)


class TargetLangSelector(QComboBox):
    """Combobox for choosing the target translation language."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumWidth(160)
        for code, name in TARGET_LANGS.items():
            self.addItem(name, userData=code)

    def get_selected_code(self) -> str:
        return self.currentData()

    def set_by_code(self, code: str):
        idx = self.findData(code)
        if idx >= 0:
            self.setCurrentIndex(idx)
