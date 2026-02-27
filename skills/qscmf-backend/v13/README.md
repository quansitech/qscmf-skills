# QSCMF Backend - Version 13

This directory contains version-specific implementation details for QSCMF v13.

> **Note**: For version detection, see the root [SKILL.md](../SKILL.md).

## Version Overview

QSCMF v13 features:
- **PHP 8.2** with type declarations
- **PHPUnit 9** for testing
- **jQuery + Bootstrap** for frontend rendering
- **ListBuilder API** with traditional template rendering

## Rendering Mode

v13 uses **jQuery + Bootstrap 3** rendering:

```php
// Environment constant
ANTD_ADMIN_BUILDER_ENABLE = false  // v13 default
```

## Key Features

### ListBuilder API

v13 uses the ListBuilder API with jQuery/Bootstrap rendering:

```php
$builder = $this->builder();

// Table columns
$builder->addTableColumn('id', 'ID');
$builder->addTableColumn('name', '名称');
$builder->addTableColumn('status', '状态', DBCont::getStatusList());

// Search items
$builder->addSearchItem('keyword', 'text', '关键词');
$builder->addSearchItem('status', 'select', '状态', '', DBCont::getStatusList());

// Buttons
$builder->addTopButton('addnew', ['title' => '新增']);
$builder->addRightButton('edit', ['href' => U('edit', ['id' => '@id@'])]);
$builder->addRightButton('delete', ['href' => U('delete', ['ids' => '@id@'])]);

$builder->display();
```

### Bootstrap CSS Classes

v13 admin pages use Bootstrap 3 classes:

```html
<!-- Status badges -->
<span class="label label-success">启用</span>
<span class="label label-default">禁用</span>

<!-- Buttons -->
<button class="btn btn-primary">新增</button>
<button class="btn btn-danger">删除</button>
```

### jQuery Event Handling

```javascript
// Custom form submission
$('#myForm').on('submit', function(e) {
    e.preventDefault();
    $.post($(this).attr('action'), $(this).serialize(), function(res) {
        if (res.status) {
            location.reload();
        }
    });
});
```

## Configuration

### composer.json
```json
{
    "require": {
        "php": "^8.2",
        "tiderjian/think-core": "^13.0"
    },
    "require-dev": {
        "phpunit/phpunit": "^9.3.0"
    }
}
```

## Testing

v13 uses PHPUnit 9:

```php
class ProductTest extends TestCase
{
    public function testIndex()
    {
        $response = $this->get('/admin/product/index');
        $response->assertStatus(200);
        $response->assertSee('Product List');
    }
}
```

## Directory Structure

```
v13/
├── SKILL.md               # v13 workflow (main entry)
├── README.md              # This file
├── templates/             # Code generation templates
│   ├── admin_controller.php.tpl
│   ├── model.php.tpl
│   ├── api_controller.php.tpl
│   └── test_case.php.tpl
└── rules/                 # Version-specific rules
    ├── listbuilder-api.md
    ├── formbuilder-api.md
    ├── legacy-jquery.md
    └── ...
```

## Getting Started

1. Read the [SKILL.md](./SKILL.md) for complete v13 workflow
2. Use shared references from [_shared/](../_shared/) for cross-version concepts
