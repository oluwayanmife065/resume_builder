"""Unit tests for src/compiler.py Jinja2-Typst rendering and compilation."""

from pathlib import Path
from unittest.mock import MagicMock, patch
import pytest

from src.compiler import TypstCompiler, escape_typst
from src.schema import (
    ContactInfo,
    EducationItem,
    SkillCategory,
    TailoredExperience,
    TailoredProject,
    TailoredResumePayload,
    TailoredCoverLetterPayload,
)


@pytest.fixture
def sample_resume_payload() -> TailoredResumePayload:
    contact = ContactInfo(
        full_name="Oluwayanmife Uriah Adeniran",
        email="uriahadeniran065@gmail.com",
        phone="315-790-2853",
        location="Rochester, NY",
        linkedin_url="https://bit.ly/uriah_linkedin",
        github_url="https://github.com/Uriahadeniran09",
        portfolio_url="https://bit.ly/uriah_portfolio"
    )
    return TailoredResumePayload(
        contact=contact,
        target_role="AI/ML Systems Engineer",
        summary="Software engineer with strong foundation in AI/ML systems and production backend APIs.",
        skills=[
            SkillCategory(category_name="Languages", skills=["Python", "C#", "C++", "SQL"]),
            SkillCategory(category_name="Frameworks", skills=["FastAPI", "PyTorch", "React", "ASP.NET Core"])
        ],
        experiences=[
            TailoredExperience(
                company="Voicify",
                title="Software Engineering Intern (AI/ML)",
                location="Rochester, NY",
                date_range="May 2024 – Aug 2025",
                bullets=[
                    "Built and deployed C# backend APIs, improving response latency by 20%.",
                    "Automated bug classification using Python + OpenAI, saving $50,000+ in engineering hours."
                ],
                technologies=["C#", "Python", "ASP.NET Core"]
            )
        ],
        projects=[
            TailoredProject(
                title="RAG Chatbot (LLM + Vector Search)",
                role="Creator & Lead Developer",
                link="https://issorientation.hamiltonlits.org/",
                bullets=["Built end-to-end RAG pipeline using Ollama Qwen2.5 and LanceDB."],
                technologies=["Ollama", "LanceDB"]
            )
        ],
        education=[
            EducationItem(
                institution="Hamilton College",
                degree="B.S.",
                field_of_study="Computer Science and Economics",
                graduation_date="May 2026",
                location="Clinton, NY",
                gpa="3.72 / 4.0",
                highlights=["Coursework: Algorithms, Deep Learning, Machine Learning"]
            )
        ]
    )


@pytest.fixture
def sample_cover_letter_payload() -> TailoredCoverLetterPayload:
    return TailoredCoverLetterPayload(
        candidate_name="Oluwayanmife Uriah Adeniran",
        candidate_contact_line="Rochester, NY | 315-790-2853 | uriahadeniran065@gmail.com",
        date_str="October 15, 2025",
        recipient_title="Hiring Committee",
        company_name="ModernTech AI",
        job_title="AI/ML Software Engineer",
        salutation="Dear Hiring Committee,",
        opening_hook="I am writing to apply for the AI/ML Software Engineer role at ModernTech AI.",
        body_paragraphs=[
            "At Hamilton, I built full-stack applications and low-latency RAG systems with LanceDB...",
            "During my internship at Voicify, I built C# APIs and automated call labeling workflows..."
        ],
        closing_paragraph="I welcome the opportunity to discuss how my system design skills align with your team.",
        sign_off="Sincerely,"
    )


def test_escape_typst():
    """Verify that escape_typst properly handles Typst special characters."""
    assert escape_typst("Budget was $2,000+ for the project") == r"Budget was \$2,000+ for the project"
    assert escape_typst("C# and #1 ranking") == r"C\# and \#1 ranking"
    assert escape_typst("Contact @company") == r"Contact \@company"
    assert escape_typst(123) == "123"


def test_render_resume(tmp_path: Path, sample_resume_payload: TailoredResumePayload):
    """Verify render_resume populates the Jinja template and writes a valid .typ file."""
    compiler = TypstCompiler(templates_dir="templates", output_dir=tmp_path)
    output_typ = compiler.render_resume(sample_resume_payload, output_filename="test_resume")

    assert output_typ.exists()
    content = output_typ.read_text(encoding="utf-8")

    # Verify key sections rendered
    assert "Oluwayanmife Uriah Adeniran" in content
    assert "AI/ML Systems Engineer" in content
    assert "Voicify" in content
    assert r"C\#" in content  # Escaped C#
    assert r"\$50,000+" in content  # Escaped $
    assert "RAG Chatbot" in content
    assert "Hamilton College" in content


def test_render_cover_letter(tmp_path: Path, sample_cover_letter_payload: TailoredCoverLetterPayload):
    """Verify render_cover_letter populates the Jinja template and writes a valid .typ file."""
    compiler = TypstCompiler(templates_dir="templates", output_dir=tmp_path)
    output_typ = compiler.render_cover_letter(sample_cover_letter_payload, output_filename="test_letter")

    assert output_typ.exists()
    content = output_typ.read_text(encoding="utf-8")

    # Verify letter components
    assert "Oluwayanmife Uriah Adeniran" in content
    assert "ModernTech AI" in content
    assert "October 15, 2025" in content
    assert "Dear Hiring Committee," in content
    assert "At Hamilton, I built full-stack applications" in content
    assert "Sincerely," in content


def test_compile_pdf_file_not_found(tmp_path: Path):
    """Verify compile_pdf raises FileNotFoundError when .typ file does not exist."""
    compiler = TypstCompiler(templates_dir="templates", output_dir=tmp_path)
    with pytest.raises(FileNotFoundError):
        compiler.compile_pdf(tmp_path / "missing.typ")


def test_compile_pdf_missing_binary(tmp_path: Path):
    """Verify compile_pdf raises RuntimeError with helpful install instructions if typst not installed."""
    compiler = TypstCompiler(templates_dir="templates", output_dir=tmp_path)
    fake_typ = tmp_path / "fake.typ"
    fake_typ.write_text("#set page(paper: 'us-letter')\nHello World", encoding="utf-8")

    with patch("shutil.which", return_value=None):
        with patch("os.path.isfile", return_value=False):
            with pytest.raises(RuntimeError, match="Typst executable not found"):
                compiler.compile_pdf(fake_typ)

