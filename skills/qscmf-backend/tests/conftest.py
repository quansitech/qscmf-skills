"""
Pytest configuration for QSCMF Skill Testing

This module provides fixtures and configuration for testing the QSCMF skill effectiveness.
"""

import pytest
import yaml
import json
from pathlib import Path


# Base paths
SKILL_ROOT = Path(__file__).parent.parent
FIXTURES_DIR = SKILL_ROOT / "tests" / "fixtures"
RESULTS_DIR = SKILL_ROOT / "tests" / "results"
SCENARIOS_DIR = FIXTURES_DIR / "scenarios"


@pytest.fixture
def skill_root():
    """Return the skill root directory."""
    return SKILL_ROOT


@pytest.fixture
def fixtures_dir():
    """Return the fixtures directory."""
    return FIXTURES_DIR


@pytest.fixture
def results_dir():
    """Return the results directory."""
    return RESULTS_DIR


@pytest.fixture
def scenarios_dir():
    """Return the scenarios directory."""
    return SCENARIOS_DIR


@pytest.fixture
def load_scenario():
    """Factory fixture to load a scenario by name."""
    def _load(name: str) -> dict:
        scenario_file = SCENARIOS_DIR / f"{name}.yaml"
        if not scenario_file.exists():
            pytest.fail(f"Scenario not found: {name}")

        with open(scenario_file, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    return _load


@pytest.fixture
def load_all_scenarios():
    """Load all test scenarios."""
    scenarios = []
    for scenario_file in SCENARIOS_DIR.glob("*.yaml"):
        with open(scenario_file, 'r', encoding='utf-8') as f:
            scenario = yaml.safe_load(f)
            scenario['_file'] = str(scenario_file)
            scenarios.append(scenario)
    return scenarios


@pytest.fixture
def baseline_results():
    """Load baseline test results."""
    baseline_file = RESULTS_DIR / "baseline.json"
    if baseline_file.exists():
        with open(baseline_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    return None


@pytest.fixture
def skill_md_content(skill_root):
    """Load SKILL.md content."""
    skill_file = skill_root / "SKILL.md"
    if skill_file.exists():
        with open(skill_file, 'r', encoding='utf-8') as f:
            return f.read()
    return None


@pytest.fixture
def rule_files(skill_root):
    """Get all rule files."""
    rules_dir = skill_root / "rules"
    return list(rules_dir.rglob("*.md"))


def pytest_configure(config):
    """Configure custom markers."""
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests"
    )
    config.addinivalue_line(
        "markers", "regression: marks tests as regression tests"
    )
