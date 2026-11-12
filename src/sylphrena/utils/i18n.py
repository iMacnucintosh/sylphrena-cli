"""Minimal gettext-style lookup for CLI user-facing strings.

Uses LANG/LC_ALL/LC_MESSAGES (first two letters). English is the source language.
"""

from __future__ import annotations

import os

_TRANSLATIONS: dict[str, dict[str, str]] = {
    "es": {
        "Recording started": "Grabación iniciada",
        "Recording...": "Grabando…",
        "Recording failed": "Error al grabar",
        "An error occurred attempting to start recorder. Command `{cmd}` failed with exit code {code}": (
            "Se produjo un error al iniciar el grabador. "
            "El comando `{cmd}` falló con el código de salida {code}"
        ),
        "Recording stopped": "Grabación detenida",
        "Recording saved in {path}": "Grabación guardada en {path}",
        "Watch": "Ver",
        "Open": "Abrir",
        "Delete": "Eliminar",
    },
}


def _lang() -> str:
    for key in ("LC_ALL", "LC_MESSAGES", "LANG"):
        value = os.environ.get(key, "")
        if value and value != "C" and not value.startswith("C."):
            return value.replace("-", "_").split(".")[0].split("_")[0].lower()
    return "en"


def tr(message: str, **kwargs: object) -> str:
    """Translate `message`, optionally formatting with kwargs (``{name}`` placeholders)."""
    table = _TRANSLATIONS.get(_lang(), {})
    text = table.get(message, message)
    if kwargs:
        return text.format(**kwargs)
    return text
