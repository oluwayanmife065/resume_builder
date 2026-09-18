"""Unit tests for src/extractor.py data loading functions."""

import json
from pathlib import Path
import pytest

from src.extractor import load_master_profile, load_job_description, load_voice_samples
from src.schema import MasterProfile


def test_load_master_profile_success():
    """Verify load_master_profile reads and validates data/master_profile.json."""
    profile = load_master_profile("data/master_profile.json")
    assert isinstance(profile, MasterProfile)
    assert profile.contact.full_name == "Oluwayanmife Uriah Adeniran"
    assert len(profile.experiences) >= 5
    assert len(profile.projects) >= 3


def test_load_master_profile_file_not_found(tmp_path: Path):
    """Verify load_master_profile raises FileNotFoundError for missing file."""
    missing_file = tmp_path / "non_existent.json"
    with pytest.raises(FileNotFoundError):
        load_master_profile(missing_file)


def test_load_master_profile_malformed_json(tmp_path: Path):
    """Verify load_master_profile raises ValueError on corrupted JSON."""
    bad_json_file = tmp_path / "corrupt.json"
    bad_json_file.write_text("{ unquoted_key: missing_bracket ", encoding="utf-8")
    with pytest.raises(ValueError, match="Malformed JSON"):
        load_master_profile(bad_json_file)


def test_load_job_description_success():
    """Verify load_job_description loads text and strips whitespace."""
    jd_text = load_job_description("data/target_jd.txt")
    assert isinstance(jd_text, str)
    assert len(jd_text) > 200
    assert "AI/ML Software Engineer" in jd_text


def test_load_job_description_missing_file(tmp_path: Path):
    """Verify load_job_description raises FileNotFoundError when JD missing."""
    missing_jd = tmp_path / "no_such_jd.txt"
    with pytest.raises(FileNotFoundError):
        load_job_description(missing_jd)


def test_load_job_description_empty_file(tmp_path: Path):
    """Verify load_job_description raises ValueError if file is empty."""
    empty_jd = tmp_path / "empty_jd.txt"
    empty_jd.write_text("   \n\n   ", encoding="utf-8")
    with pytest.raises(ValueError, match="is empty"):
        load_job_description(empty_jd)


def test_load_voice_samples_success():
    """Verify load_voice_samples loads all writing sample files."""
    samples = load_voice_samples("data/voice_samples")
    assert isinstance(samples, list)
    assert len(samples) >= 3
    for s in samples:
        assert isinstance(s, str)
        assert len(s) > 50


def test_load_voice_samples_missing_directory(tmp_path: Path):
    """Verify load_voice_samples returns empty list if directory does not exist."""
    missing_dir = tmp_path / "no_such_dir"
    samples = load_voice_samples(missing_dir)
    assert samples == []

