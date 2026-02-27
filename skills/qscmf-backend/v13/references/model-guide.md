# Model Guide

> QSCMF v13 模型开发指南 - GyListModel 实战指南

## 版本特性

| 特性 | v13 |
|------|-----|
| PHP 版本 | >= 8.1 |
| 类型系统 | 支持类型声明 |
| 返回值 | 严格类型 |

## 基础结构

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
        ['title', 'require', '标题不能为空', self::MUST_VALIDATE, '', self::MODEL_BOTH],
    ];

    // 自动完成
    protected $_auto = [
        ['create_time', 'time', self::MODEL_INSERT, 'function'],
    ];
}
```

## 类型声明

### 方法声明规范

```php
// ✅ 完整类型声明
public function getXxxCount(array $map = []): int
public function getXxxList(array $map = [], ?int $page = 1, ?int $per_page = 20): array
public function getXxxDetail(int $id): ?array
public function saveXxx(array $data): bool
public function deleteXxx(int $id): bool
public function formatList(array &$list): void

// ❌ 避免缺少类型
public function getXxxList($map, $page, $per_page)  // 缺少类型声明
```

### 返回值规范

```php
// 单条记录
public function getXxxDetail(int $id): ?array
{
    return $this->where(['id' => $id])->find();
}

// 列表（总是返回数组，即使为空）
public function getXxxList(array $map = []): array
{
    return (array)$this->where($map)->select();
}

// 数量
public function getXxxCount(array $map = []): int
{
    return (int)$this->where($map)->count();
}

// ID
public function addXxx(array $data): int
{
    $id = $this->add($data);
    return $id ?: 0;
}

// 布尔结果
public function checkExists(int $id): bool
{
    return $this->where(['id' => $id])->count() > 0;
}
```

## 验证规则

### 基础验证

```php
protected $_validate = [
    // 必填
    ['title', 'require', '标题不能为空', self::MUST_VALIDATE, '', self::MODEL_BOTH],

    // 长度验证
    ['title', '1,255', '长度1-255', self::EXISTS_VALIDATE, 'length'],

    // 唯一验证
    ['email', '', '邮箱已存在', self::MUST_VALIDATE, 'unique'],

    // 数字验证
    ['sort', 'number', '排序必须是数字', self::EXISTS_VALIDATE],

    // 正则验证
    ['mobile', '/^1[3-9]\d{9}$/', '手机号格式错误', self::EXISTS_VALIDATE, 'regex'],

    // 范围验证
    ['status', '0,1,2', '状态值错误', self::EXISTS_VALIDATE, 'in'],
];
```

### 回调验证

```php
protected $_validate = [
    // 条件验证（多字段依赖）
    ['cate_id,url,content', 'checkRequiredByCate', '内容不能为空', self::MUST_VALIDATE, 'callback'],
];

/**
 * 根据分类类型验证必填字段
 */
public function checkRequiredByCate(array $data): bool
{
    $cate_show_type = D('Cate')->where(['id' => $data['cate_id']])->getField('show_type');

    return match($cate_show_type) {
        'article' => !empty($data['content']),
        'video' => !empty($data['url']) || !empty($data['video_id']),
        'image' => !empty($data['images']),
        default => false
    };
}
```

### 验证时机常量

| 常量 | 值 | 说明 |
|------|-----|------|
| `MUST_VALIDATE` | 1 | 必须验证 |
| `EXISTS_VALIDATE` | 0 | 表单存在字段时验证 |
| `VALUE_VALIDATE` | 2 | 表单值不为空时验证 |

### 验证场景常量

| 常量 | 值 | 说明 |
|------|-----|------|
| `MODEL_INSERT` | 1 | 新增时验证 |
| `MODEL_UPDATE` | 2 | 更新时验证 |
| `MODEL_BOTH` | 3 | 全部场景验证 |

## 自动完成

```php
protected $_auto = [
    // 使用函数
    ['create_time', 'time', self::MODEL_INSERT, 'function'],
    ['update_time', 'time', self::MODEL_BOTH, 'function'],

    // 使用回调方法
    ['password', 'encryptPassword', self::MODEL_INSERT, 'callback'],

    // 使用字段填充
    ['status', '1', self::MODEL_INSERT],
];

/**
 * 密码加密回调
 */
protected function encryptPassword(string $password): string
{
    return password_hash($password, PASSWORD_DEFAULT);
}
```

## 查询方法封装

### 标准查询模式

```php
/**
 * 解析搜索参数
 */
public function parseXxxMap(array $get_data = [], array &$map = []): void
{
    if (isset($get_data['cate_id']) && !qsEmpty($get_data['cate_id'])) {
        $map['cate_id'] = $get_data['cate_id'];
    }

    if (isset($get_data['status']) && !qsEmpty($get_data['status'])) {
        $map['status'] = $get_data['status'];
    }

    if (isset($get_data['keyword']) && !qsEmpty($get_data['keyword'])) {
        $map['title'] = ['like', '%' . $get_data['keyword'] . '%'];
    }

    if (isset($get_data['start_time']) && !qsEmpty($get_data['start_time'])) {
        $map['create_time'][] = ['egt', strtotime($get_data['start_time'])];
    }

    if (isset($get_data['end_time']) && !qsEmpty($get_data['end_time'])) {
        $map['create_time'][] = ['elt', strtotime($get_data['end_time'])];
    }
}

/**
 * 获取数量
 */
public function getXxxCount(array $map = []): int
{
    return (int)$this->where($map)->count();
}

/**
 * 获取列表
 */
public function getXxxList(array $map = [], ?int $page = null, ?int $per_page = 20): array
{
    $model = $this->where($map);

    if (!is_null($page)) {
        $model->page($page, $per_page);
    }

    return (array)$model->order('sort asc, id desc')->select();
}

/**
 * 获取详情
 */
public function getXxxDetail(int $id): ?array
{
    $data = $this->where(['id' => $id])->find();
    return $data ?: null;
}
```

## 性能优化

### 避免 N+1 查询

```php
// ❌ 错误 - N+1 问题
foreach ($list as &$item) {
    $item['cate'] = D('Cate')->find($item['cate_id']);
}

// ✅ 正确 - 批量查询
$cate_ids = array_column($list, 'cate_id');
$cate_ids = array_filter(array_unique($cate_ids));

if (!empty($cate_ids)) {
    $cate_list = D('Cate')
        ->where(['id' => ['IN', $cate_ids]])
        ->getField('id,name', true);

    foreach ($list as &$item) {
        $item['cate_name'] = $cate_list[$item['cate_id']]['name'] ?? '';
    }
}
```

### 缓存优化

```php
use Qscmf\Lib\Cache\QscmfCache;

/**
 * 获取配置数据（带缓存）
 */
public function getConfig(): array
{
    return $this->cache(true, 86400)->getField('id,title', true);
}

/**
 * 获取分类列表（带缓存）
 */
public function getCateList(): array
{
    $cache = new QscmfCache('cate_list', 3600, 'cate_tag');
    return $cache->remember(function() {
        return $this->where(['status' => DBCont::NORMAL_STATUS])
            ->getField('id,name', true);
    });
}
```

### 字段选择优化

```php
// ✅ 只查询需要的字段
public function getXxxList(array $map = []): array
{
    return (array)$this->where($map)
        ->field('id,title,cover,status')
        ->select();
}

// ✅ 关联查询只获取必要字段
$cate_list = D('Cate')->getField('id,name', true);  // 只获取 id, name
```

## 事务处理

```php
/**
 * 添加数据（带事务）
 */
public function addXxx(array $data): int
{
    $this->startTrans();
    try {
        $id = $this->createAdd($data);
        if ($id === false) {
            E($this->getError());
        }

        // 关联操作
        if (isset($data['tags'])) {
            D('XxxTag')->addXxxTags($id, $data['tags']);
        }

        $this->commit();
        return $id;
    } catch (\Exception $e) {
        $this->rollback();
        $this->error = $e->getMessage();
        return 0;
    }
}

/**
 * 更新数据（带事务）
 */
public function updateXxx(int $id, array $data): bool
{
    $this->startTrans();
    try {
        $result = $this->where(['id' => $id])->save($data);
        if ($result === false) {
            E($this->getError());
        }

        // 清除缓存
        $cache = new QscmfCache('xxx_detail_' . $id);
        $cache->clear();

        $this->commit();
        return true;
    } catch (\Exception $e) {
        $this->rollback();
        $this->error = $e->getMessage();
        return false;
    }
}
```

## 状态变更

```php
use Gy_Library\DBCont;

/**
 * 禁用
 */
public function forbid($ids): array
{
    return $this->changeStatus($ids, DBCont::NORMAL_STATUS, DBCont::FORBIDDEN_STATUS);
}

/**
 * 启用
 */
public function resume($ids): array
{
    return $this->changeStatus($ids, DBCont::FORBIDDEN_STATUS, DBCont::NORMAL_STATUS);
}

/**
 * 通用状态变更
 */
private function changeStatus($ids, int $from, int $to): array
{
    $id_array = is_array($ids) ? $ids : explode(',', $ids);
    $id_array = array_filter($id_array);

    // 只变更符合源状态的记录
    $need_change_ids = $this->where([
        'id' => ['IN', $id_array],
        'status' => $from
    ])->getField('id', true);

    if (empty($need_change_ids)) {
        return [];
    }

    $this->where(['id' => ['IN', $need_change_ids]])->setField('status', $to);
    return $need_change_ids;
}
```

## 数据格式化

```php
/**
 * 格式化列表数据
 */
public function formatList(array &$list): void
{
    if (empty($list)) {
        return;
    }

    // 批量获取关联数据
    $cate_ids = array_column($list, 'cate_id');
    $cate_list = D('Cate')->getField('id,name', true);

    // 格式化每条记录
    foreach ($list as &$item) {
        $item['cate_name'] = $cate_list[$item['cate_id']]['name'] ?? '';
        $item['status_text'] = DBCont::getStatusList()[$item['status']] ?? '';
        $item['cover_url'] = $item['cover'] ? get_image_url($item['cover']) : '';
        $item['create_time_text'] = date('Y-m-d H:i', $item['create_time']);
    }
}
```

## 删除验证

```php
class XxxModel extends GyListModel
{
    // 删除时验证关联
    protected $_delete_validate = [
        ['RelatedModel', 'foreign_key', parent::EXIST_VALIDATE, '该记录已有关联数据，无法删除'],
    ];
}
```

## 字段权限控制

```php
class BoxModel extends GyListModel
{
    // 字段权限配置
    protected $_auth_node_column = [
        'company_id' => ['auth_node' => 'admin.Box.allColumns'],
        'caption' => [
            'auth_node' => ['admin.Box.allColumns', 'admin.Box.add', 'admin.Box.edit'],
            'default' => 'quansitech'
        ]
    ];
}
```

## 完整示例

```php
<?php
namespace Common\Model;

use Gy_Library\GyListModel;
use Gy_Library\DBCont;
use Qscmf\Lib\Cache\QscmfCache;

class ProductModel extends GyListModel
{
    protected $tableName = 'qs_product';
    protected $pk = 'id';

    protected $_validate = [
        ['product_name', 'require', '产品名称不能为空', self::MUST_VALIDATE, '', self::MODEL_BOTH],
        ['product_name', '1,200', '长度1-200', self::EXISTS_VALIDATE, 'length'],
        ['price', 'require', '价格不能为空', self::MUST_VALIDATE],
        ['price', '/^\d+(\.\d{1,2})?$/', '价格格式错误', self::EXISTS_VALIDATE, 'regex'],
    ];

    protected $_auto = [
        ['create_time', 'time', self::MODEL_INSERT, 'function'],
        ['update_time', 'time', self::MODEL_BOTH, 'function'],
    ];

    public function parseProductMap(array $get_data = [], array &$map = []): void
    {
        if (isset($get_data['cate_id']) && !qsEmpty($get_data['cate_id'])) {
            $map['cate_id'] = $get_data['cate_id'];
        }
        if (isset($get_data['status']) && !qsEmpty($get_data['status'])) {
            $map['status'] = $get_data['status'];
        }
        if (isset($get_data['keyword']) && !qsEmpty($get_data['keyword'])) {
            $map['product_name'] = ['like', '%' . $get_data['keyword'] . '%'];
        }
    }

    public function getProductCount(array $map = []): int
    {
        return (int)$this->where($map)->count();
    }

    public function getProductList(array $map = [], ?int $page = null, ?int $per_page = 20): array
    {
        $model = $this->where($map);

        if (!is_null($page)) {
            $model->page($page, $per_page);
        }

        $list = (array)$model->order('sort asc, id desc')->select();
        $this->formatList($list);

        return $list;
    }

    public function getProductDetail(int $id): ?array
    {
        $cache = new QscmfCache('product_detail_' . $id, 3600);
        return $cache->remember(function() use ($id) {
            return $this->where(['id' => $id])->find();
        });
    }

    public function addProduct(array $data): int
    {
        $this->startTrans();
        try {
            $id = $this->createAdd($data);
            if ($id === false) {
                E($this->getError());
            }
            $this->commit();
            return $id;
        } catch (\Exception $e) {
            $this->rollback();
            $this->error = $e->getMessage();
            return 0;
        }
    }

    public function updateProduct(int $id, array $data): bool
    {
        $this->startTrans();
        try {
            $result = $this->where(['id' => $id])->save($data);
            if ($result === false) {
                E($this->getError());
            }

            // 清除缓存
            $cache = new QscmfCache('product_detail_' . $id);
            $cache->clear();

            $this->commit();
            return true;
        } catch (\Exception $e) {
            $this->rollback();
            $this->error = $e->getMessage();
            return false;
        }
    }

    public function formatList(array &$list): void
    {
        if (empty($list)) {
            return;
        }

        $cate_ids = array_column($list, 'cate_id');
        $cate_list = D('Cate')->getField('id,name', true);

        foreach ($list as &$item) {
            $item['cate_name'] = $cate_list[$item['cate_id']]['name'] ?? '';
            $item['status_text'] = DBCont::getStatusList()[$item['status']] ?? '';
            $item['cover_url'] = $item['cover'] ? get_image_url($item['cover']) : '';
        }
    }
}
```

## 相关文档

- [Migration Guide](migration-guide.md) - 迁移文件指南
- [Where Query Reference](where-query-reference.md) - 查询语法参考
- [Admin Controllers](admin-controllers.md) - 控制器中使用模型
- [Development Standards](development-standards.md) - PHP 8.1+ 编码规范
