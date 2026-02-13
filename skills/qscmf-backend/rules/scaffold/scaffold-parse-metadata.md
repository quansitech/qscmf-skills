---
title: Parse Migration Metadata
impact: CRITICAL
impactDescription: Required; 100% of scaffold operations depend on this
tags: scaffold, metadata, parsing, both
---

## Parse Migration Metadata

**Impact: CRITICAL (Required for all scaffold operations)**

Parse @metadata annotations from migration file comments.

### When to Use This Rule

- You need to extract field information from migration
- You need to understand the @metadata annotation format
- You want to validate metadata completeness

---

## @metadata Format

Each column comment contains semicolon-separated key=value pairs:

```php
$table->string('name', 200)->comment('@title=产品名称;@type=text;@length=1,200;@require=true;');
```

### Required Attributes

| Attribute | Description | Example |
|-----------|-------------|---------|
| `@title` | Display label (Chinese) | `@title=产品名称;` |
| `@type` | Field type (17 types) | `@type=text;` |

### Optional Attributes

| Attribute | Description | Example |
|-----------|-------------|---------|
| `@require` | Is required field | `@require=true;` |
| `@length` | Length validation | `@length=1,200;` |
| `@save` | Enable inline edit | `@save=true;` |
| `@table` | FK table name | `@table=category;` |
| `@show` | FK display field | `@show=title;` |
| `@list` | DBCont variable | `@list=status;` |
| `@oss` | Use OSS storage | `@oss=true;` |

---

## Parsing Algorithm

### Step 1: Read Migration File

```python
def find_migration(table_name: str, migrations_dir: str) -> str:
    """Find migration file for table."""
    import glob

    patterns = [
        f"{migrations_dir}/*create_{table_name}*",
        f"{migrations_dir}/*_{table_name}*",
    ]

    for pattern in patterns:
        matches = glob.glob(pattern)
        if matches:
            return matches[0]

    return None
```

### Step 2: Extract Column Definitions

```python
import re

def extract_columns(migration_content: str) -> list:
    """Extract column definitions from migration."""
    # Match $table->type('name', ...) patterns
    pattern = r'\$table->(\w+)\([\'"](\w+)[\'"][^)]*\)(?:->[^;]+)*->comment\([\'"]([^\'"]+)[\'"]\);'

    columns = []
    for match in re.finditer(pattern, migration_content):
        column_type, column_name, comment = match.groups()
        columns.append({
            'type': column_type,
            'name': column_name,
            'comment': comment,
        })

    return columns
```

### Step 3: Parse @metadata

```python
def parse_metadata(comment: str) -> dict:
    """Parse @metadata from column comment."""
    metadata = {}

    # Match @key=value; patterns
    pattern = r'@(\w+)=([^;]*);'
    for match in re.finditer(pattern, comment):
        key, value = match.groups()

        # Type conversion
        if value == 'true':
            value = True
        elif value == 'false':
            value = False
        elif value.isdigit():
            value = int(value)
        elif ',' in value and all(p.isdigit() for p in value.split(',')):
            value = [int(p) for p in value.split(',')]

        metadata[key] = value

    return metadata
```

### Step 4: Build Field Definition

```python
def build_field_definition(column: dict, metadata: dict) -> dict:
    """Build complete field definition."""
    return {
        'name': column['name'],
        'db_type': column['type'],
        'title': metadata.get('title', column['name']),
        'type': metadata.get('type', infer_from_db_type(column['type'])),
        'required': metadata.get('require', False),
        'length': metadata.get('length'),
        'save': metadata.get('save', False),
        'foreign_key': {
            'table': metadata.get('table'),
            'show': metadata.get('show'),
        } if metadata.get('table') else None,
        'list': metadata.get('list'),
        'oss': metadata.get('oss', False),
    }
```

---

## Complete Parser Example

```python
#!/usr/bin/env python3
"""
Migration Metadata Parser for QSCMF

Usage:
    python parse_schema.py <table_name> [--version v14]
"""

import re
import json
import argparse
from pathlib import Path


class MigrationParser:
    """Parse migration file and extract metadata."""

    # Map Laravel column types to default @type
    DB_TYPE_MAP = {
        'string': 'text',
        'text': 'textarea',
        'integer': 'num',
        'bigInteger': 'num',
        'unsignedBigInteger': 'select',
        'tinyInteger': 'status',
        'decimal': 'num',
        'float': 'num',
        'date': 'date',
        'datetime': 'datetime',
        'time': 'time',
        'boolean': 'status',
    }

    def __init__(self, migrations_dir: str):
        self.migrations_dir = Path(migrations_dir)

    def find_migration(self, table_name: str) -> Path:
        """Find migration file for table."""
        patterns = [
            f"*create_{table_name}*",
            f"*create_{table_name.replace('qs_', '')}*",
        ]

        for pattern in patterns:
            matches = list(self.migrations_dir.glob(pattern))
            if matches:
                return matches[0]

        raise FileNotFoundError(f"Migration not found for table: {table_name}")

    def parse(self, table_name: str) -> dict:
        """Parse migration and return schema."""
        migration_file = self.find_migration(table_name)
        content = migration_file.read_text(encoding='utf-8')

        return {
            'table': table_name,
            'file': str(migration_file),
            'fields': self._extract_fields(content),
        }

    def _extract_fields(self, content: str) -> list:
        """Extract all fields from migration."""
        fields = []

        # Match column definitions
        pattern = r'\$table->(\w+)\([\'"]?(\w+)[\'"]?[^)]*\)([^;]*);'
        for match in re.finditer(pattern, content):
            column_type, column_name, modifiers = match.groups()

            # Skip system columns
            if column_name in ['id', 'created_at', 'updated_at', 'timestamps']:
                continue

            # Extract comment
            comment_match = re.search(r"->comment\([\'"]([^\'"]+)[\'"]\)", modifiers)
            comment = comment_match.group(1) if comment_match else ''

            # Parse metadata
            metadata = self._parse_metadata(comment)

            # Build field
            field = {
                'name': column_name,
                'db_type': column_type,
                'title': metadata.get('title', column_name),
                'type': metadata.get('type', self.DB_TYPE_MAP.get(column_type, 'text')),
                'nullable': 'nullable()' in modifiers,
                'default': self._extract_default(modifiers),
            }

            # Add optional attributes
            if metadata.get('require'):
                field['required'] = True
            if metadata.get('length'):
                field['length'] = metadata['length']
            if metadata.get('save'):
                field['save'] = True
            if metadata.get('table'):
                field['foreign_key'] = {
                    'table': metadata['table'],
                    'show': metadata.get('show', 'title'),
                }
            if metadata.get('list'):
                field['list'] = metadata['list']
            if metadata.get('oss'):
                field['oss'] = True

            fields.append(field)

        return fields

    def _parse_metadata(self, comment: str) -> dict:
        """Parse @metadata from comment."""
        metadata = {}
        pattern = r'@(\w+)=([^;]*);'

        for match in re.finditer(pattern, comment):
            key, value = match.groups()
            metadata[key] = self._convert_value(value)

        return metadata

    def _convert_value(self, value: str):
        """Convert string value to appropriate type."""
        if value == 'true':
            return True
        if value == 'false':
            return False
        if value.isdigit():
            return int(value)
        if ',' in value:
            parts = value.split(',')
            if all(p.isdigit() for p in parts):
                return [int(p) for p in parts]
        return value

    def _extract_default(self, modifiers: str) -> any:
        """Extract default value from modifiers."""
        match = re.search(r"->default\(([^)]+)\)", modifiers)
        if match:
            value = match.group(1)
            if value.isdigit():
                return int(value)
            if value.startswith("'") or value.startswith('"'):
                return value[1:-1]
            return value
        return None


def main():
    parser = argparse.ArgumentParser(description='Parse QSCMF migration metadata')
    parser.add_argument('table', help='Table name (with or without qs_ prefix)')
    parser.add_argument('--migrations-dir', default='lara/database/migrations',
                        help='Migrations directory')
    parser.add_argument('--format', choices=['json', 'yaml'], default='json',
                        help='Output format')

    args = parser.parse_args()

    try:
        migration_parser = MigrationParser(args.migrations_dir)
        schema = migration_parser.parse(args.table)

        if args.format == 'json':
            print(json.dumps(schema, indent=2, ensure_ascii=False))
        else:
            import yaml
            print(yaml.dump(schema, allow_unicode=True, default_flow_style=False))

    except FileNotFoundError as e:
        print(f"Error: {e}")
        return 1

    return 0


if __name__ == '__main__':
    exit(main())
```

---

## Validation Rules

### Required @metadata Check

```python
def validate_metadata(fields: list) -> list:
    """Validate metadata completeness."""
    errors = []

    for field in fields:
        # Check required attributes
        if not field.get('title'):
            errors.append(f"Field '{field['name']}' missing @title")

        if not field.get('type'):
            errors.append(f"Field '{field['name']}' missing @type")

        # Check type-specific requirements
        if field.get('type') == 'select':
            if not field.get('foreign_key') and not field.get('list'):
                errors.append(
                    f"Field '{field['name']}' is select type but has no @table or @list"
                )

        if field.get('type') in ['radio', 'checkbox']:
            if not field.get('list'):
                errors.append(
                    f"Field '{field['name']}' is {field['type']} type but has no @list"
                )

    return errors
```

### Common Validation Errors

| Error | Cause | Solution |
|-------|-------|----------|
| Missing @title | No display label | Add `@title=字段名;` to comment |
| Missing @type | No field type | Add `@type=text;` (or other type) |
| Select without source | No @table or @list | Add `@table=category;@show=title;` or `@list=status;` |
| Invalid @type | Unknown type value | Use one of 17 valid types |
| Missing semicolon | Incomplete attribute | Ensure each attribute ends with `;` |

---

## Output Format

### JSON Schema Output

```json
{
  "table": "qs_product",
  "file": "lara/database/migrations/2024_01_15_123456_create_product_table.php",
  "fields": [
    {
      "name": "name",
      "db_type": "string",
      "title": "产品名称",
      "type": "text",
      "required": true,
      "length": [1, 200],
      "nullable": false
    },
    {
      "name": "category_id",
      "db_type": "unsignedBigInteger",
      "title": "分类",
      "type": "select",
      "foreign_key": {
        "table": "category",
        "show": "title"
      },
      "nullable": false
    },
    {
      "name": "status",
      "db_type": "tinyInteger",
      "title": "状态",
      "type": "status",
      "list": "status",
      "default": 1,
      "nullable": false
    }
  ]
}
```

---

## Integration with Code Generation

```python
def generate_code(table_name: str, version: str = 'v14'):
    """Generate code from migration metadata."""
    parser = MigrationParser('lara/database/migrations')
    schema = parser.parse(table_name)

    # Validate metadata
    errors = validate_metadata(schema['fields'])
    if errors:
        print("Metadata validation errors:")
        for error in errors:
            print(f"  - {error}")
        return

    # Load version config
    config = load_version_config(version)

    # Generate each file
    for template_type in ['model', 'admin_controller', 'api_controller', 'test_case']:
        template = load_template(version, template_type)
        code = render_template(template, schema, config)
        write_file(template_type, table_name, code)
```

---

## See Also

- [Migration First](scaffold-migration-first.md) - Create migration with @metadata
- [Infer Types](scaffold-infer-types.md) - Field type inference
- [Generate Code](scaffold-generate-code.md) - Code generation workflow
- [Version Config](../../_shared/config/v14.yaml) - Version-specific configurations
