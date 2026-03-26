# Verification Test Cases

This directory contains YAML test cases for verifying scaffold output.

## Case Format

```yaml
name: "Case Name"
description: "What this case verifies"
input: "The scaffold trigger prompt"

assertions:
  - type: assertion-type
    # assertion-specific fields
```

## Assertion Types

### file-exists

Check if file exists.

```yaml
- type: file-exists
  path: "app/Admin/Controller/ProductController.class.php"
  glob: false  # Set true for wildcard patterns
  message: "Optional explanation"
```

### contains

Check if file contains specific strings (semantic matching, not exact).

```yaml
- type: contains
  file: "app/Admin/Controller/ProductController.class.php"
  values:
    - "QsListController"
    - "addTableColumn"
  message: "Controller should use ListBuilder API"
```

### php-lint

Run PHP syntax check on files.

```yaml
- type: php-lint
  pattern: "app/**/*.php"  # Glob pattern
  message: "All PHP files should pass syntax check"
```

## Adding New Cases

1. Create a new YAML file in this directory
2. Follow the format above
3. Test with `/qscmf-verify --case <filename>`
