"""Wrapper around manga-image-translator for image translation.

This module provides a clean async interface that the API layer calls.
It handles engine validation, rate limiting, cancellation, and
delegates actual translation to the manga-image-translator library.
"""

from pathlib import Path
from typing import Callable

from core.config import MODEL_DIR
from core.exceptions import TranslationError, UnsupportedEngineError
from core.rate_limiter import RATE_LIMITERS
from utils.logger import audit

SUPPORTED_ENGINES: set[str] = {"google", "deepl", "openai"}


async def translate_image(
    input_path: Path,
    source_lang: str,
    target_lang: str,
    engine: str,
    output_path: Path,
    api_key: str | None = None,
    cancel_check: Callable[[], bool] | None = None,
) -> Path:
    """Translate text in an image file and write the result to *output_path*.

    Parameters
    ----------
    input_path:
        Path to the source image.
    source_lang:
        Source language code (e.g. ``"JPN"``, ``"auto"``).
    target_lang:
        Target language code (e.g. ``"ID"``, ``"EN"``).
    engine:
        Translation engine identifier (``"google"``, ``"deepl"``, ``"openai"``).
    output_path:
        Where to write the translated image.
    api_key:
        API key for engines that require one (DeepL, OpenAI).
    cancel_check:
        Optional callable; if it returns ``True`` the translation is aborted.

    Returns
    -------
    Path
        The *output_path* after successful translation.
    """
    if engine not in SUPPORTED_ENGINES:
        raise UnsupportedEngineError(f"Engine '{engine}' is not supported")

    # Apply per-engine rate limiting (blocks if limit reached)
    RATE_LIMITERS[engine].wait_if_needed()

    if cancel_check and cancel_check():
        raise TranslationError("Cancelled by user")

    audit(
        "translate_start",
        f"engine={engine} source={source_lang} target={target_lang} "
        f"file={input_path.name}",
    )

    try:
        # Import here to defer heavy dependency loading
        from manga_translator import MangaTranslator

        # Build translator arguments
        translator_params = {
            "target_lang": target_lang,
            "translator": engine,
            "detector": "default",
            "ocr": "48px",
            "inpainter": "lama_mpe",
            "direction": "auto",
        }

        if source_lang and source_lang != "auto":
            translator_params["source_lang"] = source_lang

        if api_key:
            translator_params["translator_api_key"] = api_key

        mt = MangaTranslator(translator_params)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        await mt.translate_path(str(input_path), str(output_path))

    except ImportError:
        raise TranslationError(
            "manga-image-translator is not installed. "
            "Run: pip install git+https://github.com/zyddnys/manga-image-translator.git"
        )
    except TranslationError:
        raise
    except Exception as e:
        raise TranslationError(f"Translation failed: {e}") from e

    if not output_path.exists():
        raise TranslationError(
            "Translation produced no output file — the pipeline may have "
            "failed silently."
        )

    return output_path
