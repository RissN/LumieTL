"""Translation pipeline wrapper integrating manga-image-translator with LumieTL engines."""

import time
from pathlib import Path
from typing import Callable
from core.config import MODEL_DIR
from core.exceptions import (
    FileValidationError,
    ModelNotFoundError,
    TranslationError,
    UnsupportedEngineError,
)
from core.model_manager import models_ready
from core.rate_limiter import RATE_LIMITERS
from utils.file_utils import validate_image_file
from utils.logger import get_logger

logger = get_logger()
SUPPORTED_ENGINES = {"google", "deepl", "openai"}


def check_prerequisites(input_path: Path, model_dir: Path | None = None) -> None:
    """Validate input file and model readiness before executing translation."""
    is_valid, reason = validate_image_file(input_path)
    if not is_valid:
        raise FileValidationError(f"Invalid input image: {reason}")

    target_models = model_dir or MODEL_DIR
    if not models_ready(target_models):
        raise ModelNotFoundError(
            "Model ONNX belum lengkap. Silakan unduh model terlebih dahulu melalui Model Setup."
        )


async def translate_image(
    input_path: Path,
    source_lang: str,
    target_lang: str,
    engine: str,
    output_path: Path,
    model_dir: Path | None = None,
    api_key: str | None = None,
    progress_callback: Callable[[int, int, str], None] | None = None,
    cancel_check: Callable[[], bool] | None = None,
) -> tuple[Path, float]:
    """
    Execute translation pipeline on a single image.
    Returns tuple of (output_path, duration_seconds).
    """
    start_time = time.time()
    engine_key = engine.lower()

    if engine_key not in SUPPORTED_ENGINES:
        raise UnsupportedEngineError(f"Engine '{engine}' is not supported")

    if cancel_check and cancel_check():
        raise TranslationError("Translation cancelled by user")

    if progress_callback:
        progress_callback(10, 100, "Memvalidasi input...")

    models_path = model_dir or MODEL_DIR
    check_prerequisites(input_path, models_path)

    if progress_callback:
        progress_callback(20, 100, f"Menunggu kuota engine {engine}...")

    # Rate limiting
    RATE_LIMITERS[engine_key].wait_if_needed()

    if cancel_check and cancel_check():
        raise TranslationError("Translation cancelled by user")

    if progress_callback:
        progress_callback(35, 100, "Menjalankan deteksi teks dan OCR...")

    # Ensure output directory exists
    output_path.parent.mkdir(parents=True, exist_ok=True)

    try:
        # Dynamically import manga_translator to keep startup swift
        from manga_translator import Config, MangaTranslator

        config_kwargs = {
            "translator": engine_key,
            "target_lang": target_lang,
            "source_lang": source_lang,
            "detector": "default",
            "ocr": "48px",
            "inpainter": "lama_mpe",
            "upscaler": "none",
            "model_dir": str(models_path),
        }

        # Inject provider-specific API keys if provided
        if engine_key == "deepl" and api_key:
            config_kwargs["deepl_api_key"] = api_key
        elif engine_key == "openai" and api_key:
            config_kwargs["openai_api_key"] = api_key

        if progress_callback:
            progress_callback(55, 100, "Menerjemahkan teks dan inpainting...")

        config = Config(**config_kwargs)
        mt = MangaTranslator(config)

        if cancel_check and cancel_check():
            raise TranslationError("Translation cancelled by user")

        await mt.translate_file(str(input_path), str(output_path))

        if progress_callback:
            progress_callback(100, 100, "Selesai")

        duration = time.time() - start_time
        logger.info(
            "Successfully translated %s -> %s using %s in %.2fs",
            input_path.name,
            output_path.name,
            engine_key,
            duration,
        )
        return output_path, duration

    except Exception as e:
        duration = time.time() - start_time
        logger.error("Translation failed for %s: %s", input_path.name, e)
        if isinstance(e, (FileValidationError, ModelNotFoundError, UnsupportedEngineError, TranslationError)):
            raise
        raise TranslationError(f"Translation failed: {e}") from e
