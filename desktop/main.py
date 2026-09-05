"""Desktop application entry point."""

import sys
from pathlib import Path

# Add project root to sys.path so modules can be imported directly
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from core.config import ensure_directories
from core.model_manager import models_ready
from desktop.app import create_application
from desktop.ui.main_window import MainWindow
from desktop.ui.widgets.model_setup_dialog import ModelSetupDialog
from utils.logger import setup_logger

logger = setup_logger()


def main():
    """Application main runner."""
    ensure_directories()
    app = create_application()

    # If first run and models are missing, prompt setup dialog
    if not models_ready():
        dialog = ModelSetupDialog()
        result = dialog.exec()
        if result != ModelSetupDialog.Accepted:
            logger.info("Application exited by user during model setup.")
            sys.exit(0)

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
