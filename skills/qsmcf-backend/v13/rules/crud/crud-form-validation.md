---
title: Form Validation (v13)
impact: HIGH
impactDescription: Required for data integrity in all forms
tags: crud, form, validation, v13
---

## Form Validation (v13)

Configure validation rules for v13 forms.

### When to Use This Rule

- Adding validation to forms
- Ensuring data integrity
- Displaying error messages to users

---

## Model Validation

Define validation rules in Model `$_validate`:

```php
protected $_validate = [
    // Format: [field, rule, message, condition, type, append]

    // Required
    ['name', 'require', '名称不能为空', self::MUST_VALIDATE],

    // Unique
    ['code', 'unique', '编码已存在', self::MUST_VALIDATE],

    // Length
    ['name', '1,200', '名称长度1-200字符', self::VALUE_VALIDATE, 'length'],

    // Email
    ['email', 'email', '邮箱格式不正确', self::VALUE_VALIDATE],

    // URL
    ['url', 'url', 'URL格式不正确', self::VALUE_VALIDATE],

    // In list
    ['status', [0, 1, 2], '状态值不正确', self::VALUE_VALIDATE, 'in'],

    // Not in list
    ['type', [0], '类型不能为0', self::VALUE_VALIDATE, 'notin'],

    // Between
    ['age', '1,120', '年龄必须在1-120之间', self::VALUE_VALIDATE, 'between'],

    // Regex
    ['phone', '/^1[3-9]\d{9}$/', '手机号格式不正确', self::VALUE_VALIDATE, 'regex'],

    // Callback
    ['custom_field', 'checkCustom', '验证失败', self::MUST_VALIDATE, 'callback'],

    // Confirm (password match)
    ['password', 'confirm_password', '两次密码不一致', self::VALUE_VALIDATE, 'confirm'],

    // Equal
    ['accept', '1', '请同意协议', self::MUST_VALIDATE, 'equal'],

    // Function
    ['end_time', 'checkEndTime', '结束时间必须大于开始时间', self::VALUE_VALIDATE, 'function'],
];
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
| `in` | Value in list | `['status', [0,1,2], '状态错误', 3, 'in']` |
| `notin` | Value not in list | `['type', [0], '类型错误', 3, 'notin']` |
| `between` | Number range | `['age', '1,120', '年龄错误', 3, 'between']` |
| `regex` | Regular expression | `['phone', '/^1\d{10}$/', '手机错误', 3, 'regex']` |
| `callback` | Custom callback | `['field', 'methodName', '错误', 3, 'callback']` |
| `function` | Function call | `['field', 'functionName', '错误', 3, 'function']` |
| `confirm` | Field match | `['pwd', 'pwd_confirm', '不一致', 3, 'confirm']` |
| `equal` | Equal to value | `['accept', '1', '必须同意', 1, 'equal']` |

---

## Callback Validation

```php
protected $_validate = [
    ['start_time', 'checkTimeRange', '时间范围不正确', self::VALUE_VALIDATE, 'callback'],
];

// Callback method in model
protected function checkTimeRange($value)
{
    $end_time = I('post.end_time');
    if ($end_time && $value >= $end_time) {
        return false;
    }
    return true;
}

// Callback with parameters
protected function checkCustom($value)
{
    $id = I('post.id', 0, 'intval');

    // Check if code exists (exclude current record)
    $exists = $this->where([
        'code' => $value,
        'id' => ['neq', $id]
    ])->find();

    return !$exists;
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
        $this->error('名称不能为空');
    }

    if (mb_strlen($data['name']) > 200) {
        $this->error('名称不能超过200字符');
    }

    // Model validation
    $result = D('Product')->create($data);
    if ($result === false) {
        $this->error(D('Product')->getError());
    }

    // Save
    $id = D('Product')->add($result);
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
        ['code', 'unique', '商品编码已存在', self::MUST_VALIDATE],

        // Price
        ['price', 'require', '价格不能为空', self::MUST_VALIDATE],
        ['price', '/^\d+(\.\d{1,2})?$/', '价格格式不正确', self::VALUE_VALIDATE, 'regex'],
        ['price', '0.01,999999.99', '价格范围不正确', self::VALUE_VALIDATE, 'between'],

        // Status
        ['status', [0, 1, 2], '状态值不正确', self::VALUE_VALIDATE, 'in'],

        // Custom
        ['stock', 'checkStock', '库存不能为负数', self::VALUE_VALIDATE, 'callback'],
    ];

    protected function checkStock($value)
    {
        return $value >= 0;
    }
}
```

---

## Related Rules

- [FormBuilder API](../formbuilder-api.md) - Form field configuration
- [Model Guide](../../references/model-guide.md) - Model patterns
