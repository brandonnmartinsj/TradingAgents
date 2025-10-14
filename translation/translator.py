"""Core translation functionality using OpenAI."""

import os
from pathlib import Path
from typing import Optional
from langchain_openai import ChatOpenAI

from .config import TranslationConfig, DEFAULT_TRANSLATION_CONFIG


class ReportTranslator:
    """Handles translation of trading reports to Brazilian Portuguese."""

    def __init__(
        self,
        config: Optional[TranslationConfig] = None,
        api_key: Optional[str] = None,
    ):
        """Initialize the translator.

        Args:
            config: Translation configuration. Uses default if not provided.
            api_key: OpenAI API key. Uses OPENAI_API_KEY env var if not provided.
        """
        self.config = config or DEFAULT_TRANSLATION_CONFIG
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")

        if not self.api_key:
            raise ValueError(
                "OpenAI API key is required. Set OPENAI_API_KEY environment variable "
                "or pass api_key parameter."
            )

        self.client = ChatOpenAI(
            model=self.config.model,
            temperature=self.config.temperature,
            max_tokens=self.config.max_tokens,
            api_key=self.api_key,
        )

    def translate_text(self, text: str) -> str:
        """Translate text using OpenAI.

        Args:
            text: Text to translate

        Returns:
            Translated text in Brazilian Portuguese
        """
        if not text or not text.strip():
            return text

        try:
            messages = [
                ("system", self.config.system_prompt),
                ("user", self.config.user_prompt_template.format(content=text)),
            ]

            response = self.client.invoke(messages)
            translated_text = response.content
            return translated_text.strip()

        except Exception as e:
            raise RuntimeError(f"Translation failed: {e}")

    def translate_file(
        self, input_path: Path, output_path: Optional[Path] = None
    ) -> Path:
        """Translate a markdown file.

        Args:
            input_path: Path to input markdown file
            output_path: Path to save translated file. If None, appends '_pt-BR' to filename.

        Returns:
            Path to translated file
        """
        input_path = Path(input_path)

        if not input_path.exists():
            raise FileNotFoundError(f"Input file not found: {input_path}")

        # Read original content
        with open(input_path, "r", encoding="utf-8") as f:
            original_content = f.read()

        # Translate
        print(f"Translating {input_path.name}...")
        translated_content = self.translate_text(original_content)

        # Determine output path
        if output_path is None:
            output_path = input_path.parent / f"{input_path.stem}_pt-BR{input_path.suffix}"
        else:
            output_path = Path(output_path)

        # Create output directory if needed
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Write translated content
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(translated_content)

        print(f"[OK] Saved to {output_path}")
        return output_path

    def translate_reports_directory(
        self, reports_dir: Path, output_dir: Optional[Path] = None
    ) -> list[Path]:
        """Translate all markdown files in a reports directory.

        Args:
            reports_dir: Directory containing report markdown files
            output_dir: Directory to save translated files. If None, saves alongside originals.

        Returns:
            List of paths to translated files
        """
        reports_dir = Path(reports_dir)

        if not reports_dir.exists():
            raise FileNotFoundError(f"Reports directory not found: {reports_dir}")

        # Find all markdown files
        md_files = list(reports_dir.glob("*.md"))

        if not md_files:
            print(f"No markdown files found in {reports_dir}")
            return []

        translated_files = []
        print(f"\nFound {len(md_files)} report(s) to translate\n")

        for md_file in md_files:
            # Skip already translated files
            if "_pt-BR" in md_file.stem:
                print(f"[SKIP] {md_file.name} (already translated)")
                continue

            try:
                if output_dir:
                    output_path = output_dir / f"{md_file.stem}_pt-BR{md_file.suffix}"
                else:
                    output_path = None

                translated_path = self.translate_file(md_file, output_path)
                translated_files.append(translated_path)

            except Exception as e:
                print(f"[ERROR] translating {md_file.name}: {e}")
                continue

        return translated_files
