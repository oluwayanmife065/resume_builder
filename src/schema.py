"""Data schemas and Pydantic models for the career agent.

Enforces structural boundaries for:
1. Master Profile data (immutable ground truth).
"""

from __future__ import annotations
from typing import List, Optional
from pydantic import BaseModel, Field


# ==============================================================================
# 1. Master Profile Schemas (Ground Truth)
# ==============================================================================

class ContactInfo(BaseModel):
    """Personal and professional contact coordinates."""
    full_name: str = Field(..., description="Candidate's full legal or preferred name")
    email: str = Field(..., description="Professional contact email")
    phone: Optional[str] = Field(None, description="Phone number with country code")
    location: str = Field(..., description="City, State/Province, Country")
    linkedin_url: Optional[str] = Field(None, description="LinkedIn profile URL")
    github_url: Optional[str] = Field(None, description="GitHub profile URL")
    portfolio_url: Optional[str] = Field(None, description="Personal website or portfolio URL")


class ExperienceItem(BaseModel):
    """A verified professional role from the candidate's master history."""
    id: str = Field(..., description="Unique identifier (e.g. 'exp_apex_2022')")
    company: str = Field(..., description="Company or organization name")
    title: str = Field(..., description="Official job title")
    location: str = Field(..., description="Office location or 'Remote'")
    start_date: str = Field(..., description="Start date (e.g. 'Jan 2022')")
    end_date: str = Field(..., description="End date (e.g. 'Present' or 'Dec 2023')")
    is_current: bool = Field(False, description="Whether this is candidate's current role")
    bullet_points: List[str] = Field(
        ...,
        description="Factual achievements, metrics, and outcomes"
    )
    technologies: List[str] = Field(
        default_factory=list,
        description="Tools, languages, and frameworks used in this role"
    )


class EducationItem(BaseModel):
    """Academic credentials and degree records."""
    institution: str = Field(..., description="University or educational institution")
    degree: str = Field(..., description="Degree type (e.g. B.S., M.S.)")
    field_of_study: str = Field(..., description="Major or area of concentration")
    graduation_date: str = Field(..., description="Graduation month/year or expected date")
    location: Optional[str] = Field(None, description="Campus location")
    gpa: Optional[str] = Field(None, description="GPA if applicable")
    highlights: List[str] = Field(
        default_factory=list,
        description="Honors, thesis topic, relevant coursework, or leadership"
    )


class ProjectItem(BaseModel):
    """Notable engineering or research projects."""
    id: str = Field(..., description="Unique identifier for the project")
    title: str = Field(..., description="Project name")
    role: Optional[str] = Field(None, description="Candidate's role (e.g. 'Creator', 'Lead')")
    link: Optional[str] = Field(None, description="GitHub repository or live URL")
    bullet_points: List[str] = Field(
        ...,
        description="Factual accomplishments and architecture decisions"
    )
    technologies: List[str] = Field(
        default_factory=list,
        description="Technologies used in the project"
    )


class SkillCategory(BaseModel):
    """Grouped skill classifications."""
    category_name: str = Field(..., description="Category name (e.g. 'Languages', 'Databases')")
    skills: List[str] = Field(..., description="Specific verified skills")


class MasterProfile(BaseModel):
    """The immutable source of truth for candidate's professional career."""
    contact: ContactInfo
    summary: Optional[str] = Field(
        None,
        description="Candidate's baseline professional summary"
    )
    target_roles: List[str] = Field(
        default_factory=list,
        description="Roles the candidate is targeting"
    )
    experiences: List[ExperienceItem] = Field(
        ...,
        description="Chronological work history"
    )
    projects: List[ProjectItem] = Field(
        default_factory=list,
        description="Selected personal, open-source, or research projects"
    )
    education: List[EducationItem] = Field(
        ...,
        description="Academic background"
    )
    skill_inventory: List[SkillCategory] = Field(
        ...,
        description="Verified technical and domain skills"
    )
    certifications: List[str] = Field(
        default_factory=list,
        description="Industry certifications"
    )


# ==============================================================================
# 2. Extracted Job Description Criteria Schema
# ==============================================================================

class JobDescriptionCriteria(BaseModel):
    """Structured extraction of target job requirements and ATS scoring signals."""
    job_title: str = Field(..., description="Target position title")
    company_name: str = Field(..., description="Target company or organization")
    seniority_level: Optional[str] = Field(None, description="Seniority level (e.g. 'Senior', 'Staff', 'Mid')")
    summary: str = Field(..., description="Concise synopsis of the core mission for this role")
    hard_skills: List[str] = Field(
        ...,
        description="Essential technical proficiencies, tools, languages, and frameworks"
    )
    preferred_skills: List[str] = Field(
        default_factory=list,
        description="Nice-to-have or preferred qualifications"
    )
    key_phrasing_and_keywords: List[str] = Field(
        ...,
        description="Domain-specific terminology, buzzwords, and ATS search phrases found in the JD"
    )
    core_responsibilities: List[str] = Field(
        ...,
        description="Primary day-to-day responsibilities and expected deliverables"
    )


# ==============================================================================
# 3. Tailored Application Output Schemas
# ==============================================================================

class TailoredExperience(BaseModel):
    """Experience item with bullet points tailored to the target job."""
    company: str = Field(..., description="Company name")
    title: str = Field(..., description="Job title")
    location: str = Field(..., description="Role location")
    date_range: str = Field(..., description="Formatted dates (e.g. 'May 2025 – Present')")
    bullets: List[str] = Field(
        ...,
        description=(
            "Tailored bullet points that highlight relevant achievements. "
            "STRICT FACTUAL GROUNDING: Must only draw from verified achievements in the master record. "
            "Never hallucinate new metrics, tools, or roles."
        )
    )
    technologies: List[str] = Field(
        default_factory=list,
        description="Selected technologies used in this role that match JD priorities"
    )


class TailoredProject(BaseModel):
    """Project item prioritized for relevance to target job."""
    title: str = Field(..., description="Project title")
    role: Optional[str] = Field(None, description="Candidate role")
    link: Optional[str] = Field(None, description="Live project or repository link")
    bullets: List[str] = Field(..., description="Tailored factual bullet points")
    technologies: List[str] = Field(..., description="Key tools and languages used")


class TailoredResumePayload(BaseModel):
    """Complete structured payload ready for deterministic Jinja-Typst compilation."""
    contact: ContactInfo
    target_role: str = Field(..., description="Target role headline tailored to JD")
    summary: str = Field(
        ...,
        description="2-3 sentence executive summary aligning verified experience with target role"
    )
    skills: List[SkillCategory] = Field(
        ...,
        description="Prioritized skill categories matching JD hard and preferred requirements"
    )
    experiences: List[TailoredExperience] = Field(
        ...,
        description="Selected work experiences with optimized, grounded bullet points"
    )
    projects: List[TailoredProject] = Field(
        default_factory=list,
        description="Most relevant projects demonstrating required capabilities"
    )
    education: List[EducationItem] = Field(
        ...,
        description="Educational credentials and coursework"
    )


class TailoredCoverLetterPayload(BaseModel):
    """Voice-calibrated cover letter payload with zero generic AI filler."""
    candidate_name: str = Field(..., description="Candidate's full name")
    candidate_contact_line: str = Field(..., description="Formatted single-line contact coordinates")
    date_str: str = Field(..., description="Date formatted for letter header (e.g. 'October 15, 2025')")
    recipient_title: str = Field(
        default="Hiring Committee",
        description="Addressee (e.g. 'Hiring Committee', 'Hiring Manager')"
    )
    company_name: str = Field(..., description="Target company name")
    job_title: str = Field(..., description="Target job title")
    salutation: str = Field(default="Dear Hiring Committee,", description="Formal salutation")
    opening_hook: str = Field(
        ...,
        description=(
            "Engaging first paragraph connecting candidate's authentic perspective or genuine interest "
            "to the company's technical challenge. MUST NOT use 'I am thrilled to apply' or generic filler."
        )
    )
    body_paragraphs: List[str] = Field(
        ...,
        description=(
            "2-3 paragraphs weaving verified historical achievements with the target company's challenges. "
            "Mirrors candidate's writing samples in rhythm, sentence length, and vocabulary."
        )
    )
    closing_paragraph: str = Field(
        ...,
        description="Grounded, confident closing paragraph without subservient or clichéd phrasing."
    )
    sign_off: str = Field(default="Sincerely,", description="Formal sign-off")



