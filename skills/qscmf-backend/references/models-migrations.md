# Models & Migrations Reference

> QSCMF 模型与数据库迁移

## 概述

QSCMF 使用 ThinkPHP 3.2 的 ORM 系统，结合 Laravel 的数据库迁移工具，提供完整的数据库操作和版本管理能力。

## GyListModel 基础结构

### 基本模型定义

```php
<?php
namespace Common\Model;
use Gy_Library\GyListModel;

class XxxModel extends GyListModel
{
    protected $tableName = 'qs_xxx';
    protected $pk = 'id';

    // 验证规则
    protected $_validate = [
        ['title', 'require', '标题不能为空', self::MUST_VALIDATE],
    ];

    // 自动完成
    protected $_auto = [
        ['create_time', 'time', self::MODEL_INSERT, 'function'],
        ['update_time', 'time', self::MODEL_UPDATE, 'function'],
    ];
}
```

### 核心属性

| 属性 | 类型 | 说明 |
|------|------|------|
| `$tableName` | string | 数据表名（不含前缀） |
| `$pk` | string | 主键字段名 |
| `$_validate` | array | 验证规则 |
| `$_auto` | array | 自动完成规则 |
| `$_delete_validate` | array | 删除前验证规则 |

### 模型调用方法

```php
// 实例化模型
$model = D('Xxx');

// 查询单条记录
$data = D('Xxx')->find(1);
$data = D('Xxx')->where(['id' => 1])->find();

// 查询多条记录
$list = D('Xxx')->select();
$list = D('Xxx')->where(['status' => 1])->select();

// 统计记录数
$count = D('Xxx')->count();
$count = D('Xxx')->where(['status' => 1])->count();

// 添加记录
$id = D('Xxx')->add(['title' => 'Test']);

// 更新记录
$result = D('Xxx')->where(['id' => 1])->save(['title' => 'Updated']);

// 删除记录
$result = D('Xxx')->delete(1);
$result = D('Xxx')->where(['id' => 1])->delete();
```

## 验证规则与自动完成

### 验证规则配置

```php
protected $_validate = [
    // 必填验证
    ['field', 'require', '错误信息', self::MUST_VALIDATE],

    // 长度验证
    ['field', '1,200', '长度1-200', self::MUST_VALIDATE, 'length'],

    // 唯一验证
    ['email', '', '已存在', self::MUST_VALIDATE, 'unique'],

    // 正则验证
    ['mobile', '/^1[3-9]\d{9}$/', '格式错误', self::MUST_VALIDATE, 'regex'],

    // 值范围验证
    ['status', '0,1,2', '值错误', self::MUST_VALIDATE, 'in'],
];
```

### 验证时机常量

| 常量 | 值 | 说明 |
|------|-----|------|
| `self::MUST_VALIDATE` | 必须验证 | 无论字段是否有值都必须验证 |
| `self::EXISTS_VALIDATE` | 有值时验证 | 仅在字段有值时验证 |
| `self::VALUE_VALIDATE` | 值不为空时验证 | 字段值不为空时验证 |

### 验证时机模型常量

| 常量 | 说明 |
|------|------|
| `self::MODEL_INSERT` | 插入时验证/完成 |
| `self::MODEL_UPDATE` | 更新时验证/完成 |
| `self::MODEL_BOTH` | 插入和更新时都验证/完成 |

### 自动完成配置

```php
protected $_auto = [
    // 插入时自动完成
    ['create_time', 'time', self::MODEL_INSERT, 'function'],

    // 更新时自动完成
    ['update_time', 'time', self::MODEL_UPDATE, 'function'],

    // 插入和更新都完成
    ['ip', 'get_client_ip', self::MODEL_BOTH, 'function'],
];
```

## Laravel 数据库迁移

### 创建迁移文件

```bash
php artisan make:migration create_xxx_table
```

### 迁移文件结构

```php
<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    public function up()
    {
        Schema::create('qs_xxx', function (Blueprint $table) {
            $table->id();
            $table->string('title', 200)->comment('标题');
            $table->text('content')->nullable()->comment('内容');
            $table->unsignedInteger('cate_id')->default(0)->comment('分类ID');
            $table->string('cover', 500)->nullable()->comment('封面图');
            $table->tinyInteger('status')->default(1)->comment('状态 0禁用 1启用');
            $table->integer('sort')->default(0)->comment('排序');
            $table->timestamps();

            $table->index('cate_id');
            $table->index('status');
        });
    }

    public function down()
    {
        Schema::dropIfExists('qs_xxx');
    }
};
```

### 运行迁移命令

```bash
# 运行所有待执行的迁移
php artisan migrate

# 回滚最后一次迁移
php artisan migrate:rollback

# 回滚所有迁移
php artisan migrate:reset

# 回滚后重新运行所有迁移
php artisan migrate:refresh

# 查看迁移状态
php artisan migrate:status
```

### 常用字段类型

| 方法 | 说明 | 示例 |
|------|------|------|
| `$table->id()` | 主键（自增） | BIGINT UNSIGNED |
| `$table->string('name', 200)` | 字符串 | VARCHAR(200) |
| `$table->text('content')` | 长文本 | TEXT |
| `$table->longText('body')` | 超长文本 | LONGTEXT |
| `$table->integer('count')` | 整数 | INT |
| `$table->tinyInteger('status')` | 小整数 | TINYINT |
| `$table->boolean('is_active')` | 布尔值 | TINYINT(1) |
| `$table->decimal('price', 10, 2)` | 小数 | DECIMAL(10,2) |
| `$table->dateTime('created_at')` | 日期时间 | DATETIME |
| `$table->timestamp('publish_time')` | 时间戳 | TIMESTAMP |
| `$table->timestamps()` | 时间戳字段 | created_at, updated_at |
| `$table->foreignId('user_id')` | 外键 ID | BIGINT UNSIGNED |

### 字段修饰符

```php
->nullable()                           // 允许 NULL
->default(0)                           // 默认值
->comment('注释')                      // 字段注释
->after('id')                          // 在指定字段后添加
->unique()                             // 唯一索引
->index()                              // 普通索引
->unsigned()                           // 无符号
->first()                              // 放在表第一位
```

## 常用查询方法

### Where 条件表达式

```php
// 等于 (=)
$where['id'] = 1;

// 不等于 (!=)
$where['id'] = ['neq', 1];

// 大于 (>)
$where['count'] = ['gt', 0];

// 小于 (<)
$where['count'] = ['lt', 100];

// 大于等于 (>=)
$where['count'] = ['egt', 0];

// 小于等于 (<=)
$where['count'] = ['elt', 100];

// LIKE 模糊查询
$where['title'] = ['like', '%keyword%'];

// IN 查询
$where['status'] = ['in', '0,1,2'];

// NOT IN 查询
$where['status'] = ['notin', '0,1'];

// BETWEEN 范围查询
$where['create_time'] = ['between', [strtotime('2024-01-01'), time()]];

// 多条件 OR 查询
$where['_logic'] = 'or';
$where['title'] = ['like', '%a%'];
$where['content'] = ['like', '%b%'];
```

### 排序与分页

```php
// 单字段排序
->order('id desc')
->order('sort asc')

// 多字段排序
->order(['sort' => 'asc', 'id' => 'desc'])

// 限制数量
->limit(10)

// 分页查询
->page(1, 10)  // 第1页，每页10条
```

### 字段选择

```php
// 指定查询字段
->field('id,title,status')

// 排除字段（第二个参数为 true）
->field('id,title', true)

// 字段别名
->field('id, title as name')

// 聚合函数
->field('COUNT(*) as count')
->field('AVG(score) as avg_score')
```

## 高级查询模式

### 关联查询

```php
// 关联查询（使用 JOIN）
D('Xxx')
    ->alias('x')
    ->join('LEFT JOIN qs_cate c ON x.cate_id = c.id')
    ->field('x.*, c.name as cate_name')
    ->select();
```

### 聚合查询

```php
// 统计数量
$count = D('Xxx')->where(['status' => 1])->count();

// 求和
$sum = D('Xxx')->sum('price');

// 平均值
$avg = D('Xxx')->avg('score');

// 最大值
$max = D('Xxx')->max('views');

// 最小值
$min = D('Xxx')->min('price');
```

### 事务处理

```php
$model = D('Xxx');
$model->startTrans();

try {
    // 执行多个数据库操作
    $id = $model->add($data1);
    $model->where(['id' => $id])->save($data2);

    // 提交事务
    $model->commit();
} catch (\Exception $e) {
    // 回滚事务
    $model->rollback();
    throw $e;
}
```

## 数据库状态常量

使用 `DBCont` 常量统一管理数据库状态值：

```php
use Gy_Library\DBCont;

DBCont::NORMAL_STATUS    // = 1 (启用)
DBCont::DISABLE_STATUS   // = 0 (禁用)
DBCont::AUDIT_STATUS     // = 2 (待审核)

DBCont::getStatusList()  // [1 => '启用', 0 => '禁用']
```

## 最佳实践

### 1. 命名规范

- **表名**: `qs_xxx`（小写，下划线分隔）
- **模型名**: `XxxModel`（大驼峰，后缀 Model）
- **主键**: 通常使用 `id`
- **时间字段**: `create_time`, `update_time`（INT 类型）

### 2. 字段注释

所有数据库字段应添加有意义的注释：

```php
$table->string('title', 200)->comment('标题');
$table->tinyInteger('status')->default(1)->comment('状态 0禁用 1启用');
```

### 3. 索引策略

```php
// 单列索引
$table->index('status');

// 组合索引
$table->index(['cate_id', 'status']);

// 唯一索引
$table->unique('email');

// 外键索引
$table->foreignId('user_id')->index();
```

### 4. 迁移文件元数据

使用注释标记业务逻辑（参考 [Migration Metadata](migration-metadata.md)）：

```php
/**
 * @meta 实体名称=Demo
 * @meta 功能描述=示例模块
 * @meta 核心字段=title,status
 * @meta 关联表=qs_cate (cate_id)
 */
```

---

## 相关文档

- [Admin Controllers](admin-controllers.md) - 控制器中的模型使用
- [Abstract Base Patterns](abstract-base-patterns.md) - 抽象基类模式中的模型
- [Migration Metadata](migration-metadata.md) - 迁移元数据规范
- [Development Standards](development-standards.md) - 数据库开发规范
