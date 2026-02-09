# Models & Migrations Reference

> QSCMF 模型与数据库迁移

## GyListModel Structure

### Basic Model

```php
<?php
namespace Common\Model;
use Gy_Library\GyListModel;

class DemoModel extends GyListModel
{
    protected $tableName = 'qs_demo';
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

### Calling Models

```php
// 实例化
$model = D('Demo');

// 查询单条
$data = D('Demo')->find(1);
$data = D('Demo')->where(['id' => 1])->find();

// 查询多条
$list = D('Demo')->select();
$list = D('Demo')->where(['status' => 1])->select();

// 统计
$count = D('Demo')->count();
$count = D('Demo')->where(['status' => 1])->count();

// 添加
$id = D('Demo')->add(['title' => 'Test']);

// 更新
$result = D('Demo')->where(['id' => 1])->save(['title' => 'Updated']);

// 删除
$result = D('Demo')->delete(1);
$result = D('Demo')->where(['id' => 1])->delete();
```

## Validation & Auto-completion

### Validation Rules

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

    // 验证时机
    // self::MUST_VALIDATE  - 必须验证
    // self::EXISTS_VALIDATE  - 有值时验证
    // self::VALUE_VALIDATE  - 值不为空时验证
];
```

### Auto-completion

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

## Laravel Migrations

### Creating Migration

```bash
php artisan make:migration create_demo_table
```

### Migration Structure

```php
<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    public function up()
    {
        Schema::create('qs_demo', function (Blueprint $table) {
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
        Schema::dropIfExists('qs_demo');
    }
};
```

### Running Migrations

```bash
# 运行所有待执行的迁移
php artisan migrate

# 回滚最后一次迁移
php artisan migrate:rollback

# 回滚所有迁移
php artisan migrate:reset

# 回滚后重新运行所有迁移
php artisan migrate:refresh
```

### Common Column Types

```php
$table->id();                          // 主键
$table->string('name', 200);           // VARCHAR(200)
$table->text('content');               // TEXT
$table->longText('body');              // LONGTEXT
$table->integer('count');              // INT
$table->tinyInteger('status');         // TINYINT
$table->boolean('is_active');          // BOOLEAN/TINYINT(1)
$table->decimal('price', 10, 2);       // DECIMAL(10,2)
$table->dateTime('created_at');        // DATETIME
$table->timestamp('publish_time');     // TIMESTAMP
$table->timestamps();                  // created_at, updated_at
$table->foreignId('user_id');          // 外键 ID
```

### Column Modifiers

```php
->nullable()                           // 可空
->default(0)                           // 默认值
->comment('注释')                      // 字段注释
->after('id')                          // 在指定字段后
->unique()                             // 唯一索引
->index()                              // 普通索引
```

## Common Query Methods

### Where Conditions

```php
// 等于
$where['id'] = 1;

// 不等于
$where['id'] = ['neq', 1];

// 大于
$where['count'] = ['gt', 0];

// 小于
$where['count'] = ['lt', 100];

// LIKE
$where['title'] = ['like', '%keyword%'];

// IN
$where['status'] = ['in', '0,1,2'];

// NOT IN
$where['status'] = ['notin', '0,1'];

// BETWEEN
$where['create_time'] = ['between', [strtotime('2024-01-01'), time()]];

// 多条件 OR
$where['_logic'] = 'or';
$where['title'] = ['like', '%a%'];
$where['content'] = ['like', '%b%'];
```

### Order & Limit

```php
// 排序
->order('id desc')
->order(['sort' => 'asc', 'id' => 'desc'])

// 限制
->limit(10)

// 分页
->page(1, 10)
```

### Field Selection

```php
// 指定字段
->field('id,title,status')

// 排除字段
->field('id,title', true)

// 字段别名
->field('id, title as name')
```

---

**更多参考**：
- Laravel 迁移文档
- `app/Common/Model/` 中的现有模型
