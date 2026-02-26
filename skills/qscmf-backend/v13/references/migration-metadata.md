# Migration Metadata System

> QSCMF v13 迁移文件元数据系统 - 通过数据库注释定义字段属性

## 概述

QSCMF 扩展了 Laravel 迁移系统，通过在 `comment` 中添加元数据，实现：

- 自动生成表单字段类型
- 自动生成验证规则
- 自动生成表格列配置
- 关联关系配置
- 减少重复代码

## 核心概念

### 元数据格式

```php
$table->string('name', 100)->comment("@title=字段名称;@length=1,100;@require=true;");
```

### 元数据属性表

| 属性 | 说明 | 类型 | 示例 |
|------|------|------|------|
| `@title` | 字段标题（用于表单和表格显示） | string | `@title=栏目名称` |
| `@length` | 验证规则长度范围 | string | `@length=1,100` |
| `@require` | 是否必填 | boolean | `@require=true` |
| `@type` | 字段类型（影响表单/表格显示） | string | `@type=select` |
| `@list` | 枚举列表来源（DBCont 中的方法） | string | `@list=status` |
| `@table` | 关联表名 | string | `@table=qs_xxx_cate` |
| `@show` | 关联表显示字段 | string | `@show=name` |
| `@save` | 是否可编辑保存 | boolean | `@save=true` |

## 字段类型映射

### 基础类型

| @type 值 | 表单组件 | 表格组件 | 说明 | 迁移类型 |
|----------|----------|----------|------|----------|
| `text` | text | text | 单行文本 | string() |
| `textarea` | textarea | text | 多行文本 | text() |
| `number` | number | text | 数字 | integer() |
| `date` | date | date | 日期 | date() |
| `datetime` | datetime | datetime | 日期时间 | dateTime() |
| `url` | text | link | URL 链接 | string() |
| `email` | text | text | 邮箱 | string() |

### 选择类型

| @type 值 | 表单组件 | 表格组件 | 说明 | 迁移类型 |
|----------|----------|----------|------|----------|
| `select` | select | select | 下拉单选 | tinyint/string |
| `checkbox` | checkbox | select | 复选框（多选） | tinyint |
| `radio` | radio | select | 单选框 | tinyint/string |

### 文件类型

| @type 值 | 表单组件 | 表格组件 | 说明 | 迁移类型 |
|----------|----------|----------|------|----------|
| `image` / `picture` | picture | picture | 图片上传 | bigInteger |
| `file` | file | file | 文件上传 | bigInteger |
| `video` | file | video | 视频上传 | bigInteger |

### 富文本类型

| @type 值 | 表单组件 | 表格组件 | 说明 | 迁移类型 |
|----------|----------|----------|------|----------|
| `richText` / `ueditor` | ueditor | - | 富文本编辑器 | longText |

## 枚举列表系统

### 预定义列表

在 `DBCont` 类中预定义的枚举列表：

| List Key | 方法名 | 典型用途 |
|----------|--------|----------|
| `status` | `getStatusList()` | 状态（启用/禁用） |
| `boolStatus` | `getBoolStatusList()` | 是否（是/否） |
| `showType` | `getShowTypeList()` | 展示类型 |
| `auditStatus` | `getAuditStatusList()` | 审核状态 |

### 自定义枚举

在 `DBCont` 中添加自定义枚举方法：

```php
class DBCont
{
    public static function getXxxStatusList(): array
    {
        return [
            1 => '状态1',
            2 => '状态2',
            3 => '状态3',
        ];
    }
}
```

## 代码生成映射

元数据到代码的自动生成规则：

### 验证规则生成

| 元数据 | 生成的验证规则 |
|--------|---------------|
| `@length=1,100` | `['field', '1,100', '长度1-100', self::EXISTS_VALIDATE, 'length']` |
| `@require=true` | `['field', 'require', '不能为空', self::MUST_VALIDATE, '', self::MODEL_BOTH]` |

### 表单字段生成

| 元数据 | 生成的表单代码 |
|--------|---------------|
| `@title=名称;@require=true` | `$builder->addFormItem('field', 'text', '名称', '', '', '', 'required')` |
| `@type=select;@list=status` | `$builder->addFormItem('field', 'select', '状态', '', DBCont::getStatusList())` |
| `@save=true` | 在表格列中添加可编辑 |

### 表格列生成

| 元数据 | 生成的表格代码 |
|--------|---------------|
| `@title=名称` | `$builder->addTableColumn('field', '名称')` |
| `@type=select;@list=status` | `$builder->addTableColumn('field', '状态', 'select', $status_list)` |

## 迁移文件结构

### 基本结构

```php
<?php

use Illuminate\Support\Facades\Schema;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Database\Migrations\Migration;
use Illuminate\Support\Facades\DB;

return new class extends Migration
{
    // 迁移前钩子
    public function beforeCmmUp() { /* ... */ }

    // 回滚前钩子
    public function beforeCmmDown() { /* ... */ }

    // 创建表
    public function up()
    {
        Schema::create('qs_xxx', function (Blueprint $table) {
            $table->bigIncrements('id');
            // 字段定义...
            $table->timestamp('update_date', 4)
                ->default(DB::raw('CURRENT_TIMESTAMP(4) ON UPDATE CURRENT_TIMESTAMP(4)'));
            $table->timestamp('create_date', 4)
                ->default(DB::raw('CURRENT_TIMESTAMP(4)'));
        });

        // 表注释（含元数据）
        DB::unprepared("ALTER TABLE `qs_xxx_cate` COMMENT = '@title=XXX表;'");
    }

    // 删除表
    public function down()
    {
        Schema::dropIfExists('qs_xxx');
    }

    // 迁移后钩子
    public function afterCmmUp() { /* ... */ }

    // 回滚后钩子
    public function afterCmmDown() { /* ... */ }
};
```

### 钩子方法用途

| 钩子方法 | 执行时机 | 典型用途 |
|----------|----------|----------|
| `beforeCmmUp()` | 迁移前 | 检查依赖、验证数据 |
| `afterCmmUp()` | 迁移后 | 初始化数据、刷新缓存 |
| `beforeCmmDown()` | 回滚前 | 检查数据完整性 |
| `afterCmmDown()` | 回滚后 | 清理缓存、删除相关文件 |

## 自定义钩子

QSCMF 扩展了 Laravel 迁移，支持在迁移前后执行自定义逻辑：

```php
return new class extends Migration
{
    public function beforeCmmUp()
    {
        // 迁移前执行（如检查依赖）
    }

    public function beforeCmmDown()
    {
        // 回滚前执行（如检查数据）
    }

    public function up()
    {
        // 创建表
    }

    public function down()
    {
        // 删除表
    }

    public function afterCmmUp()
    {
        // 迁移后执行（如初始化数据）
        DB::table('qs_xxx_cate')->insert([
            'name' => '默认分类',
            'show_type' => 'article',
            'sort' => 0,
            'status' => 1,
        ]);
    }

    public function afterCmmDown()
    {
        // 回滚后执行（如清理缓存）
    }
};
```

## 常用字段定义

### 基础字段

```php
// 主键
$table->bigIncrements('id');

// 标题
$table->string('title', 255)
    ->comment("@title=标题;@length=1,255;@require=true;");

// 名称
$table->string('name', 100)
    ->comment("@title=名称;@length=1,100;@require=true;");

// 描述
$table->string('summary', 500)
    ->comment("@title=描述;@type=textarea;@length=1,500;@require=true;");
```

### 关联字段

```php
// 分类 ID
$table->bigInteger('cate_id')
    ->comment('@title=分类;@type=select;@table=qs_xxx_cate;@show=name;@require=true;');

// 标签 ID（多选，存储逗号分隔）
$table->string('tag_id')
    ->default(null)->nullable()
    ->comment('@title=标签;@type=select;@table=qs_xxx_tag;@show=name;');

// 图片 ID
$table->bigInteger('cover_id')
    ->comment('@title=封面图;@type=picture;@require=true;');

// 文件 ID
$table->bigInteger('file_id')
    ->default(null)->nullable()
    ->comment('@title=附件;@type=file;');
```

### 状态字段

```php
// 排序
$table->mediumInteger('sort')
    ->default(0)->comment('@title=排序;@save=true;');

// 状态（启用/禁用）
$table->boolean('status')
    ->default(1)->comment('@title=状态;@type=select;@list=status; 1 正常 0 禁用');

// 是否类型
$table->boolean('need_fee')
    ->default(0)->comment('@title=是否付费;@type=checkbox;@list=boolStatus; 1 是 0 否');
```

### 时间字段

```php
// 日期
$table->date('publish_date')
    ->comment('@title=发布日期;@type=date;@require=true;');

// 时间戳（使用精度 4）
$table->timestamp('create_date', 4)
    ->default(DB::raw('CURRENT_TIMESTAMP(4)'));

$table->timestamp('update_date', 4)
    ->default(DB::raw('CURRENT_TIMESTAMP(4) ON UPDATE CURRENT_TIMESTAMP(4)'));
```

### 内容字段

```php
// URL
$table->string('url', 500)
    ->default('')->comment('@title=链接;@type=url;@length=1,500;');

// 富文本内容
$table->longText('content')
    ->default(null)->nullable()
    ->comment('@title=内容;@type=richText;');
```

## 命名规范

### 迁移文件命名

```
{date}_create_{table_name}.php
```

示例:
```
2025_12_08_021921_create_xxx_cate.php
2025_12_08_024133_create_xxx_content.php
2025_12_08_024002_create_xxx_tag.php
```

### 表名规范

| 表类型 | 命名模式 | 示例 |
|--------|----------|------|
| 分类表 | `{module}_cate` | `qs_article_cate` |
| 内容表 | `{module}_content` | `qs_article_content` |
| 标签表 | `{module}_tag` | `qs_article_tag` |
| 其他表 | `{module}_{entity}` | `qs_order_item` |

**规则**:
- 必须以 `qs_` 前缀开头
- 使用小写字母和下划线
- 使用单数形式（非复数）

### 字段顺序规范

推荐的字段定义顺序：

1. **主键**: `id`
2. **业务字段**: title, name, content, summary...
3. **关联字段**: cate_id, tag_id, cover_id...
4. **状态字段**: sort, status, need_fee...
5. **时间戳**: create_date, update_date

## 最佳实践

### 1. 使用 nullable() 处理可选字段

```php
// ✅ 正确
$table->bigInteger('file_id')
    ->default(null)->nullable()
    ->comment('@title=附件;@type=file;');

// ❌ 避免
$table->bigInteger('file_id')->default(0);
```

### 2. 添加表注释

```php
DB::unprepared("ALTER TABLE `qs_xxx` COMMENT = '@title=XXX表;'");
```

### 3. 使用事务处理复杂迁移

```php
public function up()
{
    DB::transaction(function () {
        Schema::create('qs_xxx', function (Blueprint $table) {
            // ...
        });

        // 初始化数据
        DB::table('qs_xxx')->insert([
            // ...
        ]);
    });
}
```

### 4. 添加索引

```php
// 单列索引
$table->index('cate_id');
$table->index('status');

// 复合索引
$table->index(['cate_id', 'status']);

// 唯一索引
$table->unique('slug');
```

### 5. 使用外键约束（谨慎）

```php
$table->foreign('cate_id')
    ->references('id')
    ->on('qs_xxx_cate')
    ->onDelete('restrict');
```

## 相关文档

- [Migration Guide](migration-guide.md) - 迁移基础语法
- [Model Guide](model-guide.md) - 模型实现最佳实践
- [Abstract Base Patterns](abstract-base-patterns.md) - 抽象基类模式
- [CRUD Patterns](crud-patterns.md) - CRUD 开发模式
