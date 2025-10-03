import json
import os
from pathlib import Path
from config.settings import *


class Language:
    def __init__(self, language_code="en", language_dir="locales"):
        self.language_code = language_code
        self.translations = {}
        self.load_language(language_dir)

    def load_language(self, language_dir):
        """Load the language file for the specified language code."""
        try:
            language_file = Path(language_dir) / f"{self.language_code}.json"
            with open(language_file, "r", encoding="utf-8") as f:
                self.translations = json.load(f).get(self.language_code, {})
        except (FileNotFoundError, json.JSONDecodeError):
            print(
                f"Warning: Language file for '{self.language_code}' not found or invalid. Using defaults."
            )
            self.translations = {}

    def get(self, key, *args, default=None):
        """Get a translated string by key, with optional formatting."""
        message = self.translations.get(key, default or f"Missing translation: {key}")
        try:
            return message.format(*args)
        except (IndexError, KeyError):
            return message  # Return unformatted if formatting fails


# Initialize language (load once at startup)
language = Language(LANGUAGE)
