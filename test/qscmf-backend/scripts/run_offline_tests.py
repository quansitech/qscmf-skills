#!/usr/bin/env python3
"""
QSCMF Skill Offline Tests - MVP
从 cases.yaml 读取测试用例，验证技能逻辑，零 token 成本

Usage:
    python3 test/qscmf-backend/scripts/run_offline_tests.py
"""

import os
import sys
import re
import glob as glob_module
from pathlib import Path
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any

# Colors for output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
CYAN = '\033[96m'
RESET = '\033[0m'

@dataclass
class TestResult:
    test_id: str
    test_name: str
    assertion: str
    passed: bool
    message: str

def parse_cases_yaml(content: str) -> List[Dict]:
    """Parse cases.yaml into a list of test cases"""
    tests = []
    lines = content.split('\n')

    current_test = None
    current_assertion = None

    for i, line in enumerate(lines):
        stripped = line.strip()

        # Skip empty lines and comments
        if not stripped or stripped.startswith('#'):
            continue

        # New test case: "  - id: XXX"
        if stripped.startswith('- id:'):
            # Save previous test
            if current_test:
                if current_assertion and current_assertion.get('type'):
                    current_test['assertions'].append(current_assertion)
                tests.append(current_test)

            test_id = stripped.split(':', 1)[1].strip()
            current_test = {
                'id': test_id,
                'name': '',
                'description': '',
                'file': None,
                'files': None,
                'assertions': []
            }
            current_assertion = None

        elif current_test:
            # Parse test fields
            if stripped.startswith('name:'):
                val = stripped.split(':', 1)[1].strip()
                if (val.startswith('"') and val.endswith('"')) or (val.startswith("'") and val.endswith("'")):
                    val = val[1:-1]
                current_test['name'] = val
            elif stripped.startswith('description:'):
                val = stripped.split(':', 1)[1].strip()
                if (val.startswith('"') and val.endswith('"')) or (val.startswith("'") and val.endswith("'")):
                    val = val[1:-1]
                current_test['description'] = val
            elif stripped.startswith('file:'):
                val = stripped.split(':', 1)[1].strip()
                if (val.startswith('"') and val.endswith('"')) or (val.startswith("'") and val.endswith("'")):
                    val = val[1:-1]
                current_test['file'] = val
            elif stripped.startswith('files:'):
                # Start of files list - will be populated by subsequent items
                current_test['files_list'] = []
            elif stripped.startswith('- "') and 'files_list' in current_test:
                # Add to files list
                file_path = stripped[3:].strip().rstrip('"')
                current_test['files_list'].append(file_path)

            # Parse assertion fields
            elif stripped.startswith('- type:'):
                # Save previous assertion
                if current_assertion and current_assertion.get('type'):
                    current_test['assertions'].append(current_assertion)
                current_assertion = {'type': stripped.split(':', 1)[1].strip().strip('"')}
            elif current_assertion:
                if stripped.startswith('value:'):
                    val = stripped.split(':', 1)[1].strip()
                    # Strip surrounding quotes if present
                    if (val.startswith('"') and val.endswith('"')) or (val.startswith("'") and val.endswith("'")):
                        val = val[1:-1]
                    current_assertion['value'] = val
                elif stripped.startswith('message:'):
                    msg = stripped.split(':', 1)[1].strip()
                    if (msg.startswith('"') and msg.endswith('"')) or (msg.startswith("'") and msg.endswith("'")):
                        msg = msg[1:-1]
                    current_assertion['message'] = msg

    # Save last test
    if current_test:
        if current_assertion and current_assertion.get('type'):
            current_test['assertions'].append(current_assertion)
        tests.append(current_test)

    return tests


class OfflineTestRunner:
    def __init__(self, base_path: Path):
        self.base_path = base_path
        self.skill_path = base_path / "skills" / "qscmf-backend"
        self.results: List[TestResult] = []
        self.passed = 0
        self.failed = 0

    def load_cases(self) -> List[Dict]:
        """Load test cases from YAML file"""
        cases_file = self.base_path / "test" / "qscmf-backend" / "tests" / "cases.yaml"
        if not cases_file.exists():
            print(f"{RED}Error: cases.yaml not found at {cases_file}{RESET}")
            return []

        with open(cases_file, 'r', encoding='utf-8') as f:
            content = f.read()

        return parse_cases_yaml(content)

    def check_assertion(self, content: str, assertion: Dict, file_path: Path = None) -> tuple:
        """Check a single assertion against file content"""
        atype = assertion.get('type', '')
        value = assertion.get('value', '')

        if atype == 'contains':
            result = value in content
            return result, f"'{value}' found" if result else f"'{value}' not found"
        elif atype == 'not-contains':
            result = value not in content
            return result, f"'{value}' not present" if result else f"'{value}' unexpectedly found"
        elif atype == 'regex':
            match = re.search(value, content)
            return bool(match), f"Pattern matched" if match else f"Pattern not matched"
        elif atype == 'exists':
            # File existence is already checked before this
            return True, "File exists"
        else:
            return False, f"Unknown assertion type: {atype}"

    def run_test(self, test: Dict) -> List[TestResult]:
        """Run a single test case"""
        results = []
        test_id = test.get('id', 'unknown')
        test_name = test.get('name', 'unnamed')
        assertions = test.get('assertions', [])

        # Get file(s) to check
        file_pattern = test.get('file')
        files_pattern = test.get('files')
        files_list = test.get('files_list', [])

        files_to_check = []
        if file_pattern:
            fp = self.skill_path / file_pattern
            if fp.exists():
                files_to_check.append(fp)
            else:
                results.append(TestResult(
                    test_id=test_id,
                    test_name=test_name,
                    assertion="file check",
                    passed=False,
                    message=f"File not found: {file_pattern}"
                ))
                return results

        if files_pattern:
            pattern = str(self.skill_path / files_pattern)
            matched = [Path(f) for f in glob_module.glob(pattern)]
            if matched:
                files_to_check.extend(matched)

        if files_list:
            for fp in files_list:
                pattern = str(self.skill_path / fp)
                matched = [Path(f) for f in glob_module.glob(pattern)]
                if matched:
                    files_to_check.extend(matched)

        if not files_to_check:
            results.append(TestResult(
                test_id=test_id,
                test_name=test_name,
                assertion="setup",
                passed=False,
                message="No file specified"
            ))
            return results

        # Check each assertion
        for assertion in assertions:
            atype = assertion.get('type', 'unknown')
            avalue = assertion.get('value', '')
            amsg = assertion.get('message', '')

            all_passed = True
            fail_msg = amsg

            for file_path in files_to_check:
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()

                    passed, msg = self.check_assertion(content, assertion)
                    if not passed:
                        all_passed = False
                        fail_msg = f"{amsg} (in {file_path.name})"
                        break
                except Exception as e:
                    all_passed = False
                    fail_msg = f"Error reading {file_path.name}: {e}"
                    break

            assertion_label = f"{atype}: {avalue[:25]}..." if len(avalue) > 25 else f"{atype}: {avalue}"
            results.append(TestResult(
                test_id=test_id,
                test_name=test_name,
                assertion=assertion_label,
                passed=all_passed,
                message=fail_msg
            ))

        return results

    def run_all(self):
        """Run all test cases"""
        print(f"\n{BLUE}{'='*60}{RESET}")
        print(f"{BLUE}QSCMF Skill Offline Tests - MVP{RESET}")
        print(f"{BLUE}{'='*60}{RESET}\n")

        cases = self.load_cases()
        if not cases:
            print(f"{RED}No test cases found{RESET}")
            return False

        print(f"Loaded {len(cases)} test cases\n")

        # Group by prefix (section)
        sections = {}
        for test in cases:
            test_id = test.get('id', '')
            prefix = test_id.split('-')[0] if '-' in test_id else 'other'
            if prefix not in sections:
                sections[prefix] = []
            sections[prefix].append(test)

        section_names = {
            'CL': 'Closed Loop Tests',
            'VS': 'Verify System Tests',
            'FI': 'Field Inference Tests',
            'VD': 'Version Detection Tests',
            'SEC': 'Security Tests',
            'MR': 'Mode Routing Tests',
        }

        for section_key, tests in sections.items():
            section_name = section_names.get(section_key, section_key)
            print(f"{CYAN}[{section_name}]{RESET}")

            for test in tests:
                results = self.run_test(test)
                for result in results:
                    self.results.append(result)
                    if result.passed:
                        self.passed += 1
                        status = f"{GREEN}✅{RESET}"
                    else:
                        self.failed += 1
                        status = f"{RED}❌{RESET}"

                    print(f"  {status} [{result.test_id}] {result.test_name}")
                    if not result.passed:
                        print(f"      {YELLOW}{result.message}{RESET}")

            print()

        # Summary
        total = self.passed + self.failed
        print(f"{BLUE}{'='*60}{RESET}")
        if self.failed == 0:
            print(f"{GREEN}All {total} tests passed! ✅{RESET}")
        else:
            pct = (self.passed / total * 100) if total > 0 else 0
            print(f"{YELLOW}Results: {self.passed}/{total} passed ({pct:.1f}%){RESET}")
            print(f"{RED}Failed: {self.failed}{RESET}")

        print(f"{BLUE}{'='*60}{RESET}\n")

        return self.failed == 0


def main():
    script_path = Path(__file__).resolve()
    base_path = script_path.parent.parent.parent.parent

    print(f"Base path: {base_path}")

    runner = OfflineTestRunner(base_path)
    success = runner.run_all()

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
