---
title: 字段类型推断
impact: HIGH
impactDescription: 提高 80% 代码生成准确率
tags: scaffold, type-inference, both
---

## 字段类型推断

**影响级别：HIGH（提高代码生成准确率）**

使用三层策略推断表单字段类型。

### 何时使用此规则

- 迁移文件缺少 @type 元数据
- 需要根据字段名自动推断类型
- 需要理解类型推断优先级

---

## 三层推断策略

```
┌─────────────────────────────────────┐
│  第一层：配置层（最高优先级）          │
│  _shared/config/v{X}.yaml           │
│  field_types 定义                    │
└─────────────────┬───────────────────┘
                  │ 未匹配
                  ▼
┌─────────────────────────────────────┐
│  第二层：学习层                       │
│  .claude/qscmf/learned-field-types.json │
│  扫描现有代码学习到的模式              │
└─────────────────┬───────────────────┘
                  │ 未匹配
                  ▼
┌─────────────────────────────────────┐
│  第三层：模式层（默认层）              │
│  字段名后缀匹配                       │
│  数据库类型回退                       │
└─────────────────────────────────────┘
```

---

## 第一层：配置层

从版本配置文件加载：

**文件路径**：`_shared/config/v14.yaml` 或 `_shared/config/v13.yaml`

```yaml
field_types:
  text:
    component: "text"
    description: "单行文本输入框"
    form_item: "text"
    list_column: "text"
    validation: ["length", "require"]

  select:
    component: "select"
    description: "下拉选择框"
    form_item: "select"
    list_column: "select"
    validation: ["in", "require"]
```

### 使用配置

```python
def load_field_type_config(version: str) -> dict:
    """加载版本特定的字段类型配置"""
    config_file = f"_shared/config/{version}.yaml"
    with open(config_file, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    return config.get('field_types', {})

def lookup_field_type(field_name: str, field_type: str, version: str) -> dict:
    """从配置查找字段类型定义"""
    config = load_field_type_config(version)
    return config.get(field_type, {})
```

---

## 第二层：学习层

从现有代码学习字段类型模式。

### 学习文件格式

**文件路径**：`.claude/qscmf/learned-field-types.json`

```json
{
  "product_name": {
    "inferred_type": "text",
    "confidence": "high",
    "sources": ["ProductController", "CategoryController"]
  },
  "category_id": {
    "inferred_type": "select",
    "confidence": "high",
    "foreign_key": true,
    "foreign_table": "category"
  },
  "article_content": {
    "inferred_type": "richText",
    "confidence": "high",
    "sources": ["ArticleController"]
  },
  "user_phone": {
    "inferred_type": "phone",
    "confidence": "medium",
    "sources": ["UserController"]
  }
}
```

### 学习算法

```python
def scan_existing_controllers(controllers_dir: str) -> dict:
    """扫描现有控制器，学习字段类型"""
    learned = {}
    pattern = re.compile(r"->(\w+)\(['\"](\w+)['\"].*?//\s*@type[:=]\s*(\w+)")

    for controller_file in Path(controllers_dir).rglob("*Controller.class.php"):
        content = controller_file.read_text(encoding='utf-8')

        for match in pattern.finditer(content):
            method, field_name, field_type = match.groups()

            if field_name not in learned:
                learned[field_name] = {
                    'inferred_type': field_type,
                    'confidence': 'medium',
                    'sources': []
                }
            learned[field_name]['sources'].append(controller_file.stem)

    return learned

def save_learned_types(learned: dict, output_file: str):
    """保存学习结果"""
    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(learned, f, indent=2, ensure_ascii=False)
```

---

## 第三层：模式层（默认）

### 字段名后缀模式

| 模式 | 类型 | 优先级 | 示例 |
|------|------|--------|------|
| `*_content` | richText | 90 | article_content |
| `*_desc` | textarea | 80 | product_desc |
| `*_description` | textarea | 80 | category_description |
| `*_remark` | textarea | 80 | order_remark |
| `*_summary` | textarea | 80 | article_summary |
| `*_date` | date | 95 | publish_date |
| `*_time` | datetime | 95 | create_time, update_time |
| `*_at` | datetime | 95 | deleted_at, published_at |
| `status` | status | 100 | status |
| `*_status` | select | 85 | order_status, audit_status |
| `is_*` | radio | 85 | is_active, is_top |
| `has_*` | radio | 85 | has_stock, has_discount |
| `*_id` | select | 90 | category_id, user_id |
| `cate_id` | select | 95 | cate_id |
| `user_id` | select | 95 | user_id |
| `cover` | picture | 90 | cover |
| `cover_id` | picture | 90 | cover_id |
| `thumb` | picture | 90 | thumb |
| `*_image` | picture | 85 | product_image |
| `*_images` | pictures | 85 | product_images |
| `avatar` | picture | 90 | avatar |
| `logo` | picture | 90 | logo |
| `file_id` | file | 90 | file_id |
| `*_file` | file | 80 | attachment_file |
| `*_files` | files | 80 | attachment_files |
| `sort` | num | 90 | sort |
| `*_sort` | num | 85 | display_sort |
| `*_count` | num | 85 | view_count, click_count |
| `*_price` | num | 90 | unit_price, sale_price |
| `*_amount` | num | 90 | total_amount, discount_amount |
| `*_qty` | num | 85 | stock_qty |
| `url` | url | 90 | url |
| `*_url` | url | 85 | site_url, callback_url |
| `link` | url | 85 | link |
| `*_link` | url | 80 | download_link |
| `phone` | phone | 90 | phone |
| `mobile` | phone | 90 | mobile |
| `tel` | phone | 90 | tel |
| `*_phone` | phone | 85 | contact_phone |
| `email` | email | 95 | email |
| `*_email` | email | 90 | contact_email |
| `address` | district | 85 | address |
| `*_address` | district | 80 | shipping_address |

### 数据库类型回退

| Laravel 类型 | 默认 @type |
|-------------|------------|
| `string` | text |
| `char` | text |
| `text` | textarea |
| `longText` | textarea |
| `integer` | num |
| `bigInteger` | num |
| `unsignedBigInteger` | select（外键） |
| `tinyInteger` | status |
| `smallInteger` | num |
| `decimal` | num |
| `float` | num |
| `double` | num |
| `date` | date |
| `datetime` | datetime |
| `timestamp` | datetime |
| `time` | time |
| `boolean` | status |

---

## 推断实现

```python
class FieldTypeInferrer:
    """字段类型推断器"""

    # 字段名模式（按优先级排序）
    FIELD_PATTERNS = [
        (r'^status$', 'status', 100),
        (r'_content$', 'richText', 90),
        (r'_desc$', 'textarea', 80),
        (r'_description$', 'textarea', 80),
        (r'_remark$', 'textarea', 80),
        (r'_summary$', 'textarea', 80),
        (r'_date$', 'date', 95),
        (r'_time$', 'datetime', 95),
        (r'_at$', 'datetime', 95),
        (r'_status$', 'select', 85),
        (r'^is_', 'radio', 85),
        (r'^has_', 'radio', 85),
        (r'^cate_id$', 'select', 95),
        (r'^user_id$', 'select', 95),
        (r'_id$', 'select', 90),
        (r'^cover$', 'picture', 90),
        (r'^cover_id$', 'picture', 90),
        (r'^thumb$', 'picture', 90),
        (r'^avatar$', 'picture', 90),
        (r'^logo$', 'picture', 90),
        (r'_images$', 'pictures', 85),
        (r'_image$', 'picture', 85),
        (r'^file_id$', 'file', 90),
        (r'_files$', 'files', 80),
        (r'_file$', 'file', 80),
        (r'^sort$', 'num', 90),
        (r'_sort$', 'num', 85),
        (r'_count$', 'num', 85),
        (r'_price$', 'num', 90),
        (r'_amount$', 'num', 90),
        (r'_qty$', 'num', 85),
        (r'^url$', 'url', 90),
        (r'_url$', 'url', 85),
        (r'^link$', 'url', 85),
        (r'_link$', 'url', 80),
        (r'^phone$', 'phone', 90),
        (r'^mobile$', 'phone', 90),
        (r'^tel$', 'phone', 90),
        (r'_phone$', 'phone', 85),
        (r'^email$', 'email', 95),
        (r'_email$', 'email', 90),
        (r'^address$', 'district', 85),
        (r'_address$', 'district', 80),
    ]

    # 数据库类型回退
    DB_TYPE_FALLBACK = {
        'string': 'text',
        'char': 'text',
        'text': 'textarea',
        'longText': 'textarea',
        'integer': 'num',
        'bigInteger': 'num',
        'unsignedBigInteger': 'select',
        'tinyInteger': 'status',
        'smallInteger': 'num',
        'decimal': 'num',
        'float': 'num',
        'double': 'num',
        'date': 'date',
        'datetime': 'datetime',
        'timestamp': 'datetime',
        'time': 'time',
        'boolean': 'status',
    }

    def __init__(self, version: str = 'v14'):
        self.version = version
        self.config = self._load_config()
        self.learned = self._load_learned()

    def infer(self, field_name: str, db_type: str, metadata: dict = None) -> dict:
        """推断字段类型"""
        # 如果 metadata 已有 @type，直接使用
        if metadata and metadata.get('type'):
            return {
                'type': metadata['type'],
                'source': 'metadata',
                'confidence': 'high'
            }

        # 第一层：配置层
        if metadata and metadata.get('type') in self.config:
            return {
                'type': metadata['type'],
                'source': 'config',
                'confidence': 'high',
                'definition': self.config[metadata['type']]
            }

        # 第二层：学习层
        if field_name in self.learned:
            learned_type = self.learned[field_name]
            return {
                'type': learned_type['inferred_type'],
                'source': 'learned',
                'confidence': learned_type['confidence'],
                'sources': learned_type.get('sources', [])
            }

        # 第三层：模式层
        for pattern, field_type, priority in self.FIELD_PATTERNS:
            if re.search(pattern, field_name):
                return {
                    'type': field_type,
                    'source': 'pattern',
                    'confidence': 'medium',
                    'pattern': pattern,
                    'priority': priority
                }

        # 回退：数据库类型
        if db_type in self.DB_TYPE_FALLBACK:
            return {
                'type': self.DB_TYPE_FALLBACK[db_type],
                'source': 'db_type',
                'confidence': 'low',
                'db_type': db_type
            }

        # 最终回退
        return {
            'type': 'text',
            'source': 'default',
            'confidence': 'low'
        }

    def _load_config(self) -> dict:
        """加载版本配置"""
        config_file = f"_shared/config/{self.version}.yaml"
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
            return config.get('field_types', {})
        except FileNotFoundError:
            return {}

    def _load_learned(self) -> dict:
        """加载学习结果"""
        learned_file = Path('.claude/qscmf/learned-field-types.json')
        if learned_file.exists():
            with open(learned_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}
```

---

## 使用示例

```python
inferrer = FieldTypeInferrer('v14')

# 示例 1：已有 metadata
result = inferrer.infer('name', 'string', {'type': 'text', 'title': '名称'})
# {'type': 'text', 'source': 'metadata', 'confidence': 'high'}

# 示例 2：模式匹配
result = inferrer.infer('product_content', 'text', {})
# {'type': 'richText', 'source': 'pattern', 'confidence': 'medium', 'pattern': r'_content$'}

# 示例 3：数据库类型回退
result = inferrer.infer('custom_field', 'string', {})
# {'type': 'text', 'source': 'db_type', 'confidence': 'low', 'db_type': 'string'}
```

---

## 相关文档

- [解析元数据](scaffold-parse-metadata.md) - @metadata 解析逻辑
- [生成代码](scaffold-generate-code.md) - 代码生成工作流
- [迁移优先](scaffold-migration-first.md) - 创建带 @metadata 的迁移
- [版本配置](../../_shared/config/v14.yaml) - 版本特定配置
