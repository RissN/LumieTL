"""Main window with sidebar navigation and stacked pages."""

from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
    QFrame,
    QPushButton,
    QLabel,
    QStackedWidget,
    QButtonGroup,
)
from PySide6.QtCore import Qt
from core.config import APP_NAME, APP_VERSION, COLORS
from desktop.ui.pages.page_translate import PageTranslate
from desktop.ui.pages.page_batch import PageBatch
from desktop.ui.pages.page_history import PageHistory
from desktop.ui.pages.page_settings import PageSettings
from desktop.ui.styles.icons import get_icon


class MainWindow(QMainWindow):
    """Primary application window hosting the navigation sidebar and views."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle(f"{APP_NAME} v{APP_VERSION} — Manga/Manhwa Auto-Translator")
        self.resize(1100, 720)
        self.setMinimumSize(950, 600)
        self._setup_ui()

    def _setup_ui(self):
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)

        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # 1. Sidebar Frame
        sidebar = QFrame(self)
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(210)

        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(14, 20, 14, 20)
        sidebar_layout.setSpacing(8)

        # App Logo & Brand
        brand_layout = QHBoxLayout()
        brand_layout.setSpacing(10)
        logo_icon = QLabel("✨", self)
        logo_icon.setStyleSheet("font-size: 22px;")
        brand_title = QLabel(APP_NAME, self)
        brand_title.setStyleSheet(
            f"font-size: 18px; font-weight: bold; color: {COLORS['text_primary']}; letter-spacing: 0.5px;"
        )
        brand_layout.addWidget(logo_icon)
        brand_layout.addWidget(brand_title)
        brand_layout.addStretch()
        sidebar_layout.addLayout(brand_layout)

        sidebar_layout.addSpacing(18)

        # Navigation Buttons
        self.nav_group = QButtonGroup(self)
        self.nav_group.setExclusive(True)

        self.btn_nav_translate = self._create_nav_button("🖼  Terjemahkan", 0)
        self.btn_nav_batch = self._create_nav_button("⚡  Batch", 1)
        self.btn_nav_history = self._create_nav_button("📋  Riwayat", 2)
        self.btn_nav_settings = self._create_nav_button("⚙  Pengaturan", 3)

        sidebar_layout.addWidget(self.btn_nav_translate)
        sidebar_layout.addWidget(self.btn_nav_batch)
        sidebar_layout.addWidget(self.btn_nav_history)
        sidebar_layout.addWidget(self.btn_nav_settings)

        sidebar_layout.addStretch()

        # Bottom Version Info
        lbl_ver = QLabel(f"v{APP_VERSION}", self)
        lbl_ver.setStyleSheet(f"color: {COLORS['text_secondary']}; font-size: 11px;")
        sidebar_layout.addWidget(lbl_ver)

        main_layout.addWidget(sidebar)

        # 2. Content Stack Area
        content_frame = QFrame(self)
        content_frame.setObjectName("content_area")
        content_layout = QVBoxLayout(content_frame)
        content_layout.setContentsMargins(0, 0, 0, 0)

        self.stack = QStackedWidget(self)
        self.page_translate = PageTranslate(self)
        self.page_batch = PageBatch(self)
        self.page_history = PageHistory(self)
        self.page_settings = PageSettings(self)

        self.stack.addWidget(self.page_translate)
        self.stack.addWidget(self.page_batch)
        self.stack.addWidget(self.page_history)
        self.stack.addWidget(self.page_settings)

        content_layout.addWidget(self.stack)
        main_layout.addWidget(content_frame, 1)

        # Default selected page
        self.btn_nav_translate.setChecked(True)

    def _create_nav_button(self, text: str, page_index: int) -> QPushButton:
        btn = QPushButton(text, self)
        btn.setObjectName("sidebar_button")
        btn.setCheckable(True)
        btn.setCursor(Qt.PointingHandCursor)
        self.nav_group.addButton(btn, page_index)
        btn.clicked.connect(lambda: self._switch_page(page_index))
        return btn

    def _switch_page(self, index: int):
        self.stack.setCurrentIndex(index)
        if index == 2:  # Refresh history when navigating to history tab
            self.page_history.load_history()
