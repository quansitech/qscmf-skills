# CRUD Patterns Reference

> QSCMF 开发模式与最佳实践

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
    // 必填
    ['title', 'require', '标题不能为空', self::MUST_VALIDATE],

    // 长度
    ['title', '1,200', '标题长度1-200字符', self::MUST_VALIDATE, 'length'],

    // 唯一
    ['email', '', '邮箱已存在', self::MUST_VALIDATE, 'unique'],

    // 正则
    ['mobile', '/^1[3-9]\d{9}$/', '手机号格式错误', self::MUST_VALIDATE, 'regex'],

    // 值范围
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

## Performance Optimization

### Query Optimization

```php
// ✅ 使用索引字段查询
$where['id'] = $id;

// ❌ 避免 LIKE 前缀通配符
$where['title'] = ['like', '%keyword%'];  // 可以
$where['title'] = ['like', '%keyword'];   // 避免

// ✅ 限制字段
$list = D('Demo')->field('id,title,status')->select();

// ✅ 分页
$list = D('Demo')->page($page, $limit)->select();
```

### Caching

```php
use Qscmf\Lib\Cache\QscmfCache;

$cache = new QscmfCache('demo_list', 3600);

$data = $cache->remember(function() {
    return D('Demo')->select();
});

// 清除缓存
$cache->clear();
```

---

**相关文档**：
- [Admin Controllers](admin-controllers.md)
- [Development Standards](development-standards.md)
