"""Translation configuration."""

from dataclasses import dataclass
from typing import Literal


@dataclass
class TranslationConfig:
    """Configuration for translation service."""

    target_language: str = "pt-BR"
    model: str = "gpt-4o-mini"
    temperature: float = 0.3
    max_tokens: int = 4000
    preserve_formatting: bool = True

    # Translation prompt settings
    system_prompt: str = """You are a professional translator specializing in financial and trading documents.
Translate the following text from English to Brazilian Portuguese (pt-BR).

IMPORTANT INSTRUCTIONS:
1. Preserve ALL markdown formatting (headers, lists, bold, italic, tables, etc.)
2. Keep technical terms accurate and use standard Brazilian Portuguese financial terminology
3. Maintain the professional and analytical tone
4. Do NOT translate:
   - Stock tickers (e.g., ITSA4.SA, NVDA)
   - Technical indicator names (MACD, RSI, SMA, ATR, etc.)
   - Dates and numbers
   - Company names (keep original)
5. Translate naturally - avoid literal translations that sound awkward in Portuguese
6. Use financial terminology common in Brazil (e.g., "ação" not "estoque", "lucro" not "ganho")

Return ONLY the translated text, maintaining the exact same structure."""

    user_prompt_template: str = """Translate this financial report to Brazilian Portuguese:

{content}"""


DEFAULT_TRANSLATION_CONFIG = TranslationConfig()
