#!/bin/bash
# PHP Syntax Verification Script
# Usage: ./verify-syntax.sh /path/to/project file1.php file2.php ...
#
# This script is a REFERENCE TEMPLATE. AI should execute commands directly
# in the target project directory, not deploy this script.

PROJECT_ROOT="${1:-.}"
shift
FILES="$@"

PASS_COUNT=0
FAIL_COUNT=0

echo "=== PHP Syntax Verification ==="
echo "Project: $PROJECT_ROOT"
echo ""

for file in $FILES; do
    FULL_PATH="$PROJECT_ROOT/$file"
    if [ -f "$FULL_PATH" ]; then
        OUTPUT=$(php -l "$FULL_PATH" 2>&1)
        if [ $? -eq 0 ]; then
            echo "[✅] $file - No syntax errors"
            ((PASS_COUNT++))
        else
            echo "[❌] $file - Syntax error"
            echo "     $OUTPUT"
            ((FAIL_COUNT++))
        fi
    else
        echo "[⚠️] $file - File not found"
        ((FAIL_COUNT++))
    fi
done

echo ""
echo "=== Summary ==="
echo "Passed: $PASS_COUNT"
echo "Failed: $FAIL_COUNT"

if [ $FAIL_COUNT -gt 0 ]; then
    exit 1
fi
