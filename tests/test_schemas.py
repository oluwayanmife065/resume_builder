"""Unit and integration tests for Step 1 schemas and data validation."""

import json
from pathlib import Path
import pytest
from pydantic import ValidationError

from src.schema import (
    ContactInfo,
    ExperienceItem,
    EducationItem,
    ProjectItem,
    SkillCategory,
    MasterProfile,
    JobDescriptionCriteria,
    TailoredExperience,
    TailoredProject,
    TailoredResumePayload,
    TailoredCoverLetterPayload,
)


# ==============================================================================
# 1. Master Profile Tests
# ==============================================================================

def test_master_profile_json_exists():
    """Verify master_profile.json exists and is valid JSON."""
    profile_path = Path("data/master_profile.json")
    assert profile_path.exists(), "data/master_profile.json does not exist"
    
    with open(profile_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert isinstance(data, dict), "master_profile.json is not a JSON object"


def test_master_profile_schema_validation():
    """Validate master_profile.json against MasterProfile Pydantic schema."""
    with open("data/master_profile.json", "r", encoding="utf-8") as f:
        data = json.load(f)

    profile = MasterProfile.model_validate(data)

    # Candidate Contact
    assert profile.contact.full_name == "Oluwayanmife Uriah Adeniran"
    assert profile.contact.email == "uriahadeniran065@gmail.com"
    assert "Rochester" in profile.contact.location

    # Experiences
    assert len(profile.experiences) >= 5, "Expected at least 5 verified experiences"
    for exp in profile.experiences:
        assert exp.id, "Experience missing id"
        assert exp.company, "Experience missing company"
        assert exp.title, "Experience missing title"
        assert len(exp.bullet_points) > 0, f"No bullet points in {exp.company}"
        assert isinstance(exp.technologies, list), f"Technologies should be a list in {exp.company}"

    # Projects
    assert len(profile.projects) >= 3, "Expected at least 3 projects"
    project_titles = [p.title for p in profile.projects]
    assert any("RAG" in t for t in project_titles), "RAG Chatbot project missing"
    assert any("Financial" in t for t in project_titles), "Financial Analytics project missing"

    # Education
    assert len(profile.education) >= 2, "Expected 2 education records"
    institutions = [e.institution for e in profile.education]
    assert any("Rochester" in inst for inst in institutions)
    assert any("Hamilton" in inst for inst in institutions)

    # Skills
    assert len(profile.skill_inventory) >= 4, "Expected categorized skill inventory"


def test_master_profile_validation_errors():
    """Ensure MasterProfile rejects invalid or missing fields."""
    with open("data/master_profile.json", "r", encoding="utf-8") as f:
        data = json.load(f)

    # Test missing email
    bad_data = json.loads(json.dumps(data))
    del bad_data["contact"]["email"]
    with pytest.raises(ValidationError):
        MasterProfile.model_validate(bad_data)

    # Test invalid bullet points (string instead of list)
    bad_data_2 = json.loads(json.dumps(data))
    bad_data_2["experiences"][0]["bullet_points"] = "Invalid string"
    with pytest.raises(ValidationError):
        MasterProfile.model_validate(bad_data_2)


# ==============================================================================
# 2. Voice Samples Tests
# ==============================================================================

def test_voice_samples_exist_and_non_empty():
    """Verify that writing samples exist in data/voice_samples/ for voice calibration."""
    voice_dir = Path("data/voice_samples")
    assert voice_dir.exists() and voice_dir.is_dir(), "voice_samples directory missing"

    sample_files = list(voice_dir.glob("*.txt"))
    assert len(sample_files) >= 3, f"Expected at least 3 voice samples, found {len(sample_files)}"

    for sample_file in sample_files:
        content = sample_file.read_text(encoding="utf-8").strip()
        assert len(content) > 100, f"Voice sample {sample_file.name} is too short ({len(content)} chars)"


# ==============================================================================
# 3. Job Description Criteria Schema Tests
# ==============================================================================

def test_job_description_criteria_schema():
    """Verify JobDescriptionCriteria parses and exports valid JSON schema for Ollama."""
    criteria_data = {
        "job_title": "AI/ML Systems Engineer",
        "company_name": "ModernTech AI",
        "seniority_level": "Senior",
        "summary": "Building scalable low-latency LLM serving and retrieval infrastructure.",
        "hard_skills": ["Python", "PyTorch", "FastAPI", "Vector Search", "Docker"],
        "preferred_skills": ["Ollama", "LanceDB", "Llama Guard"],
        "key_phrasing_and_keywords": ["sub-50ms latency", "RAG", "prompt orchestration"],
        "core_responsibilities": ["Design vector retrieval pipelines", "Deploy production APIs"]
    }

    criteria = JobDescriptionCriteria.model_validate(criteria_data)
    assert criteria.job_title == "AI/ML Systems Engineer"
    assert len(criteria.hard_skills) == 5

    # Check Ollama JSON schema structure
    schema = JobDescriptionCriteria.model_json_schema()
    assert schema["type"] == "object"
    assert "hard_skills" in schema["properties"]
    assert "key_phrasing_and_keywords" in schema["properties"]
    assert set(schema["required"]) >= {"job_title", "company_name", "hard_skills", "core_responsibilities"}


# ==============================================================================
# 4. Tailored Payload Schemas Tests
# ==============================================================================

def test_tailored_resume_payload_schema():
    """Verify TailoredResumePayload validates and exports valid JSON schema for Ollama."""
    contact = ContactInfo(
        full_name="Oluwayanmife Uriah Adeniran",
        email="uriahadeniran065@gmail.com",
        location="Rochester, NY"
    )

    resume = TailoredResumePayload(
        contact=contact,
        target_role="AI/ML Engineer",
        summary="Software engineer experienced in deploying ML pipelines and RAG systems.",
        skills=[
            SkillCategory(category_name="ML/AI", skills=["PyTorch", "RAG", "Transformers"]),
            SkillCategory(category_name="Languages", skills=["Python", "C#", "SQL"])
        ],
        experiences=[
            TailoredExperience(
                company="Voicify",
                title="Software Engineering Intern (AI/ML)",
                location="Rochester, NY",
                date_range="May 2024 – Aug 2025",
                bullets=["Automated bug classification saving 2–3 hours/day in manual analysis."],
                technologies=["Python", "OpenAI API", "C#"]
            )
        ],
        projects=[
            TailoredProject(
                title="RAG Chatbot",
                role="Lead Developer",
                link="https://issorientation.hamiltonlits.org/",
                bullets=["Built end-to-end RAG pipeline using Ollama and LanceDB."],
                technologies=["Ollama", "LanceDB"]
            )
        ],
        education=[
            EducationItem(
                institution="Hamilton College",
                degree="B.S.",
                field_of_study="Computer Science and Economics",
                graduation_date="May 2026"
            )
        ]
    )

    assert resume.target_role == "AI/ML Engineer"
    schema = TailoredResumePayload.model_json_schema()
    assert "properties" in schema
    assert "experiences" in schema["properties"]
    assert "summary" in schema["properties"]


def test_tailored_cover_letter_payload_schema():
    """Verify TailoredCoverLetterPayload validates and exports valid JSON schema for Ollama."""
    letter = TailoredCoverLetterPayload(
        candidate_name="Oluwayanmife Uriah Adeniran",
        candidate_contact_line="Rochester, NY | 315-790-2853 | uriahadeniran065@gmail.com",
        date_str="October 7, 2025",
        recipient_title="Hiring Committee",
        company_name="Microsoft Corporation",
        job_title="Software Engineer, Cloud Consoles",
        salutation="Dear Hiring Committee,",
        opening_hook="I am writing to apply for the Software Engineer position on the Cloud Consoles team.",
        body_paragraphs=[
            "At Hamilton, I built full-stack applications with AI image processing...",
            "During my internship at Voicify, I automated call labeling and shipped backend APIs in C#..."
        ],
        closing_paragraph="I welcome the opportunity to discuss how my system design skills align with Microsoft.",
        sign_off="Sincerely,"
    )

    assert letter.company_name == "Microsoft Corporation"
    schema = TailoredCoverLetterPayload.model_json_schema()
    assert "opening_hook" in schema["properties"]
    assert "body_paragraphs" in schema["properties"]
    assert "closing_paragraph" in schema["properties"]

