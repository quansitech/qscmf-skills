> This file extends common patterns with QSMCF-specific migration metadata for enhanced code generation.

# Migration Metadata System for QSMCF

This document describes the enhanced metadata system for QSMCF migrations, providing detailed field information for intelligent code generation.

## Metadata Storage Format

Migration metadata is stored in `.claude/qsmcf/metadata.json` with the following structure:

```json
{
    "tables": {
        "users": {
            "table_comment": "用户表",
            "fields": {
                "id": {
                    "type": "integer",
                    "database_type": "int(11) unsigned",
                    "primary": true,
                    "auto_increment": true,
                    "nullable": false,
                    "comment": "主键ID"
                },
                "name": {
                    "type": "string",
                    "database_type": "varchar(255)",
                    "nullable": false,
                    "comment": "用户名称",
                    "validation": "required|max:255"
                },
                "email": {
                    "type": "string",
                    "database_type": "varchar(255)",
                    "unique": true,
                    "nullable": false,
                    "comment": "邮箱",
                    "validation": "required|email|unique:users,email"
                },
                "password": {
                    "type": "password",
                    "database_type": "varchar(255)",
                    "nullable": false,
                    "comment": "密码",
                    "validation": "required|min:8"
                },
                "status": {
                    "type": "select",
                    "database_type": "varchar(20)",
                    "nullable": false,
                    "default": "active",
                    "comment": "状态",
                    "options": {
                        "active": "激活",
                        "inactive": "未激活"
                    }
                },
                "created_at": {
                    "type": "datetime",
                    "database_type": "datetime",
                    "nullable": true,
                    "comment": "创建时间"
                },
                "updated_at": {
                    "type": "datetime",
                    "database_type": "datetime",
                    "nullable": true,
                    "comment": "更新时间"
                }
            }
        }
    }
}
```

## Field Type Inference

### Basic Type Mapping

| Database Type | Inferred Type | Form Field | Description |
|---------------|--------------|------------|-------------|
| int(11) | integer | number | Integer field |
| int(11) unsigned | integer | number | Unsigned integer |
| varchar(255) | string | text | Text input field |
| varchar(255) with email validation | string | email | Email input field |
| varchar(255) with url validation | string | url | URL input field |
| text | text | textarea | Multi-line text area |
| longtext | text | textarea, richtext | Rich text editor |
| decimal(10,2) | decimal | number, money | Decimal number |
| datetime | datetime | datetime | Date and time picker |
| date | date | date | Date picker |
| time | time | time | Time picker |
| tinyint(1) | boolean | switch, checkbox | Boolean value |
| enum(enum_val1,enum_val2) | select | select, radio | Select dropdown |
| json | json | json | JSON editor |

### Advanced Field Type Detection

#### File Fields
```json
"avatar": {
    "type": "file",
    "database_type": "varchar(255)",
    "nullable": true,
    "comment": "头像",
    "mime_types": ["image/jpeg", "image/png", "image/gif"],
    "max_size": 2048,
    "storage": "storage/avatars"
}
```

#### Image Fields
```json
"cover_image": {
    "type": "image",
    "database_type": "varchar(255)",
    "nullable": true,
    "comment": "封面图片",
    "mime_types": ["image/jpeg", "image/png"],
    "max_size": 1024,
    "dimensions": {
        "min_width": 800,
        "max_width": 1920,
        "min_height": 600,
        "max_height": 1080
    }
}
```

#### Rich Text Fields
```json
"content": {
    "type": "richtext",
    "database_type": "longtext",
    "nullable": false,
    "comment": "内容",
    "editor": "ueditor",
    "upload_config": {
        "image_upload_path": "uploads/images",
        "file_upload_path": "uploads/files"
    }
}
```

#### Relationship Fields
```json
"category_id": {
    "type": "select",
    "database_type": "int(11)",
    "nullable": false,
    "comment": "分类ID",
    "relationship": {
        "type": "belongsTo",
        "model": "Category",
        "foreign_key": "id",
        "title": "name"
    },
    "validation": "required|exists:categories,id"
}
```

## Metadata Generation

### Migration Parsing

```php
class MetadataGenerator
{
    public function generateFromMigration(string $migrationFile): array
    {
        $content = file_get_contents($migrationFile);
        $parser = new MigrationParser();
        $table = $parser->parseTableName($content);
        $columns = $parser->parseColumns($content);
        
        $metadata = [
            'table_comment' => $parser->parseTableComment($content),
            'fields' => []
        ];
        
        foreach ($columns as $column) {
            $metadata['fields'][$column['name']] = $this->inferFieldMetadata($column);
        }
        
        return $metadata;
    }
    
    private function inferFieldMetadata(array $column): array
    {
        $field = [
            'type' => $this->inferFieldType($column),
            'database_type' => $column['type'],
            'nullable' => $column['nullable'],
            'default' => $column['default']
        ];
        
        if ($column['comment']) {
            $field['comment'] = $column['comment'];
        }
        
        if ($column['primary']) {
            $field['primary'] = true;
        }
        
        if ($column['unique']) {
            $field['unique'] = true;
        }
        
        if ($column['auto_increment']) {
            $field['auto_increment'] = true;
        }
        
        // Add validation rules based on field type
        $field['validation'] = $this->inferValidationRules($field);
        
        return $field;
    }
}
```

### Database Schema Inspection

```php
class SchemaInspector
{
    public function inspectDatabase(): array
    {
        $tables = DB::select("SHOW TABLES");
        $metadata = [];
        
        foreach ($tables as $table) {
            $tableName = current((array)$table);
            $metadata[$tableName] = $this->inspectTable($tableName);
        }
        
        return $metadata;
    }
    
    private function inspectTable(string $tableName): array
    {
        $columns = DB::select("SHOW COLUMNS FROM {$tableName}");
        $metadata = [
            'table_comment' => $this->getTableComment($tableName),
            'fields' => []
        ];
        
        foreach ($columns as $column) {
            $field = $this->parseColumn($column);
            $metadata['fields'][$field['name']] = $field;
        }
        
        return $metadata;
    }
}
```

## Field Configuration

### Form Field Configuration

```php
return [
    // Basic field configuration
    'name' => [
        'type' => 'text',
        'label' => '名称',
        'placeholder' => '请输入名称',
        'rules' => 'required|max:255',
        'help' => '请输入2-255个字符的名称'
    ],
    
    // Select field with options
    'status' => [
        'type' => 'select',
        'label' => '状态',
        'options' => [
            'active' => '启用',
            'inactive' => '禁用',
            'pending' => '待审核'
        ],
        'rules' => 'required|in:active,inactive,pending',
        'default' => 'active'
    ],
    
    // File upload field
    'avatar' => [
        'type' => 'image',
        'label' => '头像',
        'rules' => 'nullable|image|max:2048|mimes:jpeg,png,jpg,gif',
        'help' => '支持JPG、PNG格式，最大2MB',
        'preview' => true
    ],
    
    // Rich text editor
    'content' => [
        'type' => 'richtext',
        'label' => '内容',
        'rules' => 'required|string',
        'editor' => 'ueditor',
        'height' => 400,
        'help' => '支持插入图片和视频'
    ],
    
    // Date range picker
    'created_at' => [
        'type' => 'daterange',
        'label' => '创建时间',
        'format' => 'YYYY-MM-DD',
        'help' => '选择创建时间范围'
    ]
];
```

### List Field Configuration

```php
return [
    // Basic list field
    'id' => [
        'title' => 'ID',
        'width' => 80,
        'fixed' => 'left',
        'sorter' => true,
        'searchable' => false
    ],
    
    // Text field with search
    'name' => [
        'title' => '名称',
        'minWidth' => 120,
        'searchable' => true,
        'ellipsis' => true,
        'tooltip' => true
    ],
    
    // Money format field
    'price' => [
        'title' => '价格',
        'type' => 'money',
        'width' => 120,
        'sorter' => true,
        'align' => 'right',
        'prefix' => '¥'
    ],
    
    // Image preview
    'avatar' => [
        'title' => '头像',
        'type' => 'image',
        'width' => 80,
        'height' => 80,
        'preview' => true,
        'formatter' => 'image'
    ],
    
    // Status badge
    'status' => [
        'title' => '状态',
        'type' => 'select',
        'width' => 100,
        'filterOptions' => [
            'active' => '启用',
            'inactive' => '禁用'
        ],
        'formatter' => 'status'
    ],
    
    // Action buttons
    'action' => [
        'title' => '操作',
        'width' => 200,
        'fixed' => 'right',
        'buttons' => [
            'view' => ['text' => '查看', 'type' => 'link'],
            'edit' => ['text' => '编辑', 'type' => 'link'],
            'delete' => ['text' => '删除', 'type' => 'danger']
        ]
    ]
];
```

## Advanced Features

### Conditional Fields

```php
'fields' => [
    // Basic field
    'type' => [
        'type' => 'select',
        'label' => '类型',
        'options' => [
            'personal' => '个人',
            'business' => '企业'
        ],
        'rules' => 'required|in:personal,business'
    ],
    
    // Conditional field based on type
    'company_name' => [
        'type' => 'text',
        'label' => '公司名称',
        'rules' => 'required_if:type,business|string|max:255',
        'dependencies' => ['type'],
        'showWhen' => 'type === "business"'
    ],
    
    // Another conditional field
    'industry' => [
        'type' => 'select',
        'label' => '行业',
        'options' => [
            'tech' => '科技',
            'finance' => '金融',
            'health' => '医疗'
        ],
        'rules' => 'required_if:type,business|in:tech,finance,health',
        'dependencies' => ['type'],
        'showWhen' => 'type === "business"'
    ]
]
```

### Validation Rules Generation

```php
class ValidationGenerator
{
    public function generateRules(array $metadata): array
    {
        $rules = [];
        
        foreach ($metadata['fields'] as $field => $fieldData) {
            if (isset($fieldData['validation'])) {
                $rules[$field] = $fieldData['validation'];
            } else {
                $rules[$field] = $this->inferRules($fieldData);
            }
        }
        
        return $rules;
    }
    
    private function inferRules(array $fieldData): string
    {
        $rules = [];
        
        // Required field
        if (!$fieldData['nullable']) {
            $rules[] = 'required';
        } else {
            $rules[] = 'nullable';
        }
        
        // Type-based rules
        switch ($fieldData['type']) {
            case 'string':
            case 'text':
                $rules[] = 'string';
                if (isset($fieldData['max'])) {
                    $rules[] = 'max:' . $fieldData['max'];
                }
                break;
                
            case 'integer':
                $rules[] = 'integer';
                if (isset($fieldData['min'])) {
                    $rules[] = 'min:' . $fieldData['min'];
                }
                if (isset($fieldData['max'])) {
                    $rules[] = 'max:' . $fieldData['max'];
                }
                break;
                
            case 'decimal':
                $rules[] = 'numeric';
                if (isset($fieldData['min'])) {
                    $rules[] = 'min:' . $fieldData['min'];
                }
                if (isset($fieldData['max'])) {
                    $rules[] = 'max:' . $fieldData['max'];
                }
                break;
                
            case 'email':
                $rules[] = 'email';
                break;
                
            case 'url':
                $rules[] = 'url';
                break;
        }
        
        // Unique rule
        if ($fieldData['unique'] ?? false) {
            $rules[] = 'unique:' . $metadata['table'] . ',' . $field;
        }
        
        // Existence rule
        if (isset($fieldData['relationship'])) {
            $relation = $fieldData['relationship'];
            $rules[] = 'exists:' . strtolower($relation['model']) . 's,id';
        }
        
        return implode('|', $rules);
    }
}
```

### Relationship Metadata

```json
{
    "relationships": {
        "category": {
            "type": "belongsTo",
            "model": "Category",
            "foreign_key": "category_id",
            "title": "name",
            "with": ['parent']
        },
        "tags": {
            "type": "belongsToMany",
            "model": "Tag",
            "table": "product_tags",
            "foreign_key": "product_id",
            "related_key": "tag_id",
            "title": "name",
            "pivot": [
                {"column": "created_at", "type": "datetime"},
                {"column": "created_by", "type": "integer"}
            ]
        },
        "images": {
            "type": "morphMany",
            "model": "Image",
            "name": "imageable"
        }
    }
}
```

## Metadata Cache and Updates

### Cache Management

```php
class MetadataCache
{
    private const CACHE_KEY = 'qsmcf_metadata';
    private const CACHE_TTL = 3600; // 1 hour
    
    public function get(): ?array
    {
        return Cache::remember(self::CACHE_KEY, self::CACHE_TTL, function () {
            return $this->generateMetadata();
        });
    }
    
    public function clear(): void
    {
        Cache::forget(self::CACHE_KEY);
        Cache::tags(['qsmcf_metadata'])->flush();
    }
    
    public function updateTable(string $tableName): void
    {
        $this->clear();
        $metadata = $this->get();
        
        if (isset($metadata[$tableName])) {
            // Update specific table metadata
            $metadata[$tableName] = $this->inspectTable($tableName);
            Cache::put(self::CACHE_KEY, $metadata);
        }
    }
}
```

### Automatic Metadata Updates

```php
class MetadataObserver
{
    public function created($table)
    {
        app(MetadataCache::class)->updateTable($table);
    }
    
    public function updated($table)
    {
        app(MetadataCache::class)->updateTable($table);
    }
    
    public function deleted($table)
    {
        app(MetadataCache::class)->clear();
    }
}
```

## Best Practices

### 1. Keep Metadata Up-to-Date

- Run metadata update after each migration
- Use version control for metadata files
- Backup metadata before major changes

### 2. Use Version Control

```json
{
    "version": "1.0.0",
    "generated_at": "2024-01-01T12:00:00Z",
    "generator": "qsmcf-metadata-generator",
    "tables": {
        // table metadata
    }
}
```

### 3. Validate Metadata

- Check for duplicate field names
- Validate relationship references
- Ensure proper type mappings
- Check validation rule syntax

### 4. Performance Considerations

- Cache metadata for better performance
- Use lazy loading for large metadata sets
- Implement incremental updates
- Use database indexes for metadata queries

### 5. Security

- Store sensitive metadata securely
- Limit metadata access
- Encrypt metadata in storage
- Audit metadata changes
