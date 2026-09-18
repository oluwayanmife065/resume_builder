"""Ollama LLM generator with native Pydantic schema enforcement and voice calibration."""

from __future__ import annotations
import json
from typing import List, Optional, Union
import ollama

from src.schema import (
    MasterProfile,
    JobDescriptionCriteria,
    TailoredResumePayload,
    TailoredCoverLetterPayload,
)


class CareerAgentGenerator:
    """Orchestrates structured LLM generations via Ollama with strict factual constraints."""

    def __init__(self, model_name: str = "qwen2.5:14b", host: Optional[str] = None):
        self.model_name = model_name
        self.client = ollama.Client(host=host) if host else ollama

    def extract_jd_criteria(self, jd_text: str) -> JobDescriptionCriteria:
        """Extract hard skills, qualifications, and ATS domain phrasing from raw job description."""
        system_prompt = (
            "You are an expert technical talent analyst and ATS optimizer. "
            "Analyze the target job description and extract critical evaluation criteria. "
            "Identify required hard skills, preferred competencies, key ATS search phrases, "
            "and core responsibilities with precision."
        )
        user_prompt = f"TARGET JOB DESCRIPTION:\n\n{jd_text}"

        response = self.client.chat(
            model=self.model_name,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            format=JobDescriptionCriteria.model_json_schema(),
            options={"temperature": 0.1},
        )

        content = response["message"]["content"]
        return JobDescriptionCriteria.model_validate_json(content)

    def generate_tailored_resume(
        self,
        master_profile: MasterProfile,
        jd_criteria: JobDescriptionCriteria,
    ) -> TailoredResumePayload:
        """Tailor master profile bullets and summary to match JD criteria.

        STRICT FACTUAL GROUNDING RULES:
        - NEVER fabricate or extrapolate metrics, numbers, or tools not present in the master profile.
        - Frame and prioritize verified accomplishments using target domain vocabulary from the JD.
        - Omit irrelevant roles or deprioritize experiences that do not speak to the core mission.
        """
        system_prompt = (
            "You are a rigorous, privacy-first career strategist. Your directive is to align a candidate's "
            "verified professional history with a target job description.\n\n"
            "CRITICAL CONSTRAINTS - STRICT FACTUAL GROUNDING:\n"
            "1. You MUST ONLY use metrics, achievements, systems, and technologies explicitly present in the MASTER PROFILE.\n"
            "2. NEVER invent or extrapolate unverified roles, tools, projects, or statistics.\n"
            "3. Optimize ATS alignment by adopting phrasing, keywords, and synonyms from the JOB CRITERIA "
            "WITHOUT modifying the underlying factual reality.\n"
            "4. Eliminate corporate fluff, buzzwords, and vague passive voice. Use crisp, high-impact action verbs.\n"
            "5. Structure the summary in 2-3 factual, high-signal sentences."
        )

        user_prompt = (
            f"TARGET JOB CRITERIA:\n"
            f"Title: {jd_criteria.job_title} at {jd_criteria.company_name}\n"
            f"Hard Skills: {', '.join(jd_criteria.hard_skills)}\n"
            f"Preferred Skills: {', '.join(jd_criteria.preferred_skills)}\n"
            f"Key Phrasing: {', '.join(jd_criteria.key_phrasing_and_keywords)}\n"
            f"Responsibilities:\n" + "\n".join(f"- {r}" for r in jd_criteria.core_responsibilities) + "\n\n"
            f"MASTER CANDIDATE PROFILE (GROUND TRUTH):\n"
            f"{master_profile.model_dump_json(indent=2)}"
        )

        response = self.client.chat(
            model=self.model_name,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            format=TailoredResumePayload.model_json_schema(),
            options={"temperature": 0.2},
        )

        content = response["message"]["content"]
        return TailoredResumePayload.model_validate_json(content)

    def generate_tailored_cover_letter(
        self,
        master_profile: MasterProfile,
        jd_criteria: JobDescriptionCriteria,
        voice_samples: List[str],
    ) -> TailoredCoverLetterPayload:
        """Synthesize an authentic cover letter mirroring candidate's tone, rhythm, and technical cadence.

        VOICE CALIBRATION & CLICHÉ ELIMINATION:
        - Ingests raw writing samples to match vocabulary, sentence lengths, and voice.
        - STRICTLY BANS: 'I am thrilled to apply', 'spearheaded', 'passionate about', 'dynamic', 'synergy'.
        - Bridges verified technical feats to the employer's domain problems.
        """
        samples_formatted = "\n\n---\n\n".join(
            f"WRITING SAMPLE {idx + 1}:\n{sample}" for idx, sample in enumerate(voice_samples)
        )

        system_prompt = (
            "You are an authentic technical ghostwriter. You write compelling, bespoke cover letters "
            "that sound like an experienced engineer speaking directly to peers.\n\n"
            "VOICE CALIBRATION RULES:\n"
            "1. Mirror the tone, rhythm, sentence lengths, and technical directness from the provided WRITING SAMPLES.\n"
            "2. ABSOLUTELY FORBIDDEN CLICHÉS: Do NOT use phrases like 'I am thrilled/excited to apply', "
            "'I am writing to express my interest', 'spearheaded', 'game-changer', 'dynamic environment', 'synergy'.\n"
            "3. Ground all statements in factual achievements from the MASTER PROFILE.\n"
            "4. Opening hook must immediately address a real engineering or operational challenge the company faces.\n"
            "5. The closing must be confident, collegial, and forward-looking."
        )

        user_prompt = (
            f"TARGET ROLE & COMPANY:\n"
            f"{jd_criteria.job_title} at {jd_criteria.company_name}\n"
            f"Core Problem Domain / Responsibilities:\n" + "\n".join(f"- {r}" for r in jd_criteria.core_responsibilities) + "\n\n"
            f"CANDIDATE'S WRITING SAMPLES (MIRROR THIS VOICE & CADENCE):\n"
            f"{samples_formatted}\n\n"
            f"CANDIDATE'S VERIFIED BACKGROUND (FACTUAL BASELINE):\n"
            f"{master_profile.model_dump_json(indent=2)}"
        )

        response = self.client.chat(
            model=self.model_name,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            format=TailoredCoverLetterPayload.model_json_schema(),
            options={"temperature": 0.3},
        )

        content = response["message"]["content"]
        return TailoredCoverLetterPayload.model_validate_json(content)
