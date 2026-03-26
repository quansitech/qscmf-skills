#!/usr/bin/env python3
"""
QSCMF Skill Static Validation - MVP
零成本静态验证，不调用 LLM，无外部依赖

Usage:
    python3 test/qscmf-backend/scripts/run_static_validation.py
"""

import os
import sys
import re
from pathlib import Path
from dataclasses import dataclass
from typing import List, Optional, Dict, Any

# Colors for output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'

@dataclass
class TestResult:
    name: str
    passed: bool
    message: str
    details: Optional[str] = None

def simple_yaml_parse(content: str) -> Dict[str, Any]:
    """Very simple YAML parser for basic structures (no external deps)"""
    result = {}
    lines = content.strip().split('\n')
    current_key = None

    for line in lines:
        line = line.rstrip()
        if not line or line.startswith('#'):
            continue

        # Check for key: value
        if ':' in line:
            key, _, value = line.partition(':')
            key = key.strip()
            value = value.strip()

            if value:
                # Simple key: value
                if value.startswith('[') and value.endswith(']'):
                    # Simple list
                    items = value[1:-1].split(',')
                    result[key] = [i.strip() for i in items if i.strip()]
                elif value.isdigit():
                    result[key] = int(value)
                else:
                    result[key] = value
            else:
                current_key = key
                result[key] = {}

    return result

class StaticValidator:
    def __init__(self, base_path: Path):
        self.base_path = base_path
        self.skill_path = base_path / "skills" / "qscmf-backend"
        self.results: List[TestResult] = []

    def add_result(self, result: TestResult):
        self.results.append(result)
        status = f"{GREEN}✅ PASS{RESET}" if result.passed else f"{RED}❌ FAIL{RESET}"
        print(f"  {status} {result.name}")
        if result.details:
            print(f"         {result.details}")
        if not result.passed:
            print(f"         {YELLOW}{result.message}{RESET}")

    def test_file_exists(self, name: str, path: str) -> TestResult:
        """Test if a file exists"""
        full_path = self.skill_path / path
        exists = full_path.exists()
        return TestResult(
            name=name,
            passed=exists,
            message=f"File not found: {path}",
            details=str(full_path) if exists else None
        )

    def test_all_files_exist(self, name: str, paths: List[str]) -> TestResult:
        """Test if all files exist"""
        missing = []
        for path in paths:
            if not (self.skill_path / path).exists():
                missing.append(path)
        return TestResult(
            name=name,
            passed=len(missing) == 0,
            message=f"Missing files: {', '.join(missing)}",
            details=f"All {len(paths)} files found" if not missing else None
        )

    def test_yaml_valid(self, name: str, path: str) -> TestResult:
        """Test if YAML file is valid (basic check)"""
        full_path = self.skill_path / path
        if not full_path.exists():
            return TestResult(name=name, passed=False, message=f"File not found: {path}")
        try:
            with open(full_path, 'r', encoding='utf-8') as f:
                content = f.read()
            simple_yaml_parse(content)
            return TestResult(name=name, passed=True, message="", details=f"Valid YAML: {path}")
        except Exception as e:
            return TestResult(name=name, passed=False, message=f"YAML error: {e}")

    def test_frontmatter(self, name: str, pattern: str, required_fields: List[str]) -> TestResult:
        """Test if markdown files have valid frontmatter"""
        files = list(self.skill_path.glob(pattern))
        if not files:
            return TestResult(name=name, passed=False, message=f"No files found matching: {pattern}")

        missing_frontmatter = []
        missing_fields = []

        for file in files:
            with open(file, 'r', encoding='utf-8') as f:
                content = f.read()

            # Check for frontmatter
            if not content.startswith('---'):
                missing_frontmatter.append(file.name)
                continue

            # Extract frontmatter
            parts = content.split('---', 2)
            if len(parts) < 3:
                missing_frontmatter.append(file.name)
                continue

            try:
                fm = simple_yaml_parse(parts[1])
                for field in required_fields:
                    if field not in fm:
                        missing_fields.append(f"{file.name}: missing '{field}'")
            except Exception:
                missing_frontmatter.append(file.name)

        if missing_frontmatter or missing_fields:
            msg = []
            if missing_frontmatter:
                msg.append(f"No frontmatter: {', '.join(missing_frontmatter[:3])}")
            if missing_fields:
                msg.append(f"Missing fields: {', '.join(missing_fields[:3])}")
            return TestResult(
                name=name,
                passed=False,
                message="; ".join(msg),
                details=f"Checked {len(files)} files"
            )

        return TestResult(
            name=name,
            passed=True,
            message="",
            details=f"All {len(files)} files have valid frontmatter"
        )

    def test_file_content(self, name: str, path: str, must_contain: List[str]) -> TestResult:
        """Test if file contains required strings"""
        full_path = self.skill_path / path
        if not full_path.exists():
            return TestResult(name=name, passed=False, message=f"File not found: {path}")

        with open(full_path, 'r', encoding='utf-8') as f:
            content = f.read()

        missing = []
        for item in must_contain:
            if item not in content:
                missing.append(item)

        if missing:
            return TestResult(
                name=name,
                passed=False,
                message=f"Missing content: {', '.join(missing)}"
            )
        return TestResult(
            name=name,
            passed=True,
            message="",
            details=f"Contains all required: {', '.join(must_contain)}"
        )

    def test_skill_entry_size(self, name: str, path: str, max_lines: int) -> TestResult:
        """Test if SKILL.md entry file is within size limit"""
        full_path = self.skill_path / path
        if not full_path.exists():
            return TestResult(name=name, passed=False, message=f"File not found: {path}")

        with open(full_path, 'r', encoding='utf-8') as f:
            lines = len(f.readlines())

        if lines > max_lines:
            return TestResult(
                name=name,
                passed=False,
                message=f"File has {lines} lines, exceeds limit of {max_lines}"
            )
        return TestResult(
            name=name,
            passed=True,
            message="",
            details=f"{lines} lines (limit: {max_lines})"
        )

    def run_all_tests(self):
        """Run all static validation tests"""
        print(f"\n{BLUE}{'='*60}{RESET}")
        print(f"{BLUE}QSCMF Skill Static Validation - MVP{RESET}")
        print(f"{BLUE}{'='*60}{RESET}\n")

        # 1. Core Structure Tests
        print(f"{BLUE}[1] Core Structure Tests{RESET}")
        self.add_result(self.test_file_exists(
            "SKILL.md entry exists",
            "SKILL.md"
        ))
        self.add_result(self.test_file_exists(
            "v14 SKILL.md exists",
            "v14/SKILL.md"
        ))
        self.add_result(self.test_file_exists(
            "v13 SKILL.md exists",
            "v13/SKILL.md"
        ))

        # 2. Modes Directory Tests
        print(f"\n{BLUE}[2] Modes Directory Tests{RESET}")
        self.add_result(self.test_all_files_exist(
            "v14 modes complete",
            [
                "v14/modes/scaffold.md",
                "v14/modes/guide.md",
                "v14/modes/learn.md",
                "v14/modes/verify.md",
            ]
        ))
        self.add_result(self.test_all_files_exist(
            "v13 modes complete",
            [
                "v13/modes/scaffold.md",
                "v13/modes/guide.md",
                "v13/modes/learn.md",
            ]
        ))

        # 3. Verification System Tests
        print(f"\n{BLUE}[3] Verification System Tests{RESET}")
        self.add_result(self.test_file_exists(
            "failures.yaml exists",
            "_shared/learn/failures.yaml"
        ))
        self.add_result(self.test_yaml_valid(
            "failures.yaml valid YAML",
            "_shared/learn/failures.yaml"
        ))
        self.add_result(self.test_file_exists(
            "product-crud.yaml case exists",
            "_shared/verify/cases/product-crud.yaml"
        ))
        self.add_result(self.test_file_exists(
            "order-relation.yaml case exists",
            "_shared/verify/cases/order-relation.yaml"
        ))

        # 4. SKILL.md Size Tests (Design Requirement)
        print(f"\n{BLUE}[4] SKILL.md Size Tests (Design Constraints){RESET}")
        self.add_result(self.test_skill_entry_size(
            "Entry SKILL.md ≤ 500 lines",
            "SKILL.md",
            500
        ))
        self.add_result(self.test_skill_entry_size(
            "v14 SKILL.md ≤ 150 lines",
            "v14/SKILL.md",
            150
        ))
        self.add_result(self.test_skill_entry_size(
            "v13 SKILL.md ≤ 150 lines",
            "v13/SKILL.md",
            150
        ))

        # 5. Frontmatter Tests
        print(f"\n{BLUE}[5] Rules Frontmatter Tests{RESET}")
        self.add_result(self.test_frontmatter(
            "v14 scaffold rules have frontmatter",
            "v14/rules/scaffold/*.md",
            ["title", "version", "impact"]
        ))
        self.add_result(self.test_frontmatter(
            "v14 pattern rules have frontmatter",
            "v14/rules/pattern/*.md",
            ["title", "version", "impact"]
        ))

        # 6. Content Structure Tests
        print(f"\n{BLUE}[6] Content Structure Tests{RESET}")
        self.add_result(self.test_file_content(
            "v14 modes/verify.md has Workflow",
            "v14/modes/verify.md",
            ["## Workflow", "Level 1", "Level 2"]
        ))
        self.add_result(self.test_file_content(
            "v14 modes/scaffold.md has Workflow",
            "v14/modes/scaffold.md",
            ["## Workflow", "Step"]
        ))
        self.add_result(self.test_file_content(
            "learn/workflow.md has Failures section",
            "_shared/learn/workflow.md",
            ["Failures Captured", "failures.yaml"]
        ))

        # Summary
        print(f"\n{BLUE}{'='*60}{RESET}")
        passed = sum(1 for r in self.results if r.passed)
        total = len(self.results)
        percentage = (passed / total * 100) if total > 0 else 0

        if passed == total:
            print(f"{GREEN}All {total} tests passed! ✅{RESET}")
        else:
            print(f"{YELLOW}Results: {passed}/{total} tests passed ({percentage:.1f}%){RESET}")
            print(f"{RED}Failed tests:{RESET}")
            for r in self.results:
                if not r.passed:
                    print(f"  - {r.name}: {r.message}")

        print(f"{BLUE}{'='*60}{RESET}\n")

        return passed == total


def main():
    # Determine base path
    script_path = Path(__file__).resolve()
    base_path = script_path.parent.parent.parent.parent  # Go up to repo root

    print(f"Base path: {base_path}")
    print(f"Skill path: {base_path / 'skills' / 'qscmf-backend'}")

    validator = StaticValidator(base_path)
    success = validator.run_all_tests()

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
