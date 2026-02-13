# CRUD Patterns Reference

> QSCMF 开发模式与最佳实践指南

## Mode Selection Decision Tree

```
需要什么功能？
│
├─ 后台管理 CRUD
│  ├─ 简单 CRUD？
│  │  → Standard CRUD (QsListController + AntdAdmin)
│  │     - 单表操作
│  │     - 基础增删改查
│  │
│  └─ 多个相似模块？
│     → Abstract Base pattern
│        - 抽象基类
│        - 共同逻辑复用
│
├─ RESTful API
│  └─ API Controller pattern (RestController)
│     - gets(), detail(), save(), update(), delete()
│
├─ 复杂业务逻辑
│  ├─ 批量操作？
│  │  → Custom controller + RedisLock
│  │
│  ├─ 异步任务？
│  │  → Queue + Job
│  │
│  └─ 外部 API？
│     → Wall class + Mock testing
│
└─ 前端页面
   └─ HomeController + Inertia.js + React/TS
```

## Field Type Configuration

### AntdAdmin Form Types

```yaml
# 基础类型
text:         单行文本
textarea:     多行文本
number:       数字
select:       下拉选择
radio:        单选
checkbox:     多选
date:         日期
time:         时间
datetime:     日期时间
switch:       开关

# 文件类型
image:        图片上传
file:         文件上传
link:         链接

# 富文本
ueditor:      UEditor 富文本

# 特殊
cascader:     级联选择
tree:         树形选择
```

### Field Naming Conventions

```php
// 内容字段
*_content → ueditor
*_desc → textarea
*_remark → textarea

// 日期时间
*_date → date
*_time → time
*_at → datetime

// 关联字段
*_id → select
cate_id → select
user_id → select

// 状态
status → select
*_status → select

// 图片/文件
cover → image
cover_id → image
*_image → image
file_id → file

// 排序
sort → number
```

## Validation Rules

### GyListModel Rules

```php
protected $_validate = [
    // 必填验证
    ['title', 'require', '标题不能为空', self::MUST_VALIDATE],

    // 长度验证
    ['title', '1,200', '标题长度1-200字符', self::MUST_VALIDATE, 'length'],

    // 唯一验证
    ['email', '', '邮箱已存在', self::MUST_VALIDATE, 'unique'],

    // 正则验证
    ['mobile', '/^1[3-9]\d{9}$/', '手机号格式错误', self::MUST_VALIDATE, 'regex'],

    // 值范围验证
    ['status', '0,1,2', '状态值错误', self::MUST_VALIDATE, 'in'],
];
```

### AntdAdmin Form Rules

```php
use Qscmf\Lib\AntdAdmin\Layouts\FormItem\Validator\Required;
use Qscmf\Lib\AntdAdmin\Layouts\FormItem\Validator\Email;
use Qscmf\Lib\AntdAdmin\Layouts\FormItem\Validator\Length;

$columns->text('title', '标题')
    ->addRule(new Required())
    ->addRule(new Length(1, 200));

$columns->text('email', '邮箱')
    ->addRule(new Email());
```

## Business Logic Encapsulation

### Save Hook

```php
public function save()
{
    $data = I('post.');

    // 前置处理
    $data['create_time'] = time();
    $data['admin_id'] = session('admin_id');

    $result = parent::save();

    // 后置处理
    if ($result->status) {
        // 同步到其他表
        // 清除缓存
        // 发送通知
    }

    return $result;
}
```

### Delete Hook

```php
public function delete()
{
    $id = I('get.id', 0, 'intval');

    // 检查依赖
    $hasChildren = D('Child')->where(['parent_id' => $id])->count();
    if ($hasChildren) {
        $this->error('存在子记录，无法删除');
    }

    return parent::delete();
}
```

### Custom Validation Before Save

```php
public function save()
{
    $data = I('post.');

    // 自定义业务验证
    if ($data['type'] == 'special' && empty($data['special_field'])) {
        $this->error('特殊类型必须填写特殊字段');
    }

    return parent::save();
}
```

## Performance Optimization

### Query Optimization

```php
// ✅ 使用索引字段查询
$where['id'] = $id;

// ❌ 避免 LIKE 前缀通配符
$where['title'] = ['like', '%keyword%'];  // 可以
$where['title'] = ['like', '%keyword'];   // 避免

// ✅ 限制字段
$list = D('TableName')->field('id,title,status')->select();

// ✅ 分页
$list = D('TableName')->page($page, $limit)->select();

// ✅ 使用索引进行排序
$list = D('TableName')->order('id DESC')->select();
```

### Caching Strategy

```php
use Qscmf\Lib\Cache\QscmfCache;

// 简单缓存
$cache = new QscmfCache('cache_key', 3600);

$data = $cache->remember(function() {
    return D('TableName')->select();
});

// 清除缓存
$cache->clear();

// 带标签的缓存（批量清除）
$cache = new QscmfCache('cache_key', 3600, 'category_tag');
// 清除所有同类缓存
QscmfCache::clearTag('category_tag');
```

### Batch Operations

```php
// ✅ 使用批量插入
$data = [
    ['name' => 'item1', 'status' => 1],
    ['name' => 'item2', 'status' => 1],
];
D('TableName')->addAll($data);

// ✅ 使用事务
D('TableName')->startTrans();
try {
    D('TableName')->add($data1);
    D('RelatedTable')->add($data2);
    D('TableName')->commit();
} catch (\Exception $e) {
    D('TableName')->rollback();
}
```

## Concurrency Control

### Redis Lock Pattern

```php
use Qscmf\Lib\Redis\RedisLock;

public function batchProcess()
{
    $lock = new RedisLock('batch_process_' . $this->uid);

    if (!$lock->acquire()) {
        $this->error('操作进行中，请稍候');
    }

    try {
        // 批量逻辑
        // ...
    } finally {
        $lock->release();
    }
}
```

### Transaction Isolation

```php
public function complexOperation()
{
    $model = D('TableName');
    $model->startTrans();

    try {
        // 操作1
        $result1 = $model->where(['id' => $id])->save(['status' => 1]);

        // 操作2
        $result2 = D('Related')->add(['related_id' => $id]);

        if ($result1 && $result2) {
            $model->commit();
            return true;
        } else {
            $model->rollback();
            return false;
        }
    } catch (\Exception $e) {
        $model->rollback();
        throw $e;
    }
}
```

## Data Validation Patterns

### Model Layer Validation

```php
class TableNameModel extends GyListModel
{
    protected $_validate = [
        // 必填
        ['title', 'require', '标题不能为空', self::MUST_VALIDATE],

        // 唯一
        ['code', '', '编码已存在', self::MUST_VALIDATE, 'unique'],

        // 正则
        ['phone', '/^1[3-9]\d{9}$/', '手机号格式错误', self::EXISTS_VALIDATE, 'regex'],

        // 范围
        ['status', '0,1,2', '状态值错误', self::EXISTS_VALIDATE, 'in'],
    ];
}
```

### Controller Layer Validation

```php
public function save()
{
    $data = I('post.');

    // 业务规则验证
    if ($data['end_time'] < $data['start_time']) {
        $this->error('结束时间不能早于开始时间');
    }

    // 权限验证
    if (! $this->checkPermission($data)) {
        $this->error('无权操作');
    }

    return parent::save();
}
```

### Custom Validation Methods

```php
class TableNameModel extends GyListModel
{
    // 自定义验证方法
    protected function checkComplexRule($field)
    {
        $value = $_POST[$field];

        // 复杂验证逻辑
        if (strlen($value) < 10) {
            return false;
        }

        if (!preg_match('/^[A-Z]/', $value)) {
            return false;
        }

        return true;
    }
}
```

## Error Handling

### Standard Error Response

```php
// 在控制器中
public function save()
{
    try {
        $result = parent::save();

        if (! $result->status) {
            $this->error($result->info);
        }

        return $result;

    } catch (\Exception $e) {
        // 记录日志
        sysLogs('操作失败: ' . $e->getMessage());

        // 返回错误
        $this->error('系统错误，请稍后重试');
    }
}
```

### Transaction Error Handling

```php
public function complexSave()
{
    $model = D('TableName');
    $model->startTrans();

    try {
        // 业务逻辑
        $id = $model->add($data);
        D('Related')->add(['foreign_id' => $id]);

        $model->commit();
        return $this->success('保存成功');

    } catch (\Exception $e) {
        $model->rollback();

        // 记录详细错误
        sysLogs('保存失败: ' . $e->getMessage(), 'error');

        return $this->error('保存失败');
    }
}
```

## Logging Best Practices

```php
// 信息日志
sysLogs('操作描述, id:' . $id);

// 带上下文的日志
sysLogs(sprintf(
    '用户 %s 操作了记录 %s，结果: %s',
    session('admin_id'),
    $id,
    $result ? '成功' : '失败'
));

// 错误日志
sysLogs('错误详情: ' . $error_message, 'error');

// 调试日志
sysLogs('调试信息: ' . json_encode($debug_data), 'debug');
```

## Best Practices

### 1. 使用常量而非魔法值

```php
// ✅ 好的做法
use Gy_Library\DBCont;

$where['status'] = DBCont::NORMAL_STATUS;

// ❌ 避免
$where['status'] = 1;
```

### 2. 验证规则分层

- **模型层**：数据完整性验证（必填、格式、唯一性）
- **控制器层**：业务规则验证（权限、状态转换、业务逻辑）
- **表单层**：用户输入验证（前端反馈）

### 3. 查询优化原则

```php
// ✅ 使用索引字段
$where['id'] = $id;

// ✅ 限制查询字段
$field = 'id,name,status';
$list = D('TableName')->field($field)->select();

// ✅ 合理使用分页
$page = I('get.p', 1, 'intval');
$limit = C('ADMIN_PER_PAGE_NUM', null, 20);
$list = D('TableName')->page($page, $limit)->select();
```

### 4. 安全性考虑

```php
// ✅ 输入过滤
$id = I('get.id', 0, 'intval');

// ✅ 使用参数绑定
$result = D('TableName')->where(['id' => $id])->find();

// ❌ 避免直接拼接 SQL
$sql = "SELECT * FROM table WHERE id = $id";  // 危险
```

### 5. 代码复用

```php
// 将通用逻辑提取到 Trait
trait CommonOperations
{
    protected function updateStatus($id, $status)
    {
        return D($this->modelName)
            ->where(['id' => $id])
            ->save(['status' => $status]);
    }
}

// 在控制器中使用
class XxxController extends QsListController
{
    use CommonOperations;
}
```

### 6. 错误处理一致性

```php
// 统一的错误响应格式
if ($error) {
    return $this->error('错误描述');  // 返回标准错误
}

// 统一的成功响应格式
return $this->success('成功描述', $data);
```

### 7. 资源清理

```php
public function complexOperation()
{
    $lock = new RedisLock('operation_key');

    try {
        $lock->acquire();
        D('TableName')->startTrans();

        // 业务逻辑

        D('TableName')->commit();
        return true;

    } catch (\Exception $e) {
        D('TableName')->rollback();
        throw $e;

    } finally {
        $lock->release();
    }
}
```

### 8. 缓存策略

```php
// 读多写少的数据：使用长期缓存
$cache = new QscmfCache('static_data', 86400);

// 频繁更新的数据：使用短期缓存或缓存标签
$cache = new QscmfCache('dynamic_data', 300, 'dynamic_tag');

// 更新时清除缓存
public function save()
{
    $result = parent::save();

    if ($result->status) {
        $cache = new QscmfCache('dynamic_data', 0, 'dynamic_tag');
        $cache->clear();
    }

    return $result;
}
```

---

**相关文档**：
- [Admin Controllers](admin-controllers.md) - 后台管理控制器详解
- [API Controllers](api-controllers.md) - RESTful API 开发
- [Abstract Base Patterns](abstract-base-patterns.md) - 抽象基类模式
- [Development Standards](development-standards.md) - 开发规范指南
