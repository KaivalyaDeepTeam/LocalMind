"""
LocalMind Internationalization (i18n) Module

Handles multi-language support using Qt's translation system.
"""

from pathlib import Path
from typing import Optional, Dict

from PySide6.QtCore import QTranslator, QLocale, QCoreApplication


class TranslationManager:
    """Manages application translations using Qt's i18n system."""

    # Supported languages with native names
    LANGUAGES: Dict[str, str] = {
        "en": "English",
        "ru": "Русский",
        "es": "Español",
        "hi": "हिन्दी",
        "ar": "العربية",
    }

    def __init__(self):
        self._translator: Optional[QTranslator] = None
        self._current_language: str = "en"
        self._translations_dir = Path(__file__).parent / "translations"

    @property
    def current_language(self) -> str:
        """Get the currently loaded language code."""
        return self._current_language

    @classmethod
    def get_available_languages(cls) -> Dict[str, str]:
        """Get dictionary of available languages {code: native_name}."""
        return cls.LANGUAGES.copy()

    @classmethod
    def get_language_name(cls, code: str) -> str:
        """Get native name for a language code."""
        return cls.LANGUAGES.get(code, code)

    def load_translation(self, language: str) -> bool:
        """
        Load translation for the specified language.

        Args:
            language: Language code (e.g., 'en', 'ru', 'es')

        Returns:
            True if translation loaded successfully, False otherwise
        """
        app = QCoreApplication.instance()
        if app is None:
            return False

        # Remove existing translator
        if self._translator is not None:
            app.removeTranslator(self._translator)
            self._translator = None

        # English is the source language, no translation needed
        if language == "en":
            self._current_language = "en"
            return True

        # Check if translation file exists
        translation_file = self._translations_dir / f"{language}.qm"
        if not translation_file.exists():
            # Try to use .ts file directly (for development)
            translation_file = self._translations_dir / f"{language}.ts"
            if not translation_file.exists():
                # Fallback to English
                self._current_language = "en"
                return False

        # Load the translation
        self._translator = QTranslator()
        if self._translator.load(str(translation_file)):
            app.installTranslator(self._translator)
            self._current_language = language
            return True
        else:
            self._translator = None
            self._current_language = "en"
            return False

    def get_system_language(self) -> str:
        """
        Get the system's preferred language if supported.

        Returns:
            Language code if supported, otherwise 'en'
        """
        locale = QLocale.system()
        language_code = locale.name().split("_")[0]  # e.g., 'en_US' -> 'en'

        if language_code in self.LANGUAGES:
            return language_code
        return "en"


# Global translation manager instance
_translation_manager: Optional[TranslationManager] = None


def get_translation_manager() -> TranslationManager:
    """Get the global translation manager instance."""
    global _translation_manager
    if _translation_manager is None:
        _translation_manager = TranslationManager()
    return _translation_manager


def init_translations(language: str = "en") -> TranslationManager:
    """
    Initialize the translation system with the specified language.

    Args:
        language: Language code to load

    Returns:
        The translation manager instance
    """
    manager = get_translation_manager()
    manager.load_translation(language)
    return manager
