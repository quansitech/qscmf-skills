# Where Query Reference

> QSCMF ThinkPHP 查询条件语法参考

## 比较运算符

### 等值查询

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
```

## 模糊查询

```php
// LIKE 模糊查询（包含）
$where['title'] = ['like', '%keyword%'];

// LIKE 前缀匹配（有索引）
$where['title'] = ['like', 'keyword%'];

// LIKE 后缀匹配
$where['title'] = ['like', '%keyword'];

// 多字段 LIKE（需要使用 _logic）
$where['_logic'] = 'or';
$where['title'] = ['like', '%a%'];
$where['content'] = ['like', '%b%'];
```

## 范围查询

```php
// IN 查询
$where['status'] = ['in', '0,1,2'];
// 或使用数组
$where['status'] = ['in', [0, 1, 2]];

// NOT IN 查询
$where['status'] = ['notin', '0,1'];

// BETWEEN 范围查询（数值）
$where['create_time'] = ['between', [strtotime('2024-01-01'), time()]];

// BETWEEN 范围查询（字符串）
$where['price'] = ['between', ['100', '500']];
```

## 复杂条件

### 正则表达式

```php
// REGEXP 正则查询（逗号分隔的 ID 匹配）
$tag_str = str_replace(',', '|', $tag_id);
$where[] = "tag_id REGEXP '(^|,)($tag_str)(,|$)'";

// 正则匹配邮箱
$where['email'] = ['like', '%@example.com'];
```

### 条件组

```php
// OR 查询（多条件满足其一）
$where['_logic'] = 'or';
$where['title'] = ['like', '%keyword%'];
$where['content'] = ['like', '%keyword%'];

// 复杂组合（使用字符串）
$where[] = "(cate_id = 1 OR status = 1) AND create_time > " . strtotime('2024-01-01');
```

### NULL 查询

```php
// IS NULL
$where['field'] = ['exp', 'IS NULL'];

// IS NOT NULL
$where['field'] = ['exp', 'IS NOT NULL'];
```

## 时间查询

```php
// 时间戳范围
$where['create_time'] = ['between', [strtotime('2024-01-01'), time()]];

// 今天
$where['create_time'] = ['between', [strtotime('today'), strtotime('tomorrow') - 1]];

// 最近7天
$where['create_time'] = ['egt', strtotime('-7 days')];

// 指定日期
$where['create_time'] = ['between', [
    strtotime('2024-01-01 00:00:00'),
    strtotime('2024-01-01 23:59:59')
]];
```

## 数组条件

```php
// 多条件 AND（默认）
$where = [
    'cate_id' => 1,
    'status' => 1,
    'title' => ['like', '%keyword%']
];

// 多条件 OR
$where['_logic'] = 'or';
$where['cate_id'] = 1;
$where['status'] = 1;

// 表达式查询
$where['id'] = ['exp', '> 0'];
$where['count'] = ['exp', 'count + 1'];
```

## 聚合查询

```php
// COUNT
$count = D('Xxx')->where($where)->count();

// SUM
$sum = D('Xxx')->where($where)->sum('price');

// AVG
$avg = D('Xxx')->where($where)->avg('score');

// MAX
$max = D('Xxx')->where($where)->max('views');

// MIN
$min = D('Xxx')->where($where)->min('price');
```

## JOIN 关联查询

```php
// LEFT JOIN
$list = D('Xxx')
    ->alias('x')
    ->join('LEFT JOIN qs_cate c ON x.cate_id = c.id')
    ->field('x.*, c.name as cate_name')
    ->where(['x.status' => 1])
    ->select();

// 多表 JOIN
$list = D('Xxx')
    ->alias('x')
    ->join('LEFT JOIN qs_cate c ON x.cate_id = c.id')
    ->join('LEFT JOIN qs_user u ON x.user_id = u.id')
    ->field('x.*, c.name as cate_name, u.username')
    ->select();

// INNER JOIN
$list = D('Xxx')
    ->alias('x')
    ->join('INNER JOIN qs_cate c ON x.cate_id = c.id')
    ->where(['c.status' => 1])
    ->select();
```

## 排序

```php
// 单字段排序
$order = 'id desc';

// 多字段排序
$order = 'sort asc, id desc';

// 字符串排序
$order = 'create_time DESC, update_time DESC';

// 应用排序
$list = D('Xxx')->where($where)->order($order)->select();
```

## 分页

```php
// ThinkPHP 分页
$page = I('get.page', 1);
$per_page = 20;

$list = D('Xxx')
    ->where($where)
    ->page($page, $per_page)
    ->select();

// 获取总数
$count = D('Xxx')->where($where)->count();
```

## 字段选择

```php
// 指定字段
$list = D('Xxx')->field('id,title,status')->select();

// 排除字段
$list = D('Xxx')->field('content', true)->select();

// 字段别名
$list = D('Xxx')
    ->alias('x')
    ->field('x.id, x.title, c.name as cate_name')
    ->select();

// 聚合字段
$list = D('Xxx')->field('id, count(*) as count')->group('cate_id')->select();
```

## 批量查询优化

```php
// 批量获取关联数据
$user_ids = array_column($list, 'user_id');
$user_list = D('User')->where(['id' => ['IN', $user_ids]])->getField('id,username', true);

foreach ($list as &$item) {
    $item['username'] = $user_list[$item['user_id']]['username'] ?? '';
}
```

## 相关文档

- [Model Guide](model-guide.md) - 模型开发指南
- [Migration Guide](migration-guide.md) - 迁移文件指南
- [Admin Controllers](admin-controllers.md) - 控制器中使用模型
