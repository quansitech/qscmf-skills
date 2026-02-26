---
title: Form Validation (v14)
impact: HIGH
impactDescription: Required for data integrity in all forms
tags: crud, form, validation, v14, antdadmin
---

## Form Validation (v14)

Configure validation rules for v14 forms using AntdAdmin Component Rules API.

### When to Use This Rule

- Adding validation to forms
- Ensuring data integrity
- Displaying error messages to users

---

## AntdAdmin Component Validation

### Basic Rule Types

```php
use AntdAdmin\Component\ColumnType\RuleType\Required;
use AntdAdmin\Component\ColumnType\RuleType\Length;
use AntdAdmin\Component\ColumnType\RuleType\Email;
use AntdAdmin\Component\ColumnType\RuleType\Pattern;
use AntdAdmin\Component\ColumnType\RuleType\Range;
use AntdAdmin\Component\ColumnType\RuleType\Validator;

// In form columns configuration
$columns->text('product_name', '商品名称')
    ->addRule(new Required())
    ->addRule(new Length(1, 200));

$columns->text('email', '邮箱')
    ->addRule(new Email());

$columns->number('price', '价格')
    ->addRule(new Required())
    ->addRule(new Range(0.01, 999999.99));
```

### Complete Form Example with Validation

```php
public function add()
{
    if (IS_POST) {
        parent::autoCheckToken();
        $data = I('post.');

        $model = D('Product');
        $result = $model->createAdd($data);

        if ($result === false) {
            $this->error($model->getError());
        }

        $this->success('添加成功');
    }

    $form = new Form();
    $form->setSubmitRequest('post', U('add'))
        ->setInitialValues([
            'status' => DBCont::NORMAL_STATUS,
            'sort' => 99,
        ])
        ->columns(function (Form\ColumnsContainer $columns) {
            // Required text with length
            $columns->text('product_name', '商品名称')
                ->addRule(new Required('请输入商品名称'))
                ->addRule(new Length(1, 200, '名称长度1-200字符'))
                ->setFormItemWidth(24);

            // Required select
            $columns->select('cate_id', '分类')
                ->setValueEnum(D('Category')->getField('id,name'))
                ->addRule(new Required('请选择分类'))
                ->setFormItemWidth(24);

            // Email validation
            $columns->text('email', '邮箱')
                ->addRule(new Email('邮箱格式不正确'))
                ->setFormItemWidth(24);

            // Phone with pattern
            $columns->text('phone', '手机号')
                ->addRule(new Pattern('/^1[3-9]\d{9}$/', '手机号格式不正确'))
                ->setFormItemWidth(12);

            // Number with range
            $columns->number('price', '价格')
                ->addRule(new Required('请输入价格'))
                ->addRule(new Range(0.01, 999999.99, '价格范围0.01-999999.99'))
                ->setFormItemWidth(12);

            // Custom validator
            $columns->text('code', '商品编码')
                ->addRule(new Validator(function($value) {
                    if (D('Product')->where(['code' => $value])->find()) {
                        return '商品编码已存在';
                    }
                    return true;
                }))
                ->setFormItemWidth(12);

            $columns->select('status', '状态')
                ->setValueEnum(DBCont::getStatusList())
                ->addRule(new Required())
                ->setFormItemWidth(12);
        })
        ->actions(function (Form\ActionsContainer $actions) {
            $actions->button('提交')->submit();
            $actions->button('重置')->reset();
        });

    return $form->render();
}
```

---

## Rule Types Reference

### Required

```php
use AntdAdmin\Component\ColumnType\RuleType\Required;

// Basic required
$columns->text('name', '名称')
    ->addRule(new Required());

// With custom message
$columns->text('name', '名称')
    ->addRule(new Required('请输入名称'));

// Whitespace validation
$columns->text('name', '名称')
    ->addRule(new Required('请输入名称', true)); // true = whitespace only also triggers error
```

### Length

```php
use AntdAdmin\Component\ColumnType\RuleType\Length;

// Min and max length
$columns->text('name', '名称')
    ->addRule(new Length(1, 200));

// With custom message
$columns->text('name', '名称')
    ->addRule(new Length(1, 200, '名称长度1-200字符'));

// Min only (no max)
$columns->text('password', '密码')
    ->addRule(new Length(6, null, '密码至少6位'));
```

### Email

```php
use AntdAdmin\Component\ColumnType\RuleType\Email;

// Basic email validation
$columns->text('email', '邮箱')
    ->addRule(new Email());

// With custom message
$columns->text('email', '邮箱')
    ->addRule(new Email('邮箱格式不正确'));
```

### Pattern (Regex)

```php
use AntdAdmin\Component\ColumnType\RuleType\Pattern;

// Phone number
$columns->text('phone', '手机号')
    ->addRule(new Pattern('/^1[3-9]\d{9}$/', '手机号格式不正确'));

// ID card
$columns->text('id_card', '身份证号')
    ->addRule(new Pattern('/^\d{17}[\dXx]$/', '身份证号格式不正确'));

// URL
$columns->text('url', '网址')
    ->addRule(new Pattern('/^https?:\/\/.+$/', '网址格式不正确'));

// Custom pattern with message
$columns->text('code', '编码')
    ->addRule(new Pattern('/^[A-Z]{2}\d{4}$/', '编码格式：2位大写字母+4位数字'));
```

### Range

```php
use AntdAdmin\Component\ColumnType\RuleType\Range;

// Number range
$columns->number('age', '年龄')
    ->addRule(new Range(1, 120, '年龄范围1-120'));

// Price range
$columns->number('price', '价格')
    ->addRule(new Range(0.01, 999999.99, '价格范围0.01-999999.99'));

// Min only
$columns->number('quantity', '数量')
    ->addRule(new Range(1, null, '数量至少为1'));

// Max only
$columns->number('stock', '库存')
    ->addRule(new Range(null, 10000, '库存不能超过10000'));
```

### Validator (Custom)

```php
use AntdAdmin\Component\ColumnType\RuleType\Validator;

// Simple custom validator
$columns->text('code', '编码')
    ->addRule(new Validator(function($value) {
        if (D('Product')->where(['code' => $value])->find()) {
            return '编码已存在';
        }
        return true;
    }));

// Custom validator with model access
$columns->text('end_time', '结束时间')
    ->addRule(new Validator(function($value, $form) {
        $start_time = $form['start_time'] ?? null;
        if ($start_time && strtotime($value) <= strtotime($start_time)) {
            return '结束时间必须大于开始时间';
        }
        return true;
    }));

// Complex validation
$columns->text('password', '密码')
    ->addRule(new Validator(function($value) {
        if (strlen($value) < 6) {
            return '密码至少6位';
        }
        if (!preg_match('/[A-Z]/', $value)) {
            return '密码必须包含大写字母';
        }
        if (!preg_match('/[a-z]/', $value)) {
            return '密码必须包含小写字母';
        }
        if (!preg_match('/\d/', $value)) {
            return '密码必须包含数字';
        }
        return true;
    }));
```

---

## Model Validation (Backend)

### Define Validation Rules

```php
<?php
namespace Common\Model;

use Gy_Library\GyListModel;
use Gy_Library\DBCont;

class ProductModel extends GyListModel
{
    protected $tableName = 'product';

    protected $_validate = [
        // Format: [field, rule, message, condition, type, append]

        // Required
        ['name', 'require', '商品名称不能为空', self::MUST_VALIDATE],
        ['code', 'require', '商品编码不能为空', self::MUST_VALIDATE],

        // Unique
        ['code', 'unique', '商品编码已存在', self::MUST_VALIDATE],

        // Length
        ['name', '1,200', '商品名称长度不正确', self::VALUE_VALIDATE, 'length'],
        ['description', '0,1000', '描述最多1000字符', self::VALUE_VALIDATE, 'length'],

        // Email
        ['email', 'email', '邮箱格式不正确', self::VALUE_VALIDATE],

        // URL
        ['url', 'url', 'URL格式不正确', self::VALUE_VALIDATE],

        // Mobile
        ['mobile', 'mobile', '手机号格式不正确', self::VALUE_VALIDATE],

        // Currency
        ['price', 'currency', '价格格式不正确', self::VALUE_VALIDATE],

        // Number
        ['sort', 'number', '排序必须为数字', self::VALUE_VALIDATE],

        // In list
        ['status', [0, 1, 2], '状态值不正确', self::VALUE_VALIDATE, 'in'],

        // Between
        ['age', '1,120', '年龄必须在1-120之间', self::VALUE_VALIDATE, 'between'],

        // Regex
        ['phone', '/^1[3-9]\d{9}$/', '手机号格式不正确', self::VALUE_VALIDATE, 'regex'],

        // Callback
        ['stock', 'checkStock', '库存不能为负数', self::VALUE_VALIDATE, 'callback'],

        // Function
        ['end_time', 'checkEndTime', '结束时间必须大于开始时间', self::VALUE_VALIDATE, 'function'],
    ];

    // Callback validation method
    protected function checkStock($value)
    {
        return $value >= 0;
    }
}
```

### Validation Conditions

| Constant | Value | Description |
|----------|-------|-------------|
| `self::MUST_VALIDATE` | 1 | Must validate always |
| `self::VALUE_VALIDATE` | 2 | Validate if field has value |
| `self::EXISTS_VALIDATE` | 3 | Validate if field exists |
| `self::MODEL_INSERT` | 1 | Only on insert |
| `self::MODEL_UPDATE` | 2 | Only on update |
| `self::MODEL_BOTH` | 3 | Both insert and update |

### Validation Types

| Type | Description | Example |
|------|-------------|---------|
| `require` | Field required | `['name', 'require', '名称必填']` |
| `unique` | Unique in table | `['code', 'unique', '编码已存在']` |
| `length` | String length | `['name', '1,200', '长度错误', 3, 'length']` |
| `email` | Email format | `['email', 'email', '邮箱格式错误']` |
| `url` | URL format | `['url', 'url', 'URL格式错误']` |
| `mobile` | Mobile format | `['mobile', 'mobile', '手机格式错误']` |
| `currency` | Currency format | `['price', 'currency', '价格格式错误']` |
| `number` | Numeric value | `['sort', 'number', '排序必须为数字']` |
| `in` | Value in list | `['status', [0,1,2], '状态错误', 3, 'in']` |
| `between` | Number range | `['age', '1,120', '年龄错误', 3, 'between']` |
| `regex` | Regular expression | `['phone', '/^1\d{10}$/', '手机错误', 3, 'regex']` |
| `callback` | Custom callback | `['field', 'methodName', '错误', 3, 'callback']` |
| `function` | Function call | `['field', 'functionName', '错误', 3, 'function']` |

---

## Callback Validation Examples

### Check Unique with Exclude

```php
protected $_validate = [
    ['code', 'checkCodeUnique', '商品编码已存在', self::VALUE_VALIDATE, 'callback'],
];

protected function checkCodeUnique($value)
{
    $id = I('post.id', 0, 'intval');

    $exists = $this->where([
        'code' => $value,
        'id' => ['neq', $id]
    ])->find();

    return !$exists;
}
```

### Check Time Range

```php
protected $_validate = [
    ['start_time', 'checkTimeRange', '时间范围不正确', self::VALUE_VALIDATE, 'callback'],
];

protected function checkTimeRange($value)
{
    $end_time = I('post.end_time');

    if ($end_time && strtotime($value) >= strtotime($end_time)) {
        return false;
    }

    return true;
}
```

### Check Related Data

```php
protected $_validate = [
    ['cate_id', 'checkCategory', '分类不存在或已禁用', self::MUST_VALIDATE, 'callback'],
];

protected function checkCategory($value)
{
    $category = D('Category')->find($value);

    if (!$category || $category['status'] != DBCont::NORMAL_STATUS) {
        return false;
    }

    return true;
}
```

---

## Controller Validation

```php
public function save()
{
    $data = I('post.');

    // Manual validation
    if (empty($data['name'])) {
        $this->error('商品名称不能为空');
    }

    if (mb_strlen($data['name']) > 200) {
        $this->error('商品名称不能超过200字符');
    }

    // Model validation
    $model = D('Product');
    $result = $model->create($data);

    if ($result === false) {
        $this->error($model->getError());
    }

    // Save
    $id = $model->add($result);

    if ($id) {
        $this->success('保存成功', U('index'));
    } else {
        $this->error('保存失败');
    }
}
```

---

## Complete Example

```php
<?php
namespace Common\Model;

use Gy_Library\GyListModel;
use Gy_Library\DBCont;

class ProductModel extends GyListModel
{
    protected $tableName = 'product';

    protected $_validate = [
        // Basic
        ['name', 'require', '商品名称不能为空', self::MUST_VALIDATE],
        ['name', '1,200', '商品名称长度不正确', self::VALUE_VALIDATE, 'length'],
        ['code', 'require', '商品编码不能为空', self::MUST_VALIDATE],
        ['code', 'checkCodeUnique', '商品编码已存在', self::VALUE_VALIDATE, 'callback'],

        // Price
        ['price', 'require', '价格不能为空', self::MUST_VALIDATE],
        ['price', 'currency', '价格格式不正确', self::VALUE_VALIDATE],
        ['price', '0.01,999999.99', '价格范围不正确', self::VALUE_VALIDATE, 'between'],

        // Status
        ['status', [0, 1, 2], '状态值不正确', self::VALUE_VALIDATE, 'in'],

        // Custom
        ['stock', 'checkStock', '库存不能为负数', self::VALUE_VALIDATE, 'callback'],

        // Related
        ['cate_id', 'checkCategory', '分类不存在或已禁用', self::MUST_VALIDATE, 'callback'],
    ];

    protected function checkCodeUnique($value)
    {
        $id = I('post.id', 0, 'intval');
        $exists = $this->where([
            'code' => $value,
            'id' => ['neq', $id]
        ])->find();
        return !$exists;
    }

    protected function checkStock($value)
    {
        return $value >= 0;
    }

    protected function checkCategory($value)
    {
        $category = D('Category')->find($value);
        return $category && $category['status'] == DBCont::NORMAL_STATUS;
    }
}
```

---

## Related Rules

- [FormBuilder API](../formbuilder-api.md) - Form field configuration
- [AntdAdmin Components](../antdadmin.md) - Component reference
- [Model Guide](../../references/model-guide.md) - Model patterns
