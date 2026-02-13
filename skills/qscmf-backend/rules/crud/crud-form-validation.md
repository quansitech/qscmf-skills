---
title: Form Field Validation Rules
impact: HIGH
impactDescription: Essential for data integrity (20% daily usage)
tags: crud, form, validation, both, v13, v14
---

## Form Field Validation Rules

Complete reference for configuring form field validation in QSCMF applications. Covers both server-side (GyListModel) and client-side (FormItem) validation.

### When to Use This Rule

- You need to add validation to form fields
- You want to ensure data integrity and prevent invalid data
- You need custom validation logic
- You want to understand the difference between client and server-side validation

---

## Overview

QSCMF supports two layers of validation:

1. **Server-Side Validation** (GyListModel `$_validate`) - Always executed, cannot be bypassed
2. **Client-Side Validation** (FormItem rules) - Provides immediate user feedback

**Best Practice:** Use both layers for robust validation.

---

## Server-Side Validation (GyListModel)

### $_validate Format

Define validation rules in your Model class:

```php
<?php
// app/Common/Model/ProductModel.class.php

class ProductModel extends \Gy_Library\GyListModel
{
    protected $_validate = [
        // [field, rule, message, condition, type, when]
        ['title', 'require', '标题不能为空', self::MUST_VALIDATE],
        ['price', 'number', '价格必须是数字', self::MUST_VALIDATE],
        ['email', 'email', '邮箱格式错误', self::EXISTS_VALIDATE],
    ];
}
```

### Validation Rule Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `$field` | string | Field name to validate |
| `$rule` | mixed | Validation rule (built-in or custom) |
| `$message` | string | Error message |
| `$condition` | int | When to validate: `self::MUST_VALIDATE`, `self::EXISTS_VALIDATE`, `self::VALUE_VALIDATE` |
| `$type` | string | Validation type (default: 'regex') |
| `$when` | string | Conditional validation |

### Validation Conditions

```php
self::MUST_VALIDATE    // Always validate (default)
self::EXISTS_VALIDATE  // Validate only if field exists (not empty)
self::VALUE_VALIDATE   // Validate only if field has a specific value
```

---

## Built-in Validation Rules

### 1. require (Required Field)

Field must not be empty.

```php
['title', 'require', '标题不能为空', self::MUST_VALIDATE]

// In migration
$table->string('title')->comment('@title=标题;@type=text;@require=true;');
```

**What it validates:**
- `null` → Invalid
- `''` (empty string) → Invalid
- `'value'` → Valid

### 2. length (Length Validation)

Validate string length within range.

```php
// Format: min,max
['title', '1,200', '标题长度必须在1-200字符之间', self::MUST_VALIDATE, 'length']

// In migration
$table->string('title', 200)->comment('@title=标题;@type=text;@length=1,200;');
```

**Examples:**
```php
['password', '6,20', '密码长度必须在6-20字符之间', self::MUST_VALIDATE, 'length']
['content', '10,5000', '内容长度必须在10-5000字符之间', self::MUST_VALIDATE, 'length']
```

### 3. email (Email Format)

Validate email address format.

```php
['email', 'email', '邮箱格式错误', self::EXISTS_VALIDATE]

// In migration
$table->string('email', 100)->comment('@title=邮箱;@type=email;');
```

**Valid formats:**
- `user@example.com` ✅
- `user.name@example.com` ✅
- `user+tag@example.co.uk` ✅
- `invalid-email` ❌

### 4. url (URL Format)

Validate URL format.

```php
['website', 'url', '网址格式错误', self::EXISTS_VALIDATE]

// In migration
$table->string('website', 500)->comment('@title=网站;@type=url;');
```

**Valid formats:**
- `https://example.com` ✅
- `http://example.com/path` ✅
- `ftp://example.com` ✅
- `not-a-url` ❌

### 5. number (Numeric Validation)

Field must be numeric.

```php
['price', 'number', '价格必须是数字', self::MUST_VALIDATE]
['sort', 'number', '排序必须是数字', self::MUST_VALIDATE]
['quantity', 'number', '数量必须是数字', self::MUST_VALIDATE]
```

**Valid values:**
- `100` ✅
- `99.99` ✅
- `-50` ✅
- `'abc'` ❌

### 6. integer (Integer Validation)

Field must be an integer.

```php
['age', 'integer', '年龄必须是整数', self::MUST_VALIDATE]
['count', 'integer', '数量必须是整数', self::MUST_VALIDATE]
```

### 7. between (Range Validation)

Validate numeric value within range.

```php
// Format: min,max
['age', '18,100', '年龄必须在18-100之间', self::MUST_VALIDATE, 'between']
['price', '0,999999', '价格必须在0-999999之间', self::MUST_VALIDATE, 'between']
```

### 8. in (Value in List)

Field value must be in specified list.

```php
// Format: value1,value2,value3
['status', '0,1,2', '状态值错误', self::MUST_VALIDATE, 'in']
['type', '1,2,3', '类型错误', self::MUST_VALIDATE, 'in']
```

**Common usage with DBCont:**
```php
['status', DBCont::NORMAL_STATUS . ',' . DBCont::DISABLE_STATUS, '状态值错误', self::MUST_VALIDATE, 'in']
```

### 9. regex (Regular Expression)

Custom regex validation.

```php
// Phone number (Chinese mobile)
['mobile', '/^1[3-9]\d{9}$/', '手机号格式错误', self::MUST_VALIDATE, 'regex']

// Postal code
['postcode', '/^\d{6}$/', '邮编格式错误', self::EXISTS_VALIDATE, 'regex']

// Username (alphanumeric, 4-20 characters)
['username', '/^[a-zA-Z0-9]{4,20}$/', '用户名只能包含字母和数字，4-20位', self::MUST_VALIDATE, 'regex']

// ID card (Chinese)
['id_card', '/^\d{17}[\dXx]$/', '身份证号格式错误', self::EXISTS_VALIDATE, 'regex']
```

**Common Regex Patterns:**
```php
// Chinese mobile phone
'/^1[3-9]\d{9}$/'

// Landline (with area code)
'/^0\d{2,3}-?\d{7,8}$/'

// Email (basic)
'/^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/'

// URL (basic)
'/^https?:\/\/.+/'

// IPv4 address
'/^((25[0-5]|2[0-4]\d|[01]?\d\d?)\.){3}(25[0-5]|2[0-4]\d|[01]?\d\d?)$/'

// Date (YYYY-MM-DD)
'/^\d{4}-\d{2}-\d{2}$/'

// Hex color code
'/^#[0-9A-Fa-f]{6}$/'
```

### 10. equal (Field Equality)

Field must match another field.

```php
// Password confirmation
['password_confirm', 'password', '两次密码不一致', self::MUST_VALIDATE, 'equal']

// Email confirmation
['email_confirm', 'email', '两次邮箱不一致', self::MUST_VALIDATE, 'equal']
```

### 11. unique (Unique Database Record)

Field value must be unique in database.

```php
['email', '', '邮箱已存在', self::MUST_VALIDATE, 'unique']
['username', '', '用户名已存在', self::MUST_VALIDATE, 'unique']
```

**Usage in Model:**
```php
protected $_validate = [
    // For insert
    ['email', '', '邮箱已存在', self::MUST_VALIDATE, 'unique'],

    // For update (exclude current record)
    ['email', '', '邮箱已存在', self::EXISTS_VALIDATE, 'unique', function($data) {
        return ['id' => ['neq', $data['id']]];
    }],
];
```

### 12. ip (IP Address)

Validate IP address format.

```php
['ip_address', 'ip', 'IP地址格式错误', self::EXISTS_VALIDATE]
```

### 13. date (Date Format)

Validate date format.

```php
['birth_date', 'date', '日期格式错误', self::EXISTS_VALIDATE]
['publish_date', 'date', '日期格式错误', self::MUST_VALIDATE]
```

### 14. callback (Custom Callback)

Custom validation function.

```php
['username', 'checkUsernameUnique', '用户名已存在', self::MUST_VALIDATE, 'callback']
```

**Define callback method in Model:**
```php
protected function checkUsernameUnique($username)
{
    $exists = $this->where(['username' => $username])->find();
    return !$exists;
}
```

**Advanced callback with parameters:**
```php
protected $_validate = [
    ['password', 'checkPasswordStrength', '密码强度不够', self::MUST_VALIDATE, 'callback'],
];

protected function checkPasswordStrength($password)
{
    // Must contain at least one lowercase, one uppercase, one number
    if (!preg_match('/[a-z]/', $password)) {
        return false;
    }
    if (!preg_match('/[A-Z]/', $password)) {
        return false;
    }
    if (!preg_match('/[0-9]/', $password)) {
        return false;
    }
    return true;
}
```

---

## Client-Side Validation (FormItem)

### v13 FormItem Validation

```php
<?php
// app/Admin/Controller/ProductController.class.php

protected function buildFormOptions($builder)
{
    $builder->addFormItem('title', 'text', '标题')
        ->setRule('required', true)
        ->setRule('minlength', 1)
        ->setRule('maxlength', 200);

    $builder->addFormItem('price', 'number', '价格')
        ->setRule('required', true)
        ->setRule('min', 0)
        ->setRule('max', 999999)
        ->setRule('number', true);

    $builder->addFormItem('email', 'text', '邮箱')
        ->setRule('email', true);

    $builder->addFormItem('mobile', 'text', '手机号')
        ->setRule('pattern', '/^1[3-9]\d{9}$/')
        ->setRule('message', '手机号格式错误');
}
```

### v14 AntdAdmin Validation

```php
<?php
// app/Admin/Controller/ProductController.class.php

use Qscmf\Lib\AntdAdmin\Layouts\FormItem\Validator\Required;
use Qscmf\Lib\AntdAdmin\Layouts\FormItem\Validator\Email;
use Qscmf\Lib\AntdAdmin\Layouts\FormItem\Validator\Number;
use Qscmf\Lib\AntdAdmin\Layouts\FormItem\Validator\Length;
use Qscmf\Lib\AntdAdmin\Layouts\FormItem\Validator\Regex;
use Qscmf\Lib\AntdAdmin\Layouts\FormItem\Validator\Callback;

protected function buildFormColumns($container)
{
    // Required validation
    $container->text('title', '标题')
        ->addRule(new Required('标题不能为空'))
        ->addRule(new Length(1, 200, '标题长度1-200字符'));

    // Number validation
    $container->number('price', '价格')
        ->addRule(new Required('价格不能为空'))
        ->addRule(new Number()->min(0)->max(999999), '价格必须在0-999999之间');

    // Email validation
    $container->text('email', '邮箱')
        ->addRule(new Email('邮箱格式错误'));

    // Regex validation
    $container->text('mobile', '手机号')
        ->addRule(new Regex('/^1[3-9]\d{9}$/', '手机号格式错误'));

    // Custom callback validation
    $container->text('username', '用户名')
        ->addRule(new Required('用户名不能为空'))
        ->addRule(new Callback(function($data) {
            $exists = D('User')->where(['username' => $data['username']])->find();
            return !$exists;
        }, '用户名已存在'));
}
```

---

## Complete Validator Reference

### Required Validator

```php
// v13
->setRule('required', true)

// v14
use Qscmf\Lib\AntdAdmin\Layouts\FormItem\Validator\Required;
->addRule(new Required('错误消息'))
```

### Email Validator

```php
// v13
->setRule('email', true)

// v14
use Qscmf\Lib\AntdAdmin\Layouts\FormItem\Validator\Email;
->addRule(new Email('邮箱格式错误'))
```

### Length Validator

```php
// v13
->setRule('minlength', 1)
->setRule('maxlength', 200)

// v14
use Qscmf\Lib\AntdAdmin\Layouts\FormItem\Validator\Length;
->addRule(new Length(1, 200, '长度必须在1-200字符'))
```

### Number Validator

```php
// v13
->setRule('number', true)
->setRule('min', 0)
->setRule('max', 999999)

// v14
use Qscmf\Lib\AntdAdmin\Layouts\FormItem\Validator\Number;
->addRule(new Number()->min(0)->max(999999), '数字范围错误')
```

### Regex Validator

```php
// v13
->setRule('pattern', '/^1[3-9]\d{9}$/')
->setRule('message', '手机号格式错误')

// v14
use Qscmf\Lib\AntdAdmin\Layouts\FormItem\Validator\Regex;
->addRule(new Regex('/^1[3-9]\d{9}$/', '手机号格式错误'))
```

### URL Validator

```php
// v13
->setRule('url', true)

// v14
use Qscmf\Lib\AntdAdmin\Layouts\FormItem\Validator\Url;
->addRule(new Url('网址格式错误'))
```

### Date Validator

```php
// v13
->setRule('date', true)

// v14
use Qscmf\Lib\AntdAdmin\Layouts\FormItem\Validator\Date;
->addRule(new Date('日期格式错误'))
```

### Callback Validator (Custom)

```php
// v14 only
use Qscmf\Lib\AntdAdmin\Layouts\FormItem\Validator\Callback;

// Simple callback
->addRule(new Callback(function($value) {
    return $value !== '';
}, '值不能为空'))

// Callback with access to all form data
->addRule(new Callback(function($data) {
    // $data contains all form fields
    return $data['password'] === $data['password_confirm'];
}, '两次密码不一致'))

// Async callback (AJAX validation)
->addRule(new Callback(function($value) use ($controller) {
    $exists = D('User')->where(['email' => $value])->find();
    return !$exists;
}, '邮箱已存在'))
```

---

## Common Validation Patterns

### Pattern 1: User Registration

```php
<?php
// app/Common/Model/UserModel.class.php

class UserModel extends \Gy_Library\GyListModel
{
    protected $_validate = [
        // Username: required, 4-20 characters, alphanumeric, unique
        ['username', 'require', '用户名不能为空', self::MUST_VALIDATE],
        ['username', '4,20', '用户名长度4-20字符', self::MUST_VALIDATE, 'length'],
        ['username', '/^[a-zA-Z0-9_]+$/', '用户名只能包含字母、数字和下划线', self::MUST_VALIDATE, 'regex'],
        ['username', 'checkUsernameUnique', '用户名已存在', self::MUST_VALIDATE, 'callback'],

        // Email: required, valid format, unique
        ['email', 'require', '邮箱不能为空', self::MUST_VALIDATE],
        ['email', 'email', '邮箱格式错误', self::MUST_VALIDATE],
        ['email', 'checkEmailUnique', '邮箱已存在', self::MUST_VALIDATE, 'callback'],

        // Password: required, 6-20 characters
        ['password', 'require', '密码不能为空', self::MUST_VALIDATE],
        ['password', '6,20', '密码长度6-20字符', self::MUST_VALIDATE, 'length'],

        // Mobile: optional, valid format if provided
        ['mobile', '/^1[3-9]\d{9}$/', '手机号格式错误', self::EXISTS_VALIDATE, 'regex'],
    ];

    protected function checkUsernameUnique($username)
    {
        return !$this->where(['username' => $username])->find();
    }

    protected function checkEmailUnique($email)
    {
        return !$this->where(['email' => $email])->find();
    }
}
```

### Pattern 2: Product Validation

```php
<?php
// app/Common/Model/ProductModel.class.php

class ProductModel extends \Gy_Library\GyListModel
{
    protected $_validate = [
        // Title: required, length
        ['title', 'require', '商品名称不能为空', self::MUST_VALIDATE],
        ['title', '1,200', '商品名称1-200字符', self::MUST_VALIDATE, 'length'],

        // Price: required, number, range
        ['price', 'require', '价格不能为空', self::MUST_VALIDATE],
        ['price', 'number', '价格必须是数字', self::MUST_VALIDATE],
        ['price', '0,999999', '价格范围0-999999', self::MUST_VALIDATE, 'between'],

        // Stock: required, integer, non-negative
        ['stock', 'require', '库存不能为空', self::MUST_VALIDATE],
        ['stock', 'number', '库存必须是数字', self::MUST_VALIDATE],
        ['stock', '0,', '库存不能为负数', self::MUST_VALIDATE, 'between'],

        // Category: required, must exist
        ['cate_id', 'require', '分类不能为空', self::MUST_VALIDATE],
        ['cate_id', 'checkCategoryExists', '分类不存在', self::MUST_VALIDATE, 'callback'],

        // Status: must be valid
        ['status', '0,1', '状态值错误', self::MUST_VALIDATE, 'in'],

        // Images: optional, valid format if provided
        ['images', 'checkImages', '图片格式错误', self::VALUE_VALIDATE, 'callback'],
    ];

    protected function checkCategoryExists($cate_id)
    {
        return D('Category')->where(['id' => $cate_id])->find();
    }

    protected function checkImages($images)
    {
        if (empty($images)) {
            return true; // Optional field
        }

        $image_array = is_array($images) ? $images : explode(',', $images);
        foreach ($image_array as $image_id) {
            if (!D('FilePic')->find($image_id)) {
                return false;
            }
        }
        return true;
    }
}
```

### Pattern 3: Conditional Validation

Validate fields only when certain conditions are met.

```php
<?php
// app/Common/Model/OrderModel.class.php

class OrderModel extends \Gy_Library\GyListModel
{
    protected $_validate = [
        // Always validate
        ['order_no', 'require', '订单号不能为空', self::MUST_VALIDATE],

        // Validate only when payment type is online payment
        ['transaction_id', 'require', '交易号不能为空', self::VALUE_VALIDATE, 'callback', 'checkOnlinePayment'],

        // Validate discount only when discount > 0
        ['discount_reason', 'require', '折扣原因不能为空', self::VALUE_VALIDATE, 'callback', 'checkDiscountReason'],
    ];

    // Validate transaction_id only when payment_type is online
    protected function checkOnlinePayment($data)
    {
        if (in_array($data['payment_type'], [1, 2])) { // WeChat Pay, Alipay
            return !empty($data['transaction_id']);
        }
        return true;
    }

    // Validate discount_reason only when discount > 0
    protected function checkDiscountReason($data)
    {
        if (isset($data['discount']) && $data['discount'] > 0) {
            return !empty($data['discount_reason']);
        }
        return true;
    }
}
```

### Pattern 4: Cross-Field Validation

Validate relationships between multiple fields.

```php
<?php
// app/Common/Model/EventModel.class.php

class EventModel extends \Gy_Library\GyListModel
{
    protected $_validate = [
        // Start date before end date
        ['end_date', 'checkDateRange', '结束日期必须大于开始日期', self::MUST_VALIDATE, 'callback'],

        // Max participants > min participants
        ['max_participants', 'checkParticipantRange', '最大人数必须大于最小人数', self::MUST_VALIDATE, 'callback'],

        // Password confirmation
        ['password_confirm', 'password', '两次密码不一致', self::MUST_VALIDATE, 'equal'],
    ];

    protected function checkDateRange($end_date, $data)
    {
        if (empty($data['start_date']) || empty($end_date)) {
            return true;
        }
        return strtotime($end_date) > strtotime($data['start_date']);
    }

    protected function checkParticipantRange($max, $data)
    {
        if (empty($data['min_participants']) || empty($max)) {
            return true;
        }
        return $max > $data['min_participants'];
    }
}
```

---

## Advanced Validation Scenarios

### Scenario 1: Password Strength

```php
<?php
// Model
protected $_validate = [
    ['password', 'checkPasswordStrength', '密码强度不够', self::MUST_VALIDATE, 'callback'],
];

protected function checkPasswordStrength($password)
{
    // At least 8 characters
    if (strlen($password) < 8) {
        return false;
    }

    // Must contain lowercase
    if (!preg_match('/[a-z]/', $password)) {
        return false;
    }

    // Must contain uppercase
    if (!preg_match('/[A-Z]/', $password)) {
        return false;
    }

    // Must contain number
    if (!preg_match('/[0-9]/', $password)) {
        return false;
    }

    // Must contain special character
    if (!preg_match('/[^a-zA-Z0-9]/', $password)) {
        return false;
    }

    return true;
}

// Form (v14)
$container->text('password', '密码')
    ->addRule(new Required('密码不能为空'))
    ->addRule(new Regex('/^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$/',
        '密码必须至少8位，包含大小写字母、数字和特殊字符'));
```

### Scenario 2: Unique with Update Exception

```php
<?php
// Model
protected $_validate = [
    // For insert
    ['email', '', '邮箱已存在', self::MUST_VALIDATE, 'unique'],
];

// Override validation for update
public function update($data = '', $options = [])
{
    // Remove unique validation for current record
    if (isset($data['id'])) {
        foreach ($this->_validate as $key => $rule) {
            if ($rule[0] === 'email' && $rule[4] === 'unique') {
                unset($this->_validate[$key]);
                $this->_validate[] = [
                    'email',
                    '',
                    '邮箱已存在',
                    self::EXISTS_VALIDATE,
                    'unique',
                    function($data) {
                        return ['id' => ['neq', $data['id']]];
                    }
                ];
            }
        }
    }

    return parent::update($data, $options);
}
```

### Scenario 3: File Upload Validation

```php
<?php
// Model
protected $_validate = [
    ['cover', 'checkImage', '封面图片格式错误', self::MUST_VALIDATE, 'callback'],
    ['attachment', 'checkFile', '附件格式错误', self::EXISTS_VALIDATE, 'callback'],
];

protected function checkImage($cover_id)
{
    if (empty($cover_id)) {
        return false;
    }

    $file = D('FilePic')->find($cover_id);
    if (!$file) {
        return false;
    }

    // Check file extension
    $allowed = ['jpg', 'jpeg', 'png', 'gif', 'webp'];
    $ext = strtolower(pathinfo($file['name'], PATHINFO_EXTENSION));

    return in_array($ext, $allowed);
}

protected function checkFile($file_id)
{
    if (empty($file_id)) {
        return true; // Optional
    }

    $file = D('FilePic')->find($file_id);
    if (!$file) {
        return false;
    }

    // Check file size (max 10MB)
    if ($file['size'] > 10 * 1024 * 1024) {
        return false;
    }

    // Check file type
    $allowed = ['pdf', 'doc', 'docx', 'xls', 'xlsx'];
    $ext = strtolower(pathinfo($file['name'], PATHINFO_EXTENSION));

    return in_array($ext, $allowed);
}
```

---

## Validation Error Handling

### Displaying Errors (v13)

```php
<?php
// Controller
public function save()
{
    $data = I('post.');
    $model = D('Product');

    if ($model->createAdd($data) === false) {
        // Validation failed
        $error = $model->getError();
        $this->error($error);
    }

    $this->success('保存成功');
}
```

### Displaying Errors (v14)

```php
<?php
// Controller
public function save()
{
    $data = I('post.');
    $model = D('Product');

    if ($model->createAdd($data) === false) {
        // Validation failed
        $error = $model->getError();

        // Return JSON for AJAX form
        if (IS_AJAX) {
            $this->ajaxReturn([
                'success' => false,
                'message' => $error,
                'errors' => $model->getErrorDetail() // Detailed errors by field
            ]);
        }

        $this->error($error);
    }

    $this->success('保存成功');
}
```

### Custom Error Messages

```php
<?php
// Model
protected $_validate = [
    // Dynamic error messages
    ['age', 'checkAge', '', self::MUST_VALIDATE, 'callback'],
];

protected function checkAge($age)
{
    if ($age < 18) {
        // Set dynamic error message
        $this->setError('年龄必须年满18周岁');
        return false;
    }

    if ($age > 100) {
        $this->setError('请输入有效的年龄');
        return false;
    }

    return true;
}
```

---

## Version Differences

### v13 vs v14

| Feature | v13 (Legacy) | v14 (Modern) |
|---------|--------------|--------------|
| **Server Validation** | `$_validate` array | Same `$_validate` array |
| **Client Validation** | `setRule()` method | Validator classes (`Required`, `Email`, etc.) |
| **Error Display** | `$this->error()` | JSON response with field-level errors |
| **Async Validation** | Not supported | `Callback` with AJAX |
| **Regex Support** | Built-in | Full regex support via `Regex` validator |

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| Validation not running | Check `$_validate` array syntax. Ensure `$condition` is correct. |
| Custom callback not called | Verify callback method exists and is `public` or `protected`. |
| Regex not matching | Use `#` or `/` delimiters. Test regex online first. |
| Unique validation fails on update | Use conditional validation or override validation for updates. |
| File validation not working | Check if file is uploaded before validating. Use `EXISTS_VALIDATE`. |
| Cross-field validation fails | Use callback with access to full `$data` array. |
| Error message not showing | Check if `getError()` returns string or array. Handle both cases. |
| Client validation bypassed | Always use server-side validation (`$_validate`) as backup. |

---

## Related Rules

- [Table Columns v13](./crud-table-columns-v13.md) - Form field types
- [Table Columns v14](./crud-table-columns-v14.md) - Form field types
- [Form Builder](../../references/admin-controllers.md#form-builder) - FormBuilder API
- [Model Guide](../../references/model-guide.md) - GyListModel reference

---

## Best Practices

1. **Always validate server-side** - Client validation can be bypassed
2. **Use both validation layers** - Client for UX, server for security
3. **Provide clear error messages** - Tell user exactly what's wrong
4. **Use regex carefully** - Test patterns thoroughly, comment complex patterns
5. **Validate file uploads** - Check type, size, and dimensions
6. **Use callback for complex logic** - Keep validation logic in Model, not Controller
7. **Return proper error responses** - AJAX forms expect JSON with field-level errors
8. **Sanitize input before validation** - Trim strings, remove special characters
9. **Validate foreign keys** - Ensure referenced records exist
10. **Test validation thoroughly** - Try invalid inputs, edge cases, and boundary values
