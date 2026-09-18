"""Data extraction and profile loading utilities.

TODO: Implement loaders for master_profile.json, target_jd.txt, and voice samples.
Provides loaders for:
1. Master Profile JSON (validated through Pydantic MasterProfile schema).
2. Target Job Description raw text.
3. Candidate writing samples for voice/tone calibration.
"""

# Scaffold placeholder - implementation to follow
from __future__ import annotations
import json
from pathlib import Path
from typing import List, Union

from src.schema import MasterProfile


def load_master_profile(profile_path: Union[Path, str] = "data/master_profile.json") -> MasterProfile:
    """Load and validate the candidate master profile from a JSON file.

    Args:
        profile_path: Path to master_profile.json file.

    Returns:
        Validated MasterProfile Pydantic instance.

    Raises:
        FileNotFoundError: If the profile file does not exist.
        ValueError: If JSON is corrupted or fails schema validation.
    """
    path = Path(profile_path)
    if not path.exists():
        raise FileNotFoundError(f"Master profile file not found at: {path.resolve()}")

    try:
        with open(path, "r", encoding="utf-8") as f:
            raw_data = json.load(f)
    except json.JSONDecodeError as err:
        raise ValueError(f"Malformed JSON in master profile ({path}): {err}") from err

    return MasterProfile.model_validate(raw_data)


def load_job_description(jd_path: Union[Path, str] = "data/target_jd.txt") -> str:
    """Load and sanitize raw target job description text.

    Args:
        jd_path: Path to target job description text file.

    Returns:
        Cleaned job description string.

    Raises:
        FileNotFoundError: If the JD file does not exist.
        ValueError: If the JD file is empty.
    """
    path = Path(jd_path)
    if not path.exists():
        raise FileNotFoundError(f"Job description file not found at: {path.resolve()}")

    content = path.read_text(encoding="utf-8").strip()
    if not content:
        raise ValueError(f"Job description file at {path} is empty.")

    return content


def load_voice_samples(voice_dir: Union[Path, str] = "data/voice_samples") -> List[str]:
    """Ingest candidate writing samples for voice and tone calibration.

    Scans the directory for .txt and .md files, reads their contents,
    and returns a list of non-empty text samples.

    Args:
        voice_dir: Path to directory containing writing sample files.

    Returns:
        List of non-empty sample strings. Returns empty list if directory missing.
    """
    path = Path(voice_dir)
    if not path.exists() or not path.is_dir():
        return []

    samples: List[str] = []
    for extension in ("*.txt", "*.md"):
        for file_path in sorted(path.glob(extension)):
            text = file_path.read_text(encoding="utf-8").strip()
            if text:
                samples.append(text)

    return samples
