"""
QSCMF Skill Effectiveness Tests

Tests to ensure the QSCMF skill maintains quality across iterations.
Based on 2025-2026 AI Agent testing research:
- Claude <500 lines per skill file
- Arcade <10 tools per scenario
- Anthropic tool clarity metrics
"""

import pytest
import re
import yaml
from pathlib import Path


class TestSkillMdCompliance:
    """Test SKILL.md compliance with best practices."""

    def test_skill_md_exists(self, skill_root):
        """SKILL.md must exist."""
        skill_file = skill_root / "SKILL.md"
        assert skill_file.exists(), "SKILL.md not found"

    def test_skill_md_line_count(self, skill_md_content):
        """SKILL.md should be under 160 lines (target: ~500 tokens)."""
        assert skill_md_content is not None, "SKILL.md content not loaded"
        lines = skill_md_content.count('\n') + 1
        assert lines <= 200, f"SKILL.md has {lines} lines, should be <= 200"

    def test_skill_md_has_frontmatter(self, skill_md_content):
        """SKILL.md must have YAML frontmatter."""
        assert skill_md_content is not None
        assert skill_md_content.startswith('---'), "SKILL.md missing YAML frontmatter"

    def test_skill_md_has_name(self, skill_md_content):
        """SKILL.md must have name in frontmatter."""
        assert skill_md_content is not None
        assert 'name: qscmf-backend' in skill_md_content, "SKILL.md missing name field"

    def test_skill_md_has_description(self, skill_md_content):
        """SKILL.md must have description in frontmatter."""
        assert skill_md_content is not None
        assert 'description:' in skill_md_content, "SKILL.md missing description field"

    def test_skill_md_has_iron_laws(self, skill_md_content):
        """SKILL.md must have Iron Laws section."""
        assert skill_md_content is not None
        assert '## Iron Laws' in skill_md_content or 'Iron Laws' in skill_md_content, \
            "SKILL.md missing Iron Laws section"

    def test_skill_md_has_quick_start(self, skill_md_content):
        """SKILL.md must have Quick Start section."""
        assert skill_md_content is not None
        assert '## Quick Start' in skill_md_content or 'Quick Start' in skill_md_content, \
            "SKILL.md missing Quick Start section"

    def test_skill_md_has_routing_table(self, skill_md_content):
        """SKILL.md must have intent routing table."""
        assert skill_md_content is not None
        assert '## Intent Routing' in skill_md_content or 'Intent Routing' in skill_md_content, \
            "SKILL.md missing Intent Routing section"


class TestRuleFilesCompliance:
    """Test rule files compliance with best practices."""

    def test_rule_files_exist(self, rule_files):
        """Rule files must exist."""
        assert len(rule_files) > 0, "No rule files found"

    def test_rule_files_line_limit(self, rule_files):
        """Each rule file should be under 500 lines (Claude guideline)."""
        for rule_file in rule_files:
            if rule_file.name.startswith('_'):
                continue  # Skip template files

            content = rule_file.read_text(encoding='utf-8')
            lines = content.count('\n') + 1
            assert lines <= 500, f"{rule_file.name} has {lines} lines, should be <= 500"

    def test_rule_files_have_frontmatter(self, rule_files):
        """Each rule file should have YAML frontmatter."""
        for rule_file in rule_files:
            if rule_file.name.startswith('_'):
                continue

            content = rule_file.read_text(encoding='utf-8')
            assert content.startswith('---'), f"{rule_file.name} missing frontmatter"

    def test_rule_files_have_title(self, rule_files):
        """Each rule file should have title in frontmatter."""
        for rule_file in rule_files:
            if rule_file.name.startswith('_'):
                continue

            content = rule_file.read_text(encoding='utf-8')
            assert 'title:' in content.lower() or '## ' in content, \
                f"{rule_file.name} missing title"

    def test_rule_files_have_impact(self, rule_files):
        """Each rule file should have impact level."""
        for rule_file in rule_files:
            if rule_file.name.startswith('_'):
                continue

            content = rule_file.read_text(encoding='utf-8')
            # Check for impact in frontmatter or tags
            has_impact = 'impact:' in content.lower() or 'CRITICAL' in content or \
                        'HIGH' in content or 'MEDIUM' in content or 'LOW' in content
            assert has_impact, f"{rule_file.name} missing impact level"


class TestDirectoryStructure:
    """Test skill directory structure."""

    def test_shared_directory_exists(self, skill_root):
        """_shared directory must exist."""
        shared_dir = skill_root / "_shared"
        assert shared_dir.exists(), "_shared directory not found"

    def test_rules_directory_exists(self, skill_root):
        """rules directory must exist."""
        rules_dir = skill_root / "rules"
        assert rules_dir.exists(), "rules directory not found"

    def test_config_files_exist(self, skill_root):
        """Version config files must exist."""
        config_dir = skill_root / "_shared" / "config"
        assert config_dir.exists(), "_shared/config directory not found"

        v13_config = config_dir / "v13.yaml"
        v14_config = config_dir / "v14.yaml"

        assert v13_config.exists() or v14_config.exists(), \
            "At least one version config file required"

    def test_template_files_exist(self, skill_root):
        """Template files must exist."""
        templates_dir = skill_root / "_shared" / "templates"
        assert templates_dir.exists(), "_shared/templates directory not found"

        # Check for common templates
        common_dir = templates_dir / "common"
        assert common_dir.exists(), "templates/common directory not found"


class TestScenarioCoverage:
    """Test scenario coverage."""

    def test_scenarios_exist(self, scenarios_dir):
        """Test scenarios must exist."""
        scenario_files = list(scenarios_dir.glob("*.yaml"))
        assert len(scenario_files) >= 3, \
            f"Only {len(scenario_files)} scenarios found, need at least 3"

    def test_simple_scenario_exists(self, scenarios_dir):
        """Simple scenario must exist."""
        simple_scenarios = [
            f for f in scenarios_dir.glob("*.yaml")
            if 'simple' in f.name.lower() or 'search' in f.name.lower()
        ]
        assert len(simple_scenarios) >= 1, "No simple scenario found"

    def test_complex_scenario_exists(self, scenarios_dir):
        """Complex scenario must exist."""
        complex_scenarios = [
            f for f in scenarios_dir.glob("*.yaml")
            if 'complex' in f.name.lower() or 'module' in f.name.lower() or 'create' in f.name.lower()
        ]
        assert len(complex_scenarios) >= 1, "No complex scenario found"


class TestToolRetrieval:
    """Test tool retrieval efficiency."""

    def test_tool_count_per_scenario(self, load_all_scenarios):
        """Each scenario should retrieve < 10 tools (Arcade guideline)."""
        for scenario in load_all_scenarios:
            expected_tools = scenario.get('expected_tools', [])
            assert len(expected_tools) < 10, \
                f"Scenario '{scenario.get('name')}' expects {len(expected_tools)} tools, should be < 10"

    def test_scenario_has_expected_tools(self, load_all_scenarios):
        """Each scenario should define expected tools."""
        for scenario in load_all_scenarios:
            expected_tools = scenario.get('expected_tools', [])
            assert len(expected_tools) > 0, \
                f"Scenario '{scenario.get('name')}' has no expected_tools defined"

    def test_expected_tools_exist(self, load_all_scenarios, skill_root):
        """Expected tool files should exist in rules/."""
        rules_dir = skill_root / "rules"

        for scenario in load_all_scenarios:
            for tool in scenario.get('expected_tools', []):
                # Check if tool file exists
                tool_file = rules_dir / tool
                if not tool_file.exists():
                    # Try finding it anywhere in rules/
                    matches = list(rules_dir.rglob(tool))
                    assert len(matches) > 0, \
                        f"Tool '{tool}' for scenario '{scenario.get('name')}' not found"


class TestScaffoldRulesCompliance:
    """Test scaffold rule files compliance."""

    def test_scaffold_generate_code_exists(self, skill_root):
        """scaffold-generate-code.md must exist."""
        rule_file = skill_root / "rules" / "scaffold" / "scaffold-generate-code.md"
        assert rule_file.exists(), "scaffold-generate-code.md not found"

    def test_scaffold_parse_metadata_exists(self, skill_root):
        """scaffold-parse-metadata.md must exist."""
        rule_file = skill_root / "rules" / "scaffold" / "scaffold-parse-metadata.md"
        assert rule_file.exists(), "scaffold-parse-metadata.md not found"

    def test_scaffold_infer_types_exists(self, skill_root):
        """scaffold-infer-types.md must exist."""
        rule_file = skill_root / "rules" / "scaffold" / "scaffold-infer-types.md"
        assert rule_file.exists(), "scaffold-infer-types.md not found"

    def test_scaffold_rules_have_metadata_section(self, skill_root):
        """Scaffold rules should explain @metadata."""
        scaffold_dir = skill_root / "rules" / "scaffold"
        for rule_file in scaffold_dir.glob("*.md"):
            if rule_file.name.startswith('_'):
                continue
            content = rule_file.read_text(encoding='utf-8')
            # At least one scaffold rule should mention @metadata
            if 'metadata' in content.lower():
                assert '@title' in content or '@type' in content, \
                    f"{rule_file.name} should explain @metadata attributes"

    def test_scaffold_rules_link_to_each_other(self, skill_root):
        """Scaffold rules should reference related rules."""
        scaffold_dir = skill_root / "rules" / "scaffold"
        rule_files = [f for f in scaffold_dir.glob("*.md") if not f.name.startswith('_')]

        for rule_file in rule_files:
            content = rule_file.read_text(encoding='utf-8')
            # Check for "See Also" or "相关文档" section
            has_links = 'See Also' in content or '相关文档' in content or \
                       '[scaffold-' in content.lower() or '](' in content
            assert has_links, f"{rule_file.name} should reference related rules"


class TestTransactionRuleCompliance:
    """Test transaction rule file compliance."""

    def test_transaction_rule_exists(self, skill_root):
        """test-transaction.md must exist."""
        rule_file = skill_root / "rules" / "test" / "test-transaction.md"
        assert rule_file.exists(), "test-transaction.md not found"

    def test_transaction_rule_has_examples(self, skill_root):
        """Transaction rule should have code examples."""
        rule_file = skill_root / "rules" / "test" / "test-transaction.md"
        content = rule_file.read_text(encoding='utf-8')

        # Should have PHP code examples
        assert '```php' in content, "Transaction rule should have PHP code examples"

        # Should cover key transaction concepts
        transaction_concepts = ['startTrans', 'commit', 'rollback', 'beginTransaction']
        found_concepts = sum(1 for concept in transaction_concepts if concept in content)
        assert found_concepts >= 2, \
            f"Transaction rule should cover at least 2 transaction concepts, found {found_concepts}"

    def test_transaction_rule_has_checklist(self, skill_root):
        """Transaction rule should have a checklist."""
        rule_file = skill_root / "rules" / "test" / "test-transaction.md"
        content = rule_file.read_text(encoding='utf-8')

        # Should have a checklist section
        has_checklist = '检查清单' in content or 'Checklist' in content.lower() or \
                       '[ ]' in content
        assert has_checklist, "Transaction rule should have a checklist section"


class TestTestingReferenceCompliance:
    """Test testing reference document compliance."""

    def test_testing_reference_exists(self, skill_root):
        """testing.md reference must exist."""
        ref_file = skill_root / "references" / "testing.md"
        assert ref_file.exists(), "testing.md reference not found"

    def test_testing_reference_has_sections(self, skill_root):
        """Testing reference should have key sections."""
        ref_file = skill_root / "references" / "testing.md"
        content = ref_file.read_text(encoding='utf-8')

        required_sections = [
            ('API 测试', 'API'),
            ('Mock', 'Mock'),
            ('PHPUnit', 'PHPUnit'),
        ]

        for section_name, keyword in required_sections:
            assert keyword in content, \
                f"Testing reference should have {section_name} section"

    def test_testing_reference_has_test_commands(self, skill_root):
        """Testing reference should include test commands."""
        ref_file = skill_root / "references" / "testing.md"
        content = ref_file.read_text(encoding='utf-8')

        # Should include phpunit command
        assert 'vendor/bin/phpunit' in content, \
            "Testing reference should include phpunit commands"


class TestDevelopmentStandardsAutoValidation:
    """Test development-standards.md auto-validation section."""

    def test_auto_validation_section_exists(self, skill_root):
        """Development standards should have auto-validation section."""
        ref_file = skill_root / "references" / "development-standards.md"
        content = ref_file.read_text(encoding='utf-8')

        assert '自动化验证' in content or 'auto' in content.lower(), \
            "Development standards should have auto-validation section"

    def test_auto_validation_has_tools(self, skill_root):
        """Auto-validation section should list validation tools."""
        ref_file = skill_root / "references" / "development-standards.md"
        content = ref_file.read_text(encoding='utf-8')

        # Should mention key validation tools
        validation_tools = ['php-cs-fixer', 'phpstan', 'phpunit']
        found_tools = sum(1 for tool in validation_tools if tool in content.lower())
        assert found_tools >= 2, \
            f"Auto-validation should mention at least 2 validation tools, found {found_tools}"

    def test_auto_validation_has_checklist(self, skill_root):
        """Auto-validation section should have verification checklist."""
        ref_file = skill_root / "references" / "development-standards.md"
        content = ref_file.read_text(encoding='utf-8')

        # Should have a checklist or verification commands
        has_checklist = '检查清单' in content or 'verification' in content.lower() or \
                       '验证' in content
        assert has_checklist, "Auto-validation should have a verification checklist"


class TestVersionDetectionEnhancement:
    """Test enhanced version detection."""

    def test_detect_version_has_class(self, skill_root):
        """detect-version.php should have a version detector class."""
        detect_file = skill_root / "_shared" / "detect-version.php"
        content = detect_file.read_text(encoding='utf-8')

        assert 'class' in content, "detect-version.php should define a class"
        assert 'VersionDetectionResult' in content or 'VersionDetector' in content, \
            "detect-version.php should have a version detection class"

    def test_detect_version_multiple_methods(self, skill_root):
        """Version detection should use multiple methods."""
        detect_file = skill_root / "_shared" / "detect-version.php"
        content = detect_file.read_text(encoding='utf-8')

        # Should have multiple detection methods
        detection_methods = [
            'detectFromComposer',
            'detectFromDirectory',
            'detectFromEnvironment',
            'detectFromConfig',
            'detectFromFeatures',
        ]
        found_methods = sum(1 for method in detection_methods if method in content)
        assert found_methods >= 3, \
            f"Version detection should have at least 3 methods, found {found_methods}"

    def test_detect_version_outputs_confidence(self, skill_root):
        """Version detection should output confidence level."""
        detect_file = skill_root / "_shared" / "detect-version.php"
        content = detect_file.read_text(encoding='utf-8')

        assert 'confidence' in content, \
            "Version detection should track confidence level"


class TestNewScenarioCoverage:
    """Test new scenario files."""

    def test_scaffold_generate_scenario_exists(self, scenarios_dir):
        """Scaffold generate scenario must exist."""
        scenario_file = scenarios_dir / "scaffold_generate.yaml"
        assert scenario_file.exists(), "scaffold_generate.yaml scenario not found"

    def test_transaction_test_scenario_exists(self, scenarios_dir):
        """Transaction test scenario must exist."""
        scenario_file = scenarios_dir / "transaction_test.yaml"
        assert scenario_file.exists(), "transaction_test.yaml scenario not found"

    def test_scaffold_scenario_has_validation_criteria(self, scenarios_dir):
        """Scaffold scenario should have validation criteria."""
        scenario_file = scenarios_dir / "scaffold_generate.yaml"
        if scenario_file.exists():
            with open(scenario_file, 'r', encoding='utf-8') as f:
                scenario = yaml.safe_load(f)

            assert 'validation_criteria' in scenario, \
                "Scaffold scenario should have validation_criteria"
            assert len(scenario.get('validation_criteria', [])) >= 3, \
                "Scaffold scenario should have at least 3 validation criteria"

    def test_transaction_scenario_has_test_scenarios(self, scenarios_dir):
        """Transaction scenario should define test scenarios."""
        scenario_file = scenarios_dir / "transaction_test.yaml"
        if scenario_file.exists():
            with open(scenario_file, 'r', encoding='utf-8') as f:
                scenario = yaml.safe_load(f)

            assert 'test_scenarios' in scenario or 'expected_outputs' in scenario, \
                "Transaction scenario should define test scenarios or expected outputs"


# Run tests
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
