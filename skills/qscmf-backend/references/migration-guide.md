# Migration Guide

> QSCMF 数据库迁移文件完整指南 - Laravel Schema Builder

## 迁移命令

### 创建迁移

```bash
# 创建新迁移
php artisan make:migration create_xxx_table

# 指定表名（带 qs_ 前缀）
php artisan make:migration create_product_table
# 生成: lara/database/migrations/xxxx_create_product_table.php
```

### 运行迁移

```bash
# 执行所有待执行的迁移
php artisan migrate

# 回滚最后一次迁移
php artisan migrate:rollback

# 回滚后重新运行所有迁移
php artisan migrate:refresh

# 查看迁移状态
php artisan migrate:status
```

## 迁移文件结构

```php
<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    public function up()
    {
        Schema::create('qs_product', function (Blueprint $table) {
            $table->bigIncrements('id');
            $table->string('product_name', 200)->comment('产品名称');
            $table->text('description')->nullable()->comment('产品描述');
            $table->decimal('price', 10, 2)->default(0)->comment('价格');
            $table->bigInteger('cate_id')->default(0)->comment('分类ID');
            $table->string('cover', 500)->nullable()->comment('封面图');
            $table->tinyInteger('status')->default(1)->comment('状态 0禁用 1启用');
            $table->integer('sort')->default(0)->comment('排序');
            $table->timestamps();

            // 索引
            $table->index('cate_id');
            $table->index('status');
        });
    }

    public function down()
    {
        Schema::dropIfExists('qs_product');
    }
};
```

## 列类型参考

| 类型 | Schema 方法 | MySQL 类型 | 说明 |
|------|------------|-----------|------|
| 主键 | `$table->bigIncrements('id')` | BIGINT UNSIGNED AUTO_INCREMENT | 自增主键 |
| 字符串 | `$table->string('name', 200)` | VARCHAR(200) | 变长字符串 |
| 文本 | `$table->text('content')` | TEXT | 长文本 |
| 长文本 | `$table->longText('body')` | LONGTEXT | 超长文本 |
| 整数 | `$table->integer('count')` | INT | 整数 |
| 大整数 | `$table->bigInteger('user_id')` | BIGINT | 大整数（外键） |
| 小整数 | `$table->tinyInteger('status')` | TINYINT | 小整数（状态） |
| 布尔 | `$table->boolean('is_active')` | TINYINT(1) | 布尔值 |
| 小数 | `$table->decimal('price', 10, 2)` | DECIMAL(10,2) | 精确小数 |
| 浮点 | `$table->float('rate')` | FLOAT | 浮点数 |
| 日期 | `$table->date('publish_date')` | DATE | 日期 |
| 时间戳 | `$table->timestamp('create_time')` | TIMESTAMP | 时间戳 |
| 日期时间 | `$table->dateTime('created_at')` | DATETIME | 日期时间 |
| JSON | `$table->json('meta')` | JSON | JSON 数据 |

## 字段修饰符

```php
->nullable()                           // 允许 NULL
->default(0)                           // 默认值
->default(DBCont::NORMAL_STATUS)       // 使用常量作为默认值
->comment('字段注释')                   // 字段注释
->after('id')                          // 在指定字段后添加
->unique()                             // 唯一索引
->index()                              // 普通索引
->unsigned()                           // 无符号（用于整数）
->first()                              // 放在表第一位
->change()                             // 修改字段（配合 up/down）
```

## 元数据注释系统

### 标准元数据格式

```php
// 完整元数据
$table->string('title', 200)->comment('标题@title=标题@type=text;必填');

// 字段元数据包含三部分：
// 1. 描述文本: "标题" - 数据库注释
// 2. @title: "标题" - 表单字段标题
// 3. @type: "text" - 表单字段类型
// 4. 其他规则: ";必填" - 验证规则或其他配置
```

### 类型映射表

| @type 值 | 表单组件 | 适用场景 |
|----------|---------|---------|
| `text` | 文本输入框 | 短文本（标题、名称） |
| `textarea` | 多行文本框 | 长文本（描述、备注） |
| `ueditor` | 富文本编辑器 | 富文本内容 |
| `number` | 数字输入框 | 数字（价格、数量） |
| `select` | 下拉选择框 | 枚举值（状态、分类） |
| `radio` | 单选框 | 少量选项 |
| `checkbox` | 多选框 | 多选标签 |
| `switch` | 开关 | 布尔值 |
| `date` | 日期选择器 | 日期 |
| `datetime` | 日期时间选择器 | 日期时间 |
| `time` | 时间选择器 | 时间 |
| `image` | 图片上传 | 单图 |
| `images` | 多图上传 | 多图 |
| `file` | 文件上传 | 文件 |
| `email` | 邮箱输入 | 邮箱地址 |
| `mobile` | 手机号输入 | 手机号 |
| `password` | 密码输入 | 密码 |

### 元数据示例

```php
$table->string('title', 200)->comment('标题@title=标题@type=text');
$table->text('content')->nullable()->comment('内容@title=详情@type=ueditor');
$table->string('cover', 500)->nullable()->comment('封面图@title=封面@type=image');
$table->tinyInteger('status')->default(1)->comment('状态@title=状态@type=select');
$table->integer('sort')->default(0)->comment('排序@title=排序@type=number');
$table->boolean('is_enabled')->default(1)->comment('启用@title=启用@type=switch');
$table->date('publish_date')->nullable()->comment('发布日期@title=发布日期@type=date');
$table->string('email', 100)->nullable()->comment('邮箱@title=邮箱@type=email');
$table->string('mobile', 20)->nullable()->comment('手机@title=手机@type=mobile');
```

## 枚举列表系统

### 定义枚举配置

```php
// 在迁移注释中使用 @enum
$table->tinyInteger('status')->default(1)->comment('状态@title=状态@type=select@enum=status');

// 对应的枚举值定义在控制器中：
public function buildTableColumns($container)
{
    $container->select('status', '状态')
        ->setValueEnum(DBCont::getStatusList());
}
```

### 枚举值位置

```php
// 位置1: Gy_Library\DBCont
use Gy_Library\DBCont;
DBCont::getStatusList();  // [1 => '启用', 0 => '禁用']

// 位置2: 模型中定义
class ProductModel extends GyListModel
{
    public function getTypeList(): array
    {
        return [1 => '类型A', 2 => '类型B', 3 => '类型C'];
    }
}

// 位置3: 控制器中调用
$container->select('type', '类型')
    ->setValueEnum(D('Product')->getTypeList());
```

## 索引设计

```php
// 单列索引
$table->index('status');
$table->index('cate_id');

// 组合索引
$table->index(['status', 'sort']);
$table->index(['cate_id', 'status']);

// 唯一索引
$table->unique('email');
$table->unique(['user_id', 'type']);

// 复合唯一索引
$table->unique(['cate_id', 'title'], 'unique_cate_title');

// 为索引指定名称
$table->index('status', 'idx_status');
```

## 表结构规范

### 命名规范

- **表名**: `qs_xxx`（小写，下划线分隔）
- **字段名**: `snake_case`（小写，下划线分隔）
- **主键**: 通常使用 `id`（bigIncrements）
- **外键**: `{关联表}_id`（如 `cate_id`, `user_id`）
- **时间戳**: 使用 `timestamps()` 或单独定义 `create_time`, `update_time`

### 标准字段

```php
Schema::create('qs_xxx', function (Blueprint $table) {
    $table->bigIncrements('id');           // 主键
    $table->string('title', 200)->comment('标题');
    $table->text('content')->nullable()->comment('内容');
    $table->bigInteger('cate_id')->default(0)->comment('分类ID');
    $table->tinyInteger('status')->default(1)->comment('状态 0禁用 1启用');
    $table->integer('sort')->default(0)->comment('排序');
    $table->timestamps();                   // created_at, updated_at

    // 常用索引
    $table->index('cate_id');
    $table->index('status');
    $table->index(['status', 'sort']);
});
```

### 字段顺序建议

1. 主键 (`id`)
2. 核心业务字段 (`title`, `name`)
3. 内容字段 (`content`, `description`)
4. 外键 (`cate_id`, `user_id`)
5. 媒体字段 (`cover`, `images`)
6. 状态字段 (`status`, `audit_status`)
7. 排序字段 (`sort`)
8. 时间字段 (`create_time`, `update_time`)

## 相关文档

- [Model Guide](model-guide.md) - 模型开发指南
- [Migration Metadata](migration-metadata.md) - 元数据系统详解
- [Where Query Reference](where-query-reference.md) - 查询语法参考
