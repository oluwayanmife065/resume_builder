"""Typst template rendering and deterministic PDF compilation pipeline."""

from __future__ import annotations
import os
import shutil
import subprocess
from pathlib import Path
from typing import Optional, Union
from jinja2 import Environment, FileSystemLoader, select_autoescape

from src.schema import TailoredResumePayload, TailoredCoverLetterPayload


def escape_typst(text: str) -> str:
    """Escape Typst syntax characters to prevent compilation errors.

    Escapes characters that carry special syntactic meaning in Typst:
    - '\\' (escape sequence) -> '\\\\'
    - '$' (math mode) -> '\\$' (e.g. '$2,000+ budget' or '$240K saved')
    - '#' (code mode) -> '\\#' (e.g. 'C#')
    - '@' (citations/labels) -> '\\@'
    """
    if not isinstance(text, str):
        return str(text)

    replacements = [
        ("\\", "\\\\"),  # Must be first
        ("$", "\\$"),
        ("#", "\\#"),
        ("@", "\\@"),
    ]
    escaped = text
    for old, new in replacements:
        escaped = escaped.replace(old, new)
    return escaped


class TypstCompiler:
    """Renders Jinja-templated Typst files and compiles them to PDF via Typst CLI."""

    def __init__(
        self,
        templates_dir: Union[Path, str] = "templates",
        output_dir: Union[Path, str] = "output",
    ):
        self.templates_dir = Path(templates_dir)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.jinja_env = Environment(
            loader=FileSystemLoader(self.templates_dir),
            autoescape=select_autoescape(disabled_extensions=("typ.jinja", "typ")),
            trim_blocks=True,
            lstrip_blocks=True,
        )
        # Register custom Typst escaping filter
        self.jinja_env.filters["escape_typst"] = escape_typst

    def render_resume(
        self,
        payload: TailoredResumePayload,
        template_name: str = "resume.typ.jinja",
        output_filename: str = "tailored_resume",
    ) -> Path:
        """Render resume payload into a .typ source file."""
        template = self.jinja_env.get_template(template_name)
        rendered_content = template.render(resume=payload)

        typ_path = self.output_dir / f"{output_filename}.typ"
        typ_path.write_text(rendered_content, encoding="utf-8")
        return typ_path

    def render_cover_letter(
        self,
        payload: TailoredCoverLetterPayload,
        template_name: str = "cover_letter.typ.jinja",
        output_filename: str = "tailored_cover_letter",
    ) -> Path:
        """Render cover letter payload into a .typ source file."""
        template = self.jinja_env.get_template(template_name)
        rendered_content = template.render(letter=payload)

        typ_path = self.output_dir / f"{output_filename}.typ"
        typ_path.write_text(rendered_content, encoding="utf-8")
        return typ_path

    def compile_pdf(
        self,
        typ_file: Union[Path, str],
        pdf_filename: Optional[str] = None,
    ) -> Path:
        """Compile a rendered .typ file to PDF using the local Typst CLI."""
        typ_path = Path(typ_file)
        if not typ_path.exists():
            raise FileNotFoundError(f"Typst source file not found: {typ_path}")

        typst_bin = shutil.which("typst")
        if not typst_bin:
            # Common installation paths check
            for candidate in [
                "/opt/homebrew/bin/typst",
                "/usr/local/bin/typst",
                os.path.expanduser("~/.cargo/bin/typst"),
            ]:
                if os.path.isfile(candidate) and os.access(candidate, os.X_OK):
                    typst_bin = candidate
                    break

        if not typst_bin:
            raise RuntimeError(
                "Typst executable not found in PATH or standard locations.\n"
                "To compile PDFs directly, please install Typst:\n"
                "  - macOS: brew install typst\n"
                "  - Linux: cargo install --locked typst-cli\n"
                "  - Or download pre-built binary: https://github.com/typst/typst/releases"
            )

        if pdf_filename:
            pdf_path = self.output_dir / f"{pdf_filename}.pdf"
        else:
            pdf_path = typ_path.with_suffix(".pdf")

        cmd = [typst_bin, "compile", str(typ_path.resolve()), str(pdf_path.resolve())]
        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode != 0:
            raise RuntimeError(f"Typst compilation failed:\n{result.stderr}")

        return pdf_path
