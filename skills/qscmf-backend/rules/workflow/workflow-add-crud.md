---
title: Workflow: Add CRUD to Existing Module
impact: HIGH
impactDescription: Core development workflow (15% daily usage)
tags: workflow, crud, scaffold, both, v13, v14
---

## Workflow: Add CRUD to Existing Module

End-to-end workflow for adding CRUD functionality to an existing database table in QSCMF.

### When to Use This Rule

- You have an existing database table and need CRUD functionality
- You want to generate Admin controller, Model, and optionally API
- You need to understand the complete CRUD development workflow
- You want to ensure best practices and avoid common pitfalls

---

## Prerequisites Checklist

Before starting CRUD development, ensure:

- [ ] **Migration file exists** for the table with @metadata annotations
- [ ] **Database table is created** by running migrations
- [ ] **QSCMF version is detected** (v13 or v14)
- [ ] **Field types are inferred** or manually specified
- [ ] **Required files are writable** (app/Common/Model/, app/Admin/Controller/)

---

## Step-by-Step Workflow

### Step 1: Verify Migration File

Find and check the migration file for your table:

```bash
# In QSCMF project root
cd /path/to/qscmf/project

# Find migration for table
ls lara/database/migrations/*create_{table_name}*.php

# Example
ls lara/database/migrations/*create_product*.php
# Output: 2024_01_15_123456_create_product_table.php
```

**Check migration has @metadata annotations:**

```php
<?php

use Illuminate\Database\Schema\Blueprint;
use Illuminate\Database\Migrations\Migration;

class CreateProductTable extends Migration
{
    public function up()
    {
        Schema::create('product', function (Blueprint $table) {
            $table->bigIncrements('id');

            // ✅ Good: Has @metadata
            $table->string('title', 200)->comment('@title=商品名称;@type=text;@length=1,200;@require=true;');
            $table->decimal('price', 10, 2)->comment('@title=价格;@type=num;@require=true;');
            $table->mediumInteger('cate_id')->comment('@title=分类;@type=select;@table=qs_category;@show=title;');
            $table->string('cover')->comment('@title=封面图;@type=picture;');
            $table->tinyInteger('status')->comment('@title=状态;@type=status;@list=status;@require=true;');

            $table->timestamps();
        });

        // Set table comment
        \DB::unprepared("ALTER TABLE `product` COMMENT = '@title=商品管理;'");
    }

    public function down()
    {
        Schema::dropIfExists('product');
    }
}
```

**❌ If migration lacks @metadata:**

> "Create migration for {table_name} with @metadata annotations including @title, @type for each field"

---

### Step 2: Run Migration

Ensure the table exists in the database:

```bash
# Run pending migrations
php artisan migrate

# Verify table exists
php artisan db:table product

# Or check directly
mysql -u root -p
USE your_database;
SHOW CREATE TABLE product;
```

---

### Step 3: Detect QSCMF Version

Check the QSCMF version to use correct templates:

```bash
# Check composer.json
cat composer.json | grep quansitech

# Or check version constant
grep "QSCMF_VERSION" app/Common/Conf/constant.php
```

**Version Detection:**
- **v13.3.0** → Use v13 ListBuilder (jQuery)
- **v14.0.2+** → Use v14 AntdAdmin (React)

---

### Step 4: Generate CRUD Code

Using the qscmf-backend skill with Claude Code:

> "生成 Product 模块的 CRUD，包括 Model 和 AdminController"

The skill will:
1. Analyze the migration file and extract @metadata
2. Infer field types (configuration → learning → default)
3. Generate code from templates
4. Write files to appropriate locations

**Generated files**:
- `app/Common/Model/ProductModel.class.php`
- `app/Admin/Controller/ProductController.class.php`

> **Tip**: Provide module name without `qs_` prefix. For table `qs_product`, use "生成 Product 模块的 CRUD" or

> "Create Product module with Admin CRUD and API"

> "Create Product module with Admin CRUD and API"

This will:
1. Parse migration metadata
2. Infer field types using three-layer strategy
3. Generate Model, AdminController, ApiController, Tests
4. Output TODO list for manual completion

---

### Step 5: Field Type Inference

Claude uses a three-layer strategy to infer field types:

#### Layer 1: Configuration Layer

```yaml
# .claude/qscmf/field-rules.yaml (project-specific)
field_overrides:
  product_name:
    type: text
    length: 200
    required: true
  sku_code:
    type: text
    regex: '/^[A-Z0-9\-]+$/'
```

#### Layer 2: Learning Layer

Claude scans existing controllers to learn patterns:

```php
// Found in app/Admin/Controller/CategoryController.class.php
$builder->addFormItem('name', 'text', '分类名称');
// Learns: fields ending in '_name' → text type
```

Saved to: `.claude/qscmf/learned-field-types.json`

#### Layer 3: Default Layer

Field name suffix patterns:

| Suffix | Type | Example |
|--------|------|---------|
| `*_content` | richText | `article_content` |
| `*_date` | date | `publish_date` |
| `*_time` | time | `start_time` |
| `*_at` | datetime | `created_at` |
| `status` | status | `status` |
| `*_status` | select | `audit_status` |
| `*_id` | select | `cate_id` |
| `cover`, `cover_id` | picture | `cover` |
| `*_image`, `*_images` | picture/pictures | `avatar`, `gallery_images` |
| `file_id` | file | `attachment_file_id` |
| `sort` | num | `sort` |
| `*_price`, `*_amount` | num | `unit_price`, `total_amount` |

---

### Step 6: Generated Files Structure

```
app/
├── Common/
│   └── Model/
│       └── ProductModel.class.php       # GyListModel with CRUD methods
├── Admin/
│   └── Controller/
│       └── ProductController.class.php  # QsListController (v13) or AdminController (v14)
└── Api/
    └── Controller/
        └── ProductController.class.php  # RestController (if requested)

lara/
└── tests/
    └── Feature/
        └── ProductTest.php              # PHPUnit tests (if requested)
```

---

### Step 7: Manual TODO Checklist

After code generation, complete these items manually:

#### 7.1 Table Columns Configuration

**For v13 (ListBuilder):**

- [ ] Add all table columns with correct types
- [ ] Configure search items
- [ ] Add top buttons (addnew, forbid, resume, delete)
- [ ] Add right buttons (edit, delete)
- [ ] Set page title and meta title

**For v14 (AntdAdmin):**

- [ ] Add all table columns (text, select, date, image, action)
- [ ] Configure search with correct types (like, exact, between)
- [ ] Set badges for status columns
- [ ] Configure action buttons
- [ ] Add custom renderers if needed

**Estimated time:** 15-30 minutes

#### 7.2 Form Fields Configuration

**For v13 (FormBuilder):**

- [ ] Add all form items with correct types
- [ ] Configure validation rules
- [ ] Set form layout
- [ ] Add custom form items if needed

**For v14 (AntdAdmin Form):**

- [ ] Add all form fields with validators
- [ ] Configure upload requests for files/images
- [ ] Set form item widths
- [ ] Add custom components if needed

**Estimated time:** 20-40 minutes

#### 7.3 Search Configuration

- [ ] Configure search items (refer to `crud-search-basic.md`)
- [ ] Implement search map in controller
- [ ] Test search functionality
- [ ] Add date range search if needed

**Estimated time:** 10-20 minutes

#### 7.4 Validation Rules

- [ ] Add `$_validate` rules to Model
- [ ] Configure client-side validators (v14)
- [ ] Test validation with invalid data
- [ ] Add custom callbacks for complex validation

**Estimated time:** 15-30 minutes

#### 7.5 Business Logic

- [ ] Implement before/after hooks
- [ ] Add data processing logic
- [ ] Implement related data operations
- [ ] Add transaction handling if needed

**Estimated time:** 30-60 minutes (varies by complexity)

#### 7.6 Tests

- [ ] Write PHPUnit tests
- [ ] Test CRUD operations
- [ ] Test validation
- [ ] Test edge cases

**Estimated time:** 30-60 minutes

---

## Complete Working Example

### Scenario: Add CRUD for Product Table

#### 1. Migration File

```php
<?php
// lara/database/migrations/2024_01_15_123456_create_product_table.php

use Illuminate\Database\Schema\Blueprint;
use Illuminate\Database\Migrations\Migration;

class CreateProductTable extends Migration
{
    public function up()
    {
        Schema::create('product', function (Blueprint $table) {
            $table->bigIncrements('id');

            $table->string('title', 200)->comment('@title=商品名称;@type=text;@length=1,200;@require=true;@save=true;');
            $table->string('sku', 50)->comment('@title=商品编码;@type=text;@length=1,50;@require=true;');
            $table->mediumInteger('cate_id')->comment('@title=分类;@type=select;@table=qs_category;@show=title;@require=true;');
            $table->decimal('price', 10, 2)->comment('@title=价格;@type=num;@require=true;');
            $table->integer('stock')->comment('@title=库存;@type=num;@save=true;');
            $table->string('cover')->comment('@title=封面图;@type=picture;');
            $table->text('summary')->comment('@title=摘要;@type=textarea;');
            $table->text('content')->comment('@title=商品详情;@type=richText;@oss=true;');
            $table->tinyInteger('is_recommend')->comment('@title=推荐;@type=radio;@list=boolStatus;@save=true;');
            $table->tinyInteger('is_hot')->comment('@title=热门;@type=radio;@list=boolStatus;@save=true;');
            $table->tinyInteger('status')->comment('@title=状态;@type=status;@list=status;@require=true;@save=true;');
            $table->integer('sort')->comment('@title=排序;@type=num;@save=true;');

            $table->timestamps();
        });

        \DB::unprepared("ALTER TABLE `product` COMMENT = '@title=商品管理;'");
    }

    public function down()
    {
        Schema::dropIfExists('product');
    }
}
```

#### 2. Run Migration

```bash
php artisan migrate
```

#### 3. Generate CRUD

Ask Claude Code:

> "生成 Product 模块的 CRUD 代码，基于 product 表"

The skill will generate the following files:

#### 4. Generated Model

```php
<?php
// app/Common/Model/ProductModel.class.php

class ProductModel extends \Gy_Library\GyListModel
{
    protected $_validate = [
        ['title', 'require', '商品名称不能为空', self::MUST_VALIDATE],
        ['title', '1,200', '商品名称1-200字符', self::MUST_VALIDATE, 'length'],
        ['sku', 'require', '商品编码不能为空', self::MUST_VALIDATE],
        ['sku', 'checkSkuUnique', '商品编码已存在', self::MUST_VALIDATE, 'callback'],
        ['price', 'require', '价格不能为空', self::MUST_VALIDATE],
        ['price', '0,999999', '价格范围错误', self::MUST_VALIDATE, 'between'],
        ['cate_id', 'require', '分类不能为空', self::MUST_VALIDATE],
        ['status', '0,1', '状态值错误', self::MUST_VALIDATE, 'in'],
    ];

    protected function checkSkuUnique($sku)
    {
        $map['sku'] = $sku;
        if (isset($this->id)) {
            $map['id'] = ['neq', $this->id];
        }
        return !$this->where($map)->find();
    }

    protected $_auto = [
        ['create_time', 'time', self::MODEL_INSERT],
        ['update_time', 'time', self::MODEL_UPDATE],
    ];

    // Get category options
    public function getCateOptions()
    {
        return D('Category')->getFields();
    }

    // Get related category
    public function getCategory()
    {
        if ($this->cate_id) {
            return D('Category')->find($this->cate_id);
        }
        return null;
    }
}
```

#### 5. Generated Controller (v14)

```php
<?php
// app/Admin/Controller/ProductController.class.php

use Qscmf\Lib\AntdAdmin\AdminController;

class ProductController extends AdminController
{
    protected function buildTableColumns($container)
    {
        // ID column
        $container->text('id', 'ID')
            ->setSortable(true)
            ->setWidth(80);

        // Product name with search
        $container->text('title', '商品名称')
            ->setSearch(true)
            ->setSearchType('like')
            ->setSearchPlaceholder('搜索商品名称')
            ->setSortable(true)
            ->setWidth(200)
            ->setEllipsis(true);

        // SKU with search
        $container->text('sku', '商品编码')
            ->setSearch(true)
            ->setSearchType('exact')
            ->setWidth(120);

        // Category with search
        $container->select('cate_id', '分类')
            ->setValueEnum(D('Product')->getCateOptions())
            ->setSearch(true)
            ->setSearchType('exact')
            ->setWidth(100);

        // Cover image
        $container->image('cover', '封面')
            ->setWidth(80)
            ->setHeight(60);

        // Price with search and inline edit
        $container->number('price', '价格')
            ->setSearch(true)
            ->setSearchType('between')
            ->setSortable(true)
            ->setWidth(100)
            ->editable();

        // Stock with inline edit
        $container->number('stock', '库存')
            ->setSearch(true)
            ->setSearchType('between')
            ->setSortable(true)
            ->setWidth(80)
            ->editable();

        // Status with badge and inline edit
        $container->select('status', '状态')
            ->setValueEnum(DBCont::getStatusList())
            ->setBadge([1 => 'success', 0 => 'default'])
            ->setSearch(true)
            ->setSearchType('exact')
            ->setWidth(80)
            ->editable();

        // Sort with inline edit
        $container->number('sort', '排序')
            ->setSortable(true)
            ->setWidth(80)
            ->editable();

        // Create time
        $container->date('create_time', '创建时间')
            ->setSearch(true)
            ->setSearchType('between')
            ->setFormat('Y-m-d H:i:s')
            ->setWidth(180);

        // Action column
        $container->action('', '操作')
            ->setParams(['id' => 'id'])
            ->setWidth(150)
            ->actions(function ($actions) {
                $actions->edit()
                    ->modal((new \Qscmf\Lib\AntdAdmin\Layouts\FormBuilder\Modal())
                        ->setWidth('900px')
                        ->setUrl(U('edit', ['id' => '__id__']))
                        ->setTitle('编辑商品'));

                $actions->delete();
            });
    }

    public function index()
    {
        $container = new \Qscmf\Lib\AntdAdmin\Layouts\Table\TableContainer();
        $this->buildTableColumns($container);

        $container->setDataSource(U('getListData'));
        $container->setPagination([
            'pageSize' => 20,
            'showSizeChanger' => true,
        ]);

        return $this->display($container);
    }
}
```

#### 6. Manual TODO Items (Completed)

**Table Columns:** ✅ Completed in `buildTableColumns()`

**Form Fields:** Need to implement `buildFormColumns()`

```php
protected function buildFormColumns($container)
{
    $container->text('title', '商品名称')
        ->addRule(new Required('商品名称不能为空'))
        ->addRule(new Length(1, 200, '1-200字符'))
        ->setFormItemWidth('100%');

    $container->text('sku', '商品编码')
        ->addRule(new Required('商品编码不能为空'))
        ->addRule(new Length(1, 50, '1-50字符'))
        ->setFormItemWidth('50%');

    $container->select('cate_id', '分类')
        ->setValueEnum(D('Product')->getCateOptions())
        ->addRule(new Required('请选择分类'))
        ->setFormItemWidth('50%');

    $container->number('price', '价格')
        ->addRule(new Required('请输入价格'))
        ->addRule(new Number()->min(0)->max(999999), '价格范围0-999999')
        ->setFormItemWidth('50%');

    $container->number('stock', '库存')
        ->addRule(new Number()->min(0), '库存不能为负数')
        ->setFormItemWidth('50%');

    $container->image('cover', '封面图')
        ->setFormItemWidth('50%');

    $container->textarea('summary', '摘要')
        ->setRows(4)
        ->setFormItemWidth('100%');

    $container->rich_text('content', '商品详情')
        ->setFormItemWidth('100%')
        ->setHeight('500px');

    $container->radio('is_recommend', '推荐')
        ->setValueEnum(DBCont::getBoolStatusList())
        ->setFormItemWidth('25%');

    $container->radio('is_hot', '热门')
        ->setValueEnum(DBCont::getBoolStatusList())
        ->setFormItemWidth('25%');

    $container->select('status', '状态')
        ->setValueEnum(DBCont::getStatusList())
        ->addRule(new Required('请选择状态'))
        ->setFormItemWidth('25%');

    $container->number('sort', '排序')
        ->setFormItemWidth('25%');
}
```

**Estimated completion time:** 30 minutes

---

## Common Pitfalls and Solutions

### Pitfall 1: Missing @metadata Annotations

**Problem:** Generated code has incorrect field types.

**Solution:** Always add @metadata to migration before generating CRUD.

```php
// ❌ Wrong
$table->string('title')->comment('标题');

// ✅ Correct
$table->string('title')->comment('@title=标题;@type=text;@require=true;');
```

### Pitfall 2: Wrong Table Name

**Problem:** Cannot find generated files or errors occur.

**Solution:** Use exact table name without prefix when prompting.

> ❌ "生成 qs_product 模块的 CRUD"
>
> ✅ "生成 product 模块的 CRUD"

**Explanation:** The skill extracts module name from table name by removing the `qs_` prefix. Always refer to the module name in prompts.

### Pitfall 3: Foreign Key Fields

**Problem:** Select fields don't show correct options.

**Solution:** Ensure @table and @show are specified.

```php
// ❌ Missing @show
$table->mediumInteger('cate_id')->comment('@title=分类;@type=select;@table=qs_category;');

// ✅ Complete
$table->mediumInteger('cate_id')->comment('@title=分类;@type=select;@table=qs_category;@show=title;');
```

### Pitfall 4: Rich Text OSS

**Problem:** Rich text images don't upload correctly.

**Solution:** Add @oss=true if using OSS.

```php
// For OSS storage
$table->text('content')->comment('@title=内容;@type=richText;@oss=true;');

// For default imageproxy
$table->text('content')->comment('@title=内容;@type=richText;');
```

### Pitfall 5: Inline Edit Not Working

**Problem:** Cannot edit fields in list view.

**Solution:** Add @save=true to migration metadata.

```php
$table->integer('sort')->comment('@title=排序;@type=num;@save=true;');
$table->string('title')->comment('@title=标题;@type=text;@save=true;');
```

### Pitfall 6: Validation Not Working

**Problem:** Invalid data can be saved.

**Solution:** Add both server-side and client-side validation.

```php
// Server-side (Model)
protected $_validate = [
    ['title', 'require', '标题不能为空', self::MUST_VALIDATE],
];

// Client-side (v14 Form)
$container->text('title', '标题')
    ->addRule(new Required('标题不能为空'));
```

### Pitfall 7: Date Search Not Working

**Problem:** Date range search doesn't filter data.

**Solution:** Implement search map in controller.

```php
protected function buildSearchMap()
{
    $map = [];

    if ($start_time = I('get.create_time_start')) {
        $map['create_time'][] = ['egt', strtotime($start_time)];
    }
    if ($end_time = I('get.create_time_end')) {
        $map['create_time'][] = ['elt', strtotime($end_time)];
    }

    return $map;
}
```

---

## Testing Checklist

After completing manual TODO items, test the CRUD functionality:

### Basic CRUD Operations

- [ ] **List page loads** without errors
- [ ] **Search works** for all configured search items
- [ ] **Pagination works** correctly
- [ ] **Sort works** on sortable columns
- [ ] **Add new** opens form and saves correctly
- [ ] **Edit** opens form with data and saves correctly
- [ ] **Delete** removes record after confirmation
- [ ] **Status toggle** works (if enabled)

### Validation Testing

- [ ] **Required fields** show errors when empty
- [ ] **Length validation** prevents too long/short input
- [ ] **Format validation** (email, url, phone) works
- [ ] **Unique validation** prevents duplicates
- [ ] **Custom validation** callbacks work correctly

### Edge Cases

- [ ] **Empty database** shows empty state correctly
- [ ] **Large dataset** (1000+ records) performs well
- [ ] **Special characters** are handled correctly
- [ ] **Foreign keys** reference valid data
- [ ] **Concurrent edits** don't cause conflicts

---

## Version-Specific Considerations

### v13 (ListBuilder - jQuery)

**Key Differences:**

- Use `addTableColumn()` instead of `text()`, `select()`
- Use `addFormItem()` for form fields
- Custom renderers use `'fun'` type with callback
- Inline edit via `@save=true` metadata only

**Generated Controller Base:**

```php
class ProductController extends \Qscmf\Builder\FormBuilder\QsListController
{
    protected function buildListOptions($builder)
    {
        $builder->setMetaTitle('商品列表');
        $builder->addTableColumn('id', 'ID');
        $builder->addTableColumn('title', '商品名称');
        // ...
    }
}
```

### v14 (AntdAdmin - React)

**Key Differences:**

- Use `text()`, `select()`, `date()` methods
- Use `addRule()` with Validator classes
- Custom renderers via `setRenderer()` with React components
- Full inline editing support with `editable()`

**Generated Controller Base:**

```php
class ProductController extends \Qscmf\Lib\AntdAdmin\AdminController
{
    protected function buildTableColumns($container)
    {
        $container->text('id', 'ID');
        $container->text('title', '商品名称');
        // ...
    }
}
```

---

## Related Rules

- [Table Columns v13](./crud-table-columns-v13.md) - ListBuilder complete API
- [Table Columns v14](./crud-table-columns-v14.md) - AntdAdmin complete API
- [Form Validation](./crud-form-validation.md) - Validation rules reference
- [Search Configuration](./crud-search-basic.md) - Search types and patterns
- [Migration Guide](../../references/migration-guide.md) - Metadata system
- [Admin Controllers](../../references/admin-controllers.md) - Controller patterns

---

## Iron Law

```
NO ADMIN CRUD WITHOUT MIGRATION METADATA FIRST
```

Always ensure migration files have proper @metadata annotations before generating CRUD code. This is the foundation of the entire code generation system.

---

## Quick Reference Commands

```bash
# Find migration
ls lara/database/migrations/*create_{table}*.php

# Run migration
php artisan migrate

# Rollback migration
php artisan migrate:rollback

# Generate CRUD (ask Claude Code)
> "生成 {模块名} 模块的 CRUD 代码"

# Run tests
vendor/bin/phpunit lara/tests/Feature/{Model}Test.php

# Check table structure
php artisan db:table {table_name}
```

---

## Best Practices

1. **Always add @metadata** to migration before generating CRUD
2. **Use descriptive titles** for better UX
3. **Set correct field types** based on data usage patterns
4. **Add validation** to both Model and Form
5. **Test thoroughly** after generation
6. **Implement search** for frequently filtered fields
7. **Use inline edit** for frequently updated fields
8. **Add foreign key constraints** for data integrity
9. **Write tests** for critical business logic
10. **Keep controllers thin** - move business logic to Model
