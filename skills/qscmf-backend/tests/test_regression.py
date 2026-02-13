"""
QSCMF Skill Regression Tests

Ensures skill iterations don't break existing functionality.
Based on Agentic QE framework principles:
- Test selection algorithm
- Impact analysis
- Risk-based regression
- Continuous regression

Reference: https://github.com/proffesor-for-testing/agentic-qe
"""

import pytest
import json
from datetime import datetime
from pathlib import Path


class TestBaselinePreserved:
    """Test that baseline results are preserved or improved."""

    @pytest.fixture
    def current_metrics(self, skill_root, rule_files):
        """Calculate current metrics."""
        # Calculate SKILL.md metrics
        skill_file = skill_root / "SKILL.md"
        skill_content = skill_file.read_text(encoding='utf-8') if skill_file.exists() else ""
        skill_lines = skill_content.count('\n') + 1

        # Calculate rule file metrics
        rule_count = len([f for f in rule_files if not f.name.startswith('_')])
        avg_rule_lines = 0
        if rule_count > 0:
            total_lines = sum(
                f.read_text(encoding='utf-8').count('\n') + 1
                for f in rule_files if not f.name.startswith('_')
            )
            avg_rule_lines = total_lines / rule_count

        return {
            'skill_md_lines': skill_lines,
            'rule_file_count': rule_count,
            'avg_rule_lines': avg_rule_lines,
            'timestamp': datetime.now().isoformat()
        }

    def test_skill_md_lines_not_increased(self, current_metrics, baseline_results):
        """SKILL.md line count should not increase significantly."""
        if baseline_results is None:
            pytest.skip("No baseline results found")

        current_lines = current_metrics['skill_md_lines']
        baseline_lines = baseline_results.get('skill_md_lines', current_lines)

        # Allow 10% increase
        max_allowed = baseline_lines * 1.1
        assert current_lines <= max_allowed, \
            f"SKILL.md lines increased from {baseline_lines} to {current_lines} (>10%)"

    def test_rule_count_maintained(self, current_metrics, baseline_results):
        """Rule file count should be maintained or increased."""
        if baseline_results is None:
            pytest.skip("No baseline results found")

        current_count = current_metrics['rule_file_count']
        baseline_count = baseline_results.get('rule_file_count', current_count)

        assert current_count >= baseline_count, \
            f"Rule file count decreased from {baseline_count} to {current_count}"


class TestClaudeGuidelinesCompliance:
    """Test compliance with Claude skill guidelines."""

    def test_skill_md_under_500_lines(self, skill_md_content):
        """SKILL.md should be under 500 lines."""
        assert skill_md_content is not None
        lines = skill_md_content.count('\n') + 1
        assert lines <= 500, f"SKILL.md has {lines} lines (Claude limit: 500)"

    def test_rule_files_under_500_lines(self, rule_files):
        """Each rule file should be under 500 lines."""
        for rule_file in rule_files:
            if rule_file.name.startswith('_'):
                continue

            content = rule_file.read_text(encoding='utf-8')
            lines = content.count('\n') + 1
            assert lines <= 500, \
                f"{rule_file.name} has {lines} lines (Claude limit: 500)"


class TestArcadeGuidelinesCompliance:
    """Test compliance with Arcade skill guidelines."""

    def test_scenario_tool_count(self, load_all_scenarios):
        """Each scenario should reference < 10 tools."""
        for scenario in load_all_scenarios:
            tool_count = len(scenario.get('expected_tools', []))
            assert tool_count < 10, \
                f"Scenario '{scenario.get('name')}' references {tool_count} tools (Arcade limit: 10)"

    def test_routing_table_entries(self, skill_md_content):
        """Routing table should have reasonable number of entries."""
        assert skill_md_content is not None

        # Count table rows (lines with | character)
        table_rows = [l for l in skill_md_content.split('\n') if '|' in l and not l.strip().startswith('#')]
        # Filter out header separators
        data_rows = [r for r in table_rows if '---' not in r]

        assert len(data_rows) < 50, \
            f"Routing table has {len(data_rows)} entries, consider splitting"


class TestAnthropicToolClarity:
    """Test tool selection clarity (Anthropic metrics)."""

    def test_scenarios_have_complexity_rating(self, load_all_scenarios):
        """Each scenario should have complexity rating."""
        for scenario in load_all_scenarios:
            complexity = scenario.get('complexity')
            assert complexity in ['simple', 'medium', 'complex'], \
                f"Scenario '{scenario.get('name')}' missing valid complexity rating"

    def test_scenarios_have_max_tokens(self, load_all_scenarios):
        """Each scenario should have max_tokens limit."""
        for scenario in load_all_scenarios:
            max_tokens = scenario.get('metrics', {}).get('max_tokens')
            assert max_tokens is not None, \
                f"Scenario '{scenario.get('name')}' missing max_tokens in metrics"
            assert max_tokens > 0, \
                f"Scenario '{scenario.get('name')}' has invalid max_tokens: {max_tokens}"

    def test_quick_start_examples_present(self, skill_md_content):
        """Quick Start section should have code examples."""
        assert skill_md_content is not None

        # Find Quick Start section
        quick_start_match = re.search(
            r'## Quick Start.*?(?=##|\Z)',
            skill_md_content,
            re.DOTALL | re.IGNORECASE
        )

        if quick_start_match:
            quick_start = quick_start_match.group(0)
            # Should have code blocks
            assert '```' in quick_start, \
                "Quick Start section should have code examples"


class TestVersionSupport:
    """Test version support functionality."""

    def test_v13_config_exists(self, skill_root):
        """v13 config file should exist."""
        config_file = skill_root / "_shared" / "config" / "v13.yaml"
        assert config_file.exists(), "v13.yaml config not found"

    def test_v14_config_exists(self, skill_root):
        """v14 config file should exist."""
        config_file = skill_root / "_shared" / "config" / "v14.yaml"
        assert config_file.exists(), "v14.yaml config not found"

    def test_version_config_structure(self, skill_root):
        """Version config should have required fields."""
        import yaml

        for version in ['v13', 'v14']:
            config_file = skill_root / "_shared" / "config" / f"{version}.yaml"
            if config_file.exists():
                with open(config_file, 'r') as f:
                    config = yaml.safe_load(f)

                assert 'version' in config, f"{version} config missing 'version'"
                assert 'php_requirement' in config, f"{version} config missing 'php_requirement'"


class TestFileIntegrity:
    """Test file integrity and structure."""

    def test_no_broken_links_in_skill_md(self, skill_md_content, skill_root):
        """SKILL.md should not have broken internal links."""
        assert skill_md_content is not None

        # Find all markdown links
        link_pattern = r'\[([^\]]+)\]\(([^)]+)\)'
        links = re.findall(link_pattern, skill_md_content)

        for text, link in links:
            # Only check internal links to rules/
            if link.startswith('rules/'):
                target = skill_root / link
                assert target.exists(), f"Broken link in SKILL.md: {link}"

    def test_rule_files_in_correct_directories(self, rule_files, skill_root):
        """Rule files should be in correct category directories."""
        valid_categories = [
            'workflow', 'scaffold', 'crud', 'api', 'test', 'pattern'
        ]

        for rule_file in rule_files:
            if rule_file.name.startswith('_'):
                continue

            # Get parent directory name
            parent = rule_file.parent.name
            assert parent in valid_categories, \
                f"{rule_file.name} in invalid category: {parent}"


def create_baseline(skill_root, rule_files):
    """Create baseline results file."""
    results_dir = skill_root / "tests" / "results"
    results_dir.mkdir(parents=True, exist_ok=True)

    skill_file = skill_root / "SKILL.md"
    skill_content = skill_file.read_text(encoding='utf-8') if skill_file.exists() else ""

    rule_count = len([f for f in rule_files if not f.name.startswith('_')])

    baseline = {
        'skill_md_lines': skill_content.count('\n') + 1,
        'rule_file_count': rule_count,
        'created_at': datetime.now().isoformat(),
        'version': '1.0'
    }

    baseline_file = results_dir / "baseline.json"
    with open(baseline_file, 'w') as f:
        json.dump(baseline, f, indent=2)

    return baseline


# Required for broken link check
import re


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
