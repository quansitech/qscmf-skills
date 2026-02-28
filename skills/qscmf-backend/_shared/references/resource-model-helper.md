# ResourceModelHelper 资源联合查询

> 统一查询 Resource 和 Basics 两种内容类型

## 概述

`ResourceModelHelper` 是 QSCMF 项目中用于联合查询两种内容类型的核心工具类。

**文件位置**: `app/Common/Lib/ResourceModelHelper.class.php`

## 支持的内容类型

| 类型 | 表名 | 模型 |
|------|------|------|
| `ResourceContent` | `qs_resource_content` | ResourceContentModel |
| `BasicsContent` | `qs_basics_content` | BasicsContentModel |

## API 参考

### getList() - 分页查询

```php
public static function getList(
    array $map = [],
    int $page = 1,
    int $per_page = 20,
    string $order = ''
): array
```

**参数**:
- `$map` - 查询条件数组
- `$page` - 页码，从1开始
- `$per_page` - 每页数量
- `$order` - 排序规则，如 `'id desc'`

**返回**: 包含 `type`, `show_type`, `uq_id` 等字段的记录数组

**示例**:
```php
use Common\Lib\ResourceModelHelper;

$list = ResourceModelHelper::getList([
    'keyword' => '搜索关键词',
    'cate_id' => 123,
    'status' => DBCont::NORMAL_STATUS,
], 1, 20, 'id desc');
```

### count() - 统计总数

```php
public static function count(array $map = []): int
```

**示例**:
```php
$total = ResourceModelHelper::count(['status' => 1]);
```

### getByUqId() - 通过唯一ID获取

```php
public static function getByUqId($uq_id)
```

**参数**:
- `$uq_id` - 统一ID，格式为 `{type}_{id}`
  - `resource_123` → ResourceContent 记录
  - `basics_456` → BasicsContent 记录

**返回**: 单条记录，包含 `type`, `show_type`, `uq_id` 字段

**示例**:
```php
$record = ResourceModelHelper::getByUqId('resource_123');
if ($record) {
    echo $record['type'];      // 'ResourceContent'
    echo $record['show_type']; // 显示类型
    echo $record['uq_id'];     // 'resource_123'
}
```

### parseResourceMap() - 构建查询条件

```php
public static function parseResourceMap(array $get_data = [], array &$map = []): void
```

**支持的查询参数**:

| 参数 | 说明 | 示例 |
|------|------|------|
| `keyword` | 标题模糊搜索 | `'测试'` |
| `cate_id` | 分类ID筛选 | `123` |
| `tag_id` | 标签ID筛选 | `456` |
| `is_free` | 是否免费 | `0/1` |
| `is_guest_viewable` | 是否游客可见 | `0/1` |
| `show_type` | 显示类型 | `1/2/3` |
| `start_date` / `end_date` | 日期范围 | `'2024-01-01'` |
| `ids` | ID列表 | `'1,2,3'` |

**示例**:
```php
$map = [];
ResourceModelHelper::parseResourceMap(I('get.'), $map);
$list = ResourceModelHelper::getList($map);
```

### formatUrlToQdrant() - 格式化URL给向量数据库

```php
public static function formatUrlToQdrant(array &$data): array
```

**返回**: `[type, url]` 其中 type 为 `'html'` 或 `'pdf'`

### formatContentToQdrant() - 格式化内容给向量数据库

```php
public static function formatContentToQdrant(array &$data): string
```

**返回**: 处理后的 HTML 内容

## 完整使用示例

### 控制器中列表查询

```php
public function index()
{
    $get_data = I('get.');

    // 构建查询条件
    $map = [];
    ResourceModelHelper::parseResourceMap($get_data, $map);

    // 添加额外条件
    $map['status'] = DBCont::NORMAL_STATUS;

    // 分页查询
    $page = I('get.page', 1);
    $per_page = 20;
    $list = ResourceModelHelper::getList($map, $page, $per_page, 'id desc');

    // 统计总数
    $total = ResourceModelHelper::count($map);

    $this->assign('list', $list);
    $this->assign('total', $total);
    $this->display();
}
```

### 通过统一ID获取记录

```php
public function detail()
{
    $uq_id = I('get.id');  // 如 'resource_123' 或 'basics_456'

    $record = ResourceModelHelper::getByUqId($uq_id);
    if (!$record) {
        $this->error('记录不存在');
    }

    // 根据类型加载完整数据
    if ($record['type'] === 'ResourceContent') {
        $detail = D('ResourceContent')->find($record['id']);
    } else {
        $detail = D('BasicsContent')->find($record['id']);
    }

    $this->assign('detail', $detail);
    $this->display();
}
```

## 内部实现

### UNION ALL 查询

```sql
SELECT
    'ResourceContent' as type,
    show_type,
    CONCAT('resource_', id) as uq_id,
    id, title, status, ...
FROM qs_resource_content
WHERE ...

UNION ALL

SELECT
    'BasicsContent' as type,
    show_type,
    CONCAT('basics_', id) as uq_id,
    id, title, status, ...
FROM qs_basics_content
WHERE ...

ORDER BY id DESC
LIMIT 0, 20
```

## 注意事项

1. **性能**: UNION ALL 查询在大数据量时可能较慢，建议添加索引
2. **分页**: 使用 LIMIT 分页，注意深度分页性能问题
3. **类型判断**: 返回结果中的 `type` 字段用于区分内容来源
4. **ID唯一性**: 使用 `uq_id` 作为跨表的唯一标识符
