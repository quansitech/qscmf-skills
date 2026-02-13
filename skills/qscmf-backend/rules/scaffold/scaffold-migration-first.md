---
title: Migration First for Code Generation
impact: CRITICAL
impactDescription: Required; 100% of scaffold operations depend on this
tags: scaffold, migration, metadata, code-generation, both
---

## Migration First for Code Generation

**Impact: CRITICAL (Required for all scaffold operations)**

Always ensure migration file with @metadata exists before generating any code.

### When to Use This Rule

- You need to generate CRUD code for a table
- You need to understand the @metadata annotation system
- You want to ensure proper field type inference
- You need to create database tables with proper schema

---

## Why Migration First?

### Benefits of Migration-First Approach

| Benefit | Description |
|---------|-------------|
| **Single Source of Truth** | Migration defines table structure and metadata in one place |
| **Version Control** | Schema changes tracked in git |
| **Automated Inference** | @metadata enables intelligent field type detection |
| **Consistency** | Code generation always matches actual database |
| **Team Collaboration** | Developers can generate code without asking for schema details |

### Without @metadata

```markdown
User: "生成 Product CRUD"
AI: What fields does Product have?
User: name, price, status
AI: What types?
User: varchar, decimal, int
AI: Validation rules? Required? Length?
... (5 minutes of Q&A)
```

### With @metadata

```markdown
User: "生成 Product CRUD"
AI: ✅ Reads migration, parses @metadata, generates code
Total time: 30 seconds
```

---

## @metadata Annotation System

### Complete Attribute Reference

| Attribute | Required | Values | Description | Example |
|-----------|-----------|---------|-------------|---------|
| **@title** | ✅ Yes | Any string | Display label (Chinese recommended) | `@title=产品名称;` |
| **@type** | ✅ Yes | See field types below | Form field type | `@type=text;` |
| **@require** | Optional | `true`, `false` | Mark as required | `@require=true;` |
| **@length** | Optional | `min,max` | Validation length range | `@length=1,200;` |
| **@save** | Optional | `true`, `false` | Enable inline edit | `@save=true;` |
| **@table** | For select | Table name | Foreign key table | `@table=qs_category;` |
| **@show** | For select | Field name | Display field from FK table | `@show=title;` |
| **@list** | For select/checkbox/radio | Variable name | DBCont static variable | `@list=status;` |
| **@oss** | For richText | `true`, `false` | Use OSS for uploads | `@oss=true;` |

### Field Types (17 Total)

| Type | Database Column | Description | @type Value |
|------|----------------|-------------|-------------|
| **Text Input** | varchar, char | Single line text | `text` |
| **Textarea** | text | Multi-line text | `textarea` |
| **Select (FK)** | int | Foreign key dropdown | `select` |
| **Select (Enum)** | tinyint, int | Enum dropdown (DBCont) | `select` |
| **Radio** | tinyint, int | Radio button group | `radio` |
| **Checkbox** | varchar, text | Multiple selections | `checkbox` |
| **Date** | date, datetime | Date picker | `date` |
| **Time** | time | Time picker | `time` |
| **DateTime** | datetime | DateTime picker | `datetime` |
| **Number** | int, decimal, float | Number input | `num` |
| **File** | varchar | Single file upload | `file` |
| **Files** | varchar, text | Multiple files | `files` |
| **Picture** | varchar | Single image upload | `picture` |
| **Pictures** | varchar, text | Multiple images | `pictures` |
| **Rich Text** | text | Rich text editor | `richText` |
| **URL** | varchar | URL input | `url` |
| **Phone** | varchar | Phone number | `phone` |
| **Email** | varchar | Email input | `email` |
| **District** | int | China district selector | `district` |
| **Status** | tinyint | Boolean switch | `status` |

---

## Creating Migration with @metadata

### Step 1: Generate Migration File

```bash
# In QSCMF project root
php artisan make:migration create_product_table

# Output: lara/database/migrations/2024_01_15_123456_create_product_table.php
```

### Step 2: Edit Migration File

```php
<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    public function up(): void
    {
        Schema::create('qs_product', function (Blueprint $table) {
            $table->id();
            $table->string('name', 200)->comment('@title=产品名称;@type=text;@length=1,200;@require=true;');
            $table->string('sku', 50)->comment('@title=产品编码;@type=text;@length=1,50;@require=true;');
            $table->decimal('price', 10, 2)->comment('@title=价格;@type=num;@require=true;');
            $table->text('description')->comment('@title=描述;@type=textarea;');
            $table->unsignedBigInteger('category_id')->comment('@title=分类;@type=select;@table=qs_category;@show=title;');
            $table->tinyInteger('status')->default(1)->comment('@title=状态;@type=status;@list=status;');
            $table->integer('sort')->default(0)->comment('@title=排序;@type=num;@save=true;');
            $table->string('cover', 255)->nullable()->comment('@title=封面图;@type=picture;');
            $table->text('images')->nullable()->comment('@title=产品图片;@type=pictures;');
            $table->timestamps();
        });
    }

    public function down(): void
    {
        Schema::dropIfExists('qs_product');
    }
};
```

### Step 3: Run Migration

```bash
# Run pending migrations
php artisan migrate

# Verify table created
mysql -u root -p
> USE your_database;
> SHOW CREATE TABLE qs_product;

# Or use Laravel command
php artisan db:table product
```

---

## @metadata Usage Examples

### Example 1: Basic Product Table

```php
Schema::create('qs_product', function (Blueprint $table) {
    $table->id();

    // Required text field
    $table->string('name', 200)->comment('@title=产品名称;@type=text;@length=1,200;@require=true;');

    // Optional text field
    $table->string('sku', 50)->nullable()->comment('@title=产品编码;@type=text;');

    // Required number field
    $table->decimal('price', 10, 2)->comment('@title=价格;@type=num;@require=true;');

    // Textarea
    $table->text('description')->comment('@title=描述;@type=textarea;');

    // Foreign key select
    $table->unsignedBigInteger('category_id')
        ->comment('@title=分类;@type=select;@table=qs_category;@show=title;');

    // Status with DBCont
    $table->tinyInteger('status')
        ->default(1)
        ->comment('@title=状态;@type=status;@list=status;');

    $table->timestamps();
});
```

### Example 2: User Table with Multiple Field Types

```php
Schema::create('qs_user', function (Blueprint $table) {
    $table->id();

    // Username
    $table->string('username', 50)->comment('@title=用户名;@type=text;@length=3,50;@require=true;');

    // Email with validation
    $table->string('email', 100)->comment('@title=邮箱;@type=email;@require=true;');

    // Phone number
    $table->string('phone', 20)->nullable()->comment('@title=手机号;@type=phone;');

    // Avatar (single image)
    $table->string('avatar', 255)->nullable()->comment('@title=头像;@type=picture;');

    // Gender (radio with DBCont)
    $table->tinyInteger('gender')
        ->default(0)
        ->comment('@title=性别;@type=radio;@list=gender;');

    // District selector
    $table->integer('district')->nullable()->comment('@title=地区;@type=district;');

    // Status
    $table->tinyInteger('status')
        ->default(1)
        ->comment('@title=状态;@type=status;@list=status;');

    $table->timestamps();
});
```

### Example 3: Article Table with Rich Text

```php
Schema::create('qs_article', function (Blueprint $table) {
    $table->id();

    // Title
    $table->string('title', 200)->comment('@title=标题;@type=text;@length=1,200;@require=true;');

    // Category (foreign key)
    $table->unsignedBigInteger('category_id')
        ->comment('@title=分类;@type=select;@table=qs_category;@show=title;');

    // Tags (multiple select)
    $table->string('tags', 255)->nullable()->comment('@title=标签;@type=checkbox;@list=tags;');

    // Thumbnail
    $table->string('thumb', 255)->nullable()->comment('@title=缩略图;@type=picture;');

    // Images (multiple)
    $table->text('images')->nullable()->comment('@title=图片;@type=pictures;');

    // Content (rich text with OSS)
    $table->text('content')->comment('@title=内容;@type=richText;@oss=true;');

    // Author
    $table->unsignedBigInteger('author_id')
        ->comment('@title=作者;@type=select;@table=qs_user;@show=username;');

    // Publish date
    $table->datetime('publish_time')->nullable()->comment('@title=发布时间;@type=datetime;');

    // Status
    $table->tinyInteger('status')
        ->default(0)
        ->comment('@title=状态;@type=status;@list=status;');

    // View count (inline editable)
    $table->integer('views')->default(0)->comment('@title=浏览量;@type=num;@save=true;');

    $table->timestamps();
});
```

### Example 4: Order Table with Various Inputs

```php
Schema::create('qs_order', function (Blueprint $table) {
    $table->id();

    // Order number (exact match search)
    $table->string('order_no', 50)->unique()
        ->comment('@title=订单号;@type=text;@require=true;');

    // Customer (foreign key)
    $table->unsignedBigInteger('user_id')
        ->comment('@title=客户;@type=select;@table=qs_user;@show=username;');

    // Total amount
    $table->decimal('total_amount', 10, 2)
        ->comment('@title=总金额;@type=num;@require=true;');

    // Payment method (select)
    $table->string('payment_method', 50)
        ->comment('@title=支付方式;@type=select;@list=payment_method;');

    // Payment time
    $table->datetime('payment_time')->nullable()
        ->comment('@title=支付时间;@type=datetime;');

    // Shipping address (textarea)
    $table->text('shipping_address')->nullable()
        ->comment('@title=收货地址;@type=textarea;');

    // Order status (select)
    $table->tinyInteger('order_status')
        ->default(0)
        ->comment('@title=订单状态;@type=select;@list=order_status;');

    // Notes (textarea)
    $table->text('notes')->nullable()
        ->comment('@title=备注;@type=textarea;');

    $table->timestamps();
});
```

---

## Field Type Inference System

QSCMF skill uses a three-layer strategy to infer field types from migration:

### Layer 1: Configuration Layer (Highest Priority)

**File:** `.claude/qscmf/field-rules.yaml`

```yaml
# Project-specific field type overrides
product_name: text
user_email: email
user_phone: phone
article_content: richText
```

### Layer 2: Learning Layer

**File:** `.claude/qscmf/learned-field-types.json`

Auto-generated from scanning existing controllers:

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
    "foreign_key": true
  }
}
```

### Layer 3: Default Layer (Field Name Patterns)

| Pattern | Type | Example |
|---------|-------|---------|
| `*_content` | richText | article_content |
| `*_desc` or `*description` | textarea | product_desc |
| `*_time` or `*_date` or `*_at` | date/datetime | create_time, publish_date |
| `*_id` | select (foreign key) | category_id, user_id |
| `status` | status | status |
| `*_sort` or `sort` | num | sort, display_sort |
| `*_url` or `url` | url | site_url |
| `*_email` or `email` | email | user_email |
| `*_phone` or `phone` | phone | contact_phone |
| `cover` or `thumb` | picture | cover, thumb |
| `*_image` or `*_images` or `images` | pictures | product_images |
| `*_file` or `*_files` or `files` | files | attachment_files |

---

## Common @metadata Pitfalls

### Pitfall 1: Missing Semicolon

```php
// ❌ Wrong
$table->string('name')->comment('@title=名称;@type=text')

// ✅ Correct
$table->string('name')->comment('@title=名称;@type=text;');
```

### Pitfall 2: Missing Required Attributes

```php
// ❌ Wrong (no @title)
$table->string('name')->comment('@type=text;');

// ✅ Correct
$table->string('name')->comment('@title=名称;@type=text;');
```

### Pitfall 3: Wrong Table Name

```php
// ❌ Wrong (with qs_ prefix)
$table->unsignedBigInteger('category_id')
    ->comment('@title=分类;@type=select;@table=qs_category;@show=title;');

// ✅ Correct (without qs_ prefix)
$table->unsignedBigInteger('category_id')
    ->comment('@title=分类;@type=select;@table=category;@show=title;');
```

### Pitfall 4: Invalid Field Type

```php
// ❌ Wrong (type doesn't exist)
$table->string('name')->comment('@title=名称;@type=string;');

// ✅ Correct
$table->string('name')->comment('@title=名称;@type=text;');
```

### Pitfall 5: Forgetting nullable() for Optional Fields

```php
// ❌ Wrong (not nullable, will fail on INSERT)
$table->string('cover')->comment('@title=封面;@type=picture;');

// ✅ Correct
$table->string('cover')->nullable()->comment('@title=封面;@type=picture;');
```

---

## Migration Management Best Practices

### 1. Always Use Descriptive Comments

```php
// Good - Chinese title, clear type
$table->string('product_name', 200)->comment('@title=产品名称;@type=text;@length=1,200;@require=true;');

// Bad - unclear, no type
$table->string('name', 200)->comment('name');
```

### 2. Set Appropriate Defaults

```php
// Status defaults to enabled
$table->tinyInteger('status')->default(1)->comment('@title=状态;@type=status;@list=status;');

// Sort defaults to 0
$table->integer('sort')->default(0)->comment('@title=排序;@type=num;@save=true;');
```

### 3. Use Proper Column Types

| Data | MySQL Type | Laravel Method | @type |
|-------|------------|-----------------|--------|
| Short text | varchar(255) | `string($name, $length)` | text |
| Long text | text | `text($name)` | textarea |
| Integer IDs | int(11) | `unsignedBigInteger($name)` | select (FK) |
| Decimals | decimal(10,2) | `decimal($name, $total, $places)` | num |
| Boolean | tinyint(1) | `tinyInteger($name)` | status |
| Dates | datetime | `datetime($name)` | datetime |
| Timestamps | timestamp | `timestamps()` | - |

### 4. Add Indexes for Searchable Fields

```php
Schema::create('qs_product', function (Blueprint $table) {
    $table->id();

    $table->string('name', 200)->comment('@title=产品名称;@type=text;');
    $table->index('name'); // For LIKE search

    $table->unsignedBigInteger('category_id')->comment('@title=分类;@type=select;');
    $table->index('category_id'); // For JOIN and WHERE

    $table->tinyInteger('status')->default(1)->comment('@title=状态;@type=status;');
    $table->index('status'); // For filtering

    $table->timestamps();
});
```

### 5. Use Foreign Key Constraints (Optional)

```php
Schema::create('qs_product', function (Blueprint $table) {
    $table->id();

    $table->unsignedBigInteger('category_id')
        ->comment('@title=分类;@type=select;@table=category;@show=title;');

    $table->foreign('category_id')
        ->references('id')
        ->on('qs_category')
        ->onDelete('cascade');

    $table->timestamps();
});
```

---

## Troubleshooting

| Problem | Cause | Solution |
|---------|--------|----------|
| Migration not found | Wrong table name or file not created | Use exact table name without `qs_` prefix in prompts |
| @metadata not parsed | Missing semicolon or wrong format | Ensure all attributes end with `;` |
| Field type wrong | Invalid @type value | Check valid types list (17 total) |
| Foreign key not working | Wrong @table name | Use table name without `qs_` prefix |
| DBCont not found | Wrong @list value | Check DBCont class for static variable name |
| Code generation fails | Migration doesn't exist in database | Run `php artisan migrate` first |
| Nullable constraint error | Missing `nullable()` for optional fields | Add `->nullable()` before `->comment()` |

---

## Complete Working Example

### E-commerce Product Table

```php
<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    public function up(): void
    {
        Schema::create('qs_product', function (Blueprint $table) {
            // Primary key
            $table->id();

            // Basic information
            $table->string('name', 200)->comment('@title=产品名称;@type=text;@length=1,200;@require=true;');
            $table->string('sku', 50)->unique()->comment('@title=产品编码;@type=text;@length=1,50;@require=true;');
            $table->decimal('price', 10, 2)->comment('@title=价格;@type=num;@require=true;');
            $table->decimal('market_price', 10, 2)->nullable()->comment('@title=市场价;@type=num;');
            $table->text('description')->nullable()->comment('@title=描述;@type=textarea;');

            // Category and brand
            $table->unsignedBigInteger('category_id')
                ->comment('@title=分类;@type=select;@table=category;@show=title;');
            $table->unsignedBigInteger('brand_id')
                ->nullable()
                ->comment('@title=品牌;@type=select;@table=brand;@show=name;');

            // Media
            $table->string('cover', 255)->nullable()->comment('@title=封面图;@type=picture;');
            $table->text('images')->nullable()->comment('@title=产品图片;@type=pictures;');

            // Inventory
            $table->integer('stock')->default(0)->comment('@title=库存;@type=num;@save=true;');
            $table->integer('sales')->default(0)->comment('@title=销量;@type=num;');

            // Attributes
            $table->tinyInteger('is_new')->default(0)->comment('@title=新品;@type=status;@list=yes_no;');
            $table->tinyInteger('is_hot')->default(0)->comment('@title=热销;@type=status;@list=yes_no;');
            $table->tinyInteger('is_recommend')->default(0)->comment('@title=推荐;@type=status;@list=yes_no;');

            // SEO
            $table->string('seo_title', 200)->nullable()->comment('@title=SEO标题;@type=text;');
            $table->text('seo_keywords')->nullable()->comment('@title=SEO关键词;@type=textarea;');
            $table->text('seo_description')->nullable()->comment('@title=SEO描述;@type=textarea;');

            // Sorting and status
            $table->integer('sort')->default(0)->comment('@title=排序;@type=num;@save=true;');
            $table->tinyInteger('status')->default(1)->comment('@title=状态;@type=status;@list=status;');

            // Timestamps
            $table->timestamps();

            // Indexes
            $table->index('name');
            $table->index('category_id');
            $table->index('brand_id');
            $table->index('status');
            $table->index('sort');
        });
    }

    public function down(): void
    {
        Schema::dropIfExists('qs_product');
    }
};
```

### After Migration

Now you can generate code:

```markdown
User: "生成 Product CRUD"

AI Actions:
1. ✅ Found migration: lara/database/migrations/xxxx_create_product_table.php
2. ✅ Parsed @metadata from all 24 fields
3. ✅ Inferred field types (text, select, picture, pictures, num, status)
4. ✅ Generated ProductModel.class.php
5. ✅ Generated ProductController.class.php (v14 AntdAdmin)
6. ✅ Generated ProductTest.php

Generated files:
- app/Common/Model/ProductModel.class.php
- app/Admin/Controller/ProductController.class.php
- lara/tests/Feature/ProductTest.php

TODO (manual):
- [ ] Run migration: php artisan migrate
- [ ] Configure permissions in qs_node table
- [ ] Add validation rules in Model::$_validate
- [ ] Implement business logic (save, delete hooks)
- [ ] Run tests: vendor/bin/phpunit
```

---

## See Also

- [Infer Field Types](scaffold-infer-types.md) - Field type inference system
- [Parse Migration Metadata](scaffold-parse-metadata.md) - @metadata parsing logic
- [Add CRUD Workflow](../workflow/workflow-add-crud.md) - Complete CRUD workflow
- [Create Module Workflow](../workflow/workflow-create-module.md) - End-to-end module creation
- [Field Type Reference](../../_shared/config/v14.yaml) - Complete field type mappings

---

## Iron Law

```
NO MIGRATION METADATA, NO CODE GENERATION
```

**Always check:**
1. ✅ Migration file exists: `ls lara/database/migrations/*create_{table}*`
2. ✅ Migration has @metadata: grep '@title' lara/database/migrations/*create_{table}*
3. ✅ Migration is applied: `php artisan migrate:status`

**Only then:**
4. ✅ Generate code: "生成 {Table} CRUD"
