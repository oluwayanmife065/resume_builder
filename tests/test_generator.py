"""Unit tests for src/generator.py LLM engine and prompt formatting."""

import json
from unittest.mock import MagicMock, patch
import pytest

from src.generator import CareerAgentGenerator
from src.schema import (
    MasterProfile,
    JobDescriptionCriteria,
    TailoredResumePayload,
    TailoredCoverLetterPayload,
)
from src.extractor import load_master_profile, load_job_description, load_voice_samples


@pytest.fixture
def mock_master_profile() -> MasterProfile:
    return load_master_profile("data/master_profile.json")


@pytest.fixture
def mock_jd_criteria() -> JobDescriptionCriteria:
    return JobDescriptionCriteria(
        job_title="AI/ML Software Engineer",
        company_name="ModernTech AI",
        seniority_level="Mid-Senior",
        summary="Build scalable RAG pipelines and production machine learning services.",
        hard_skills=["Python", "PyTorch", "FastAPI", "Vector Search"],
        preferred_skills=["Ollama", "LanceDB", "Llama Guard"],
        key_phrasing_and_keywords=["sub-50ms latency", "cosine similarity retrieval", "prompt orchestration"],
        core_responsibilities=["Develop RAG systems", "Train and evaluate models"]
    )


def test_generator_initialization():
    """Verify CareerAgentGenerator initializes with custom or default model."""
    gen = CareerAgentGenerator(model_name="qwen2.5:14b")
    assert gen.model_name == "qwen2.5:14b"
    assert gen.client is not None


def test_extract_jd_criteria_prompt_and_schema(mock_jd_criteria):
    """Verify extract_jd_criteria constructs correct prompt and passes schema to Ollama."""
    gen = CareerAgentGenerator(model_name="qwen2.5:14b")
    mock_client = MagicMock()
    mock_client.chat.return_value = {
        "message": {"content": mock_jd_criteria.model_dump_json()}
    }
    gen.client = mock_client

    jd_text = "Sample Job Description for AI/ML Engineer..."
    criteria = gen.extract_jd_criteria(jd_text)

    # Verify return value
    assert isinstance(criteria, JobDescriptionCriteria)
    assert criteria.job_title == "AI/ML Software Engineer"
    assert "Python" in criteria.hard_skills

    # Verify call parameters
    mock_client.chat.assert_called_once()
    call_kwargs = mock_client.chat.call_args.kwargs
    assert call_kwargs["model"] == "qwen2.5:14b"
    assert call_kwargs["format"] == JobDescriptionCriteria.model_json_schema()
    assert any(jd_text in msg["content"] for msg in call_kwargs["messages"])


def test_generate_tailored_resume_strict_grounding_prompt(mock_master_profile, mock_jd_criteria):
    """Verify generate_tailored_resume enforces strict factual grounding and schema."""
    gen = CareerAgentGenerator(model_name="qwen2.5:14b")
    mock_client = MagicMock()

    # Create dummy tailored resume JSON payload
    dummy_payload = {
        "contact": mock_master_profile.contact.model_dump(),
        "target_role": "AI/ML Systems Engineer",
        "summary": "Software engineer with experience building RAG systems and full-stack APIs.",
        "skills": [c.model_dump() for c in mock_master_profile.skill_inventory[:2]],
        "experiences": [
            {
                "company": "Voicify",
                "title": "Software Engineering Intern (AI/ML)",
                "location": "Rochester, NY",
                "date_range": "May 2024 – Aug 2025",
                "bullets": ["Automated bug classification using Python + OpenAI."],
                "technologies": ["Python", "OpenAI API", "C#"]
            }
        ],
        "projects": [
            {
                "title": "RAG Chatbot",
                "role": "Creator & Lead Developer",
                "link": "https://issorientation.hamiltonlits.org/",
                "bullets": ["Built end-to-end RAG pipeline."],
                "technologies": ["Ollama", "LanceDB"]
            }
        ],
        "education": [mock_master_profile.education[0].model_dump()]
    }

    mock_client.chat.return_value = {
        "message": {"content": json.dumps(dummy_payload)}
    }
    gen.client = mock_client

    resume = gen.generate_tailored_resume(mock_master_profile, mock_jd_criteria)

    assert isinstance(resume, TailoredResumePayload)
    assert resume.target_role == "AI/ML Systems Engineer"

    # Verify prompt enforcement
    call_kwargs = mock_client.chat.call_args.kwargs
    assert call_kwargs["format"] == TailoredResumePayload.model_json_schema()
    
    system_msg = next(m["content"] for m in call_kwargs["messages"] if m["role"] == "system")
    assert "STRICT FACTUAL GROUNDING" in system_msg
    assert "NEVER invent or extrapolate" in system_msg

    user_msg = next(m["content"] for m in call_kwargs["messages"] if m["role"] == "user")
    assert mock_master_profile.contact.full_name in user_msg
    assert mock_jd_criteria.job_title in user_msg


def test_generate_tailored_cover_letter_voice_calibration(mock_master_profile, mock_jd_criteria):
    """Verify generate_tailored_cover_letter injects voice samples and bans cliches."""
    gen = CareerAgentGenerator(model_name="qwen2.5:14b")
    mock_client = MagicMock()

    dummy_letter = {
        "candidate_name": "Oluwayanmife Uriah Adeniran",
        "candidate_contact_line": "Rochester, NY | 315-790-2853",
        "date_str": "October 7, 2025",
        "recipient_title": "Hiring Committee",
        "company_name": "ModernTech AI",
        "job_title": "AI/ML Software Engineer",
        "salutation": "Dear Hiring Committee,",
        "opening_hook": "I am writing to apply for the AI/ML Software Engineer role...",
        "body_paragraphs": [
            "At Hamilton, I built RAG systems with LanceDB...",
            "During my internship at Voicify, I built production C# endpoints..."
        ],
        "closing_paragraph": "I look forward to discussing how my experience aligns with your team.",
        "sign_off": "Sincerely,"
    }

    mock_client.chat.return_value = {
        "message": {"content": json.dumps(dummy_letter)}
    }
    gen.client = mock_client

    voice_samples = load_voice_samples("data/voice_samples")
    letter = gen.generate_tailored_cover_letter(mock_master_profile, mock_jd_criteria, voice_samples)

    assert isinstance(letter, TailoredCoverLetterPayload)
    assert letter.company_name == "ModernTech AI"

    # Verify call parameters
    call_kwargs = mock_client.chat.call_args.kwargs
    assert call_kwargs["format"] == TailoredCoverLetterPayload.model_json_schema()

    system_msg = next(m["content"] for m in call_kwargs["messages"] if m["role"] == "system")
    assert "VOICE CALIBRATION RULES" in system_msg
    assert "FORBIDDEN CLICHÉS" in system_msg
    assert "thrilled" in system_msg

    user_msg = next(m["content"] for m in call_kwargs["messages"] if m["role"] == "user")
    assert "WRITING SAMPLE" in user_msg

