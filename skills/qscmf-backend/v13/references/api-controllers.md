# API Controllers Reference

> QSCMF v13 RESTful API 开发指南

## 概述

QSCMF v13 API 控制器使用 `RestController` 作为基础类，提供统一的响应格式和认证机制。

## 版本特性

| 特性 | v13 |
|------|-----|
| PHP 版本 | >= 8.1 |
| PHPUnit | ^9.3.0 |
| 响应类 | `QscmfApiCommon\Cache\Response` |

## 标准模式

### 基本结构

```php
<?php
namespace Api\Controller;

use Qscmf\Api\RestController;
use QscmfApiCommon\Cache\Response;

class XxxController extends RestController
{
    protected $modelName = 'Xxx';

    // 不需要认证的端点
    protected $noAuthorization = ['gets', 'detail'];
}
```

### 核心属性

| 属性 | 类型 | 说明 |
|------|------|------|
| `$modelName` | string | 关联的模型名称（如 'Demo', 'User'） |
| `$noAuthorization` | array | 不需要认证的端点列表 |

### 核心方法

| 方法 | 说明 | HTTP 方法 | 路径 |
|------|------|-----------|------|
| `gets()` | 列表/详情查询 | GET | /api/xxx |
| `create()` | 创建记录 | POST | /api/xxx |
| `update()` | 更新记录 | PUT | /api/xxx |
| `delete()` | 删除记录 | DELETE | /api/xxx |

## 标准端点实现

### GET 列表/详情查询

```php
public function gets(): Response
{
    $get_data = I('get.');
    $page = (int)($get_data['page'] ?? 1);
    $limit = (int)($get_data['limit'] ?? 10);

    $where = $this->buildWhere($get_data);
    $total = D($this->modelName)->where($where)->count();
    $list = D($this->modelName)->where($where)->page($page, $limit)->select();

    $data = $this->formatList($list);

    return new Response('成功', 1, [
        'list' => $data,
        'total' => $total,
        'page' => $page,
        'limit' => $limit
    ]);
}
```

### POST 创建记录

```php
public function create(): Response
{
    if (!IS_POST) {
        return new Response('请求方法错误', 0);
    }

    $data = I('post.');
    $id = D($this->modelName)->add($data);

    return new Response('创建成功', 1, ['id' => $id]);
}
```

### PUT 更新记录

```php
public function update(): Response
{
    if (!IS_PUT) {
        return new Response('请求方法错误', 0);
    }

    $data = I('put.');
    $result = D($this->modelName)->where(['id' => $data['id']])->save($data);

    return $result !== false
        ? new Response('更新成功', 1)
        : new Response('更新失败', 0);
}
```

### DELETE 删除记录

```php
public function delete(): Response
{
    if (!IS_DELETE) {
        return new Response('请求方法错误', 0);
    }

    $id = I('get.id', 0, 'intval');
    $result = D($this->modelName)->delete($id);

    return $result
        ? new Response('删除成功', 1)
        : new Response('删除失败', 0);
}
```

## 响应格式

### 标准响应

```php
// 成功响应
return new Response('成功', 1, $data);

// 错误响应
return new Response('错误信息', 0);
```

### 响应结构

```json
{
    "msg": "操作成功",
    "status": 1,
    "data": { }
}
```

## 数据格式化

### 列表数据格式化

```php
protected function formatList(array $list): array
{
    foreach ($list as &$item) {
        // 图片 URL 处理
        $item['cover_url'] = get_image_url($item['cover']);

        // 状态文本转换
        $item['status_text'] = DBCont::getStatusList()[$item['status']] ?? '';

        // 时间格式化
        $item['create_time_text'] = date('Y-m-d H:i', $item['create_time']);
    }
    return $list;
}
```

### 详情数据格式化

```php
protected function formatDetail(array $data): array
{
    // 标签数组转换
    $data['tags'] = explode(',', $data['tags']);

    // 关联数据加载
    $data['category'] = D('Category')->find($data['cate_id']);

    // 图片处理
    $data['images'] = array_map(function($img) {
        return get_image_url($img);
    }, explode(',', $data['images']));

    return $data;
}
```

## 查询条件构建

### 基础过滤

```php
protected function buildWhere(array $params): array
{
    $where = [];

    // 关键词搜索
    if (!empty($params['keyword'])) {
        $where['title'] = ['like', '%' . $params['keyword'] . '%'];
    }

    // 状态过滤（支持 0 值）
    if (isset($params['status']) && $params['status'] !== '') {
        $where['status'] = $params['status'];
    }

    // 分类过滤
    if (!empty($params['cate_id'])) {
        $where['cate_id'] = $params['cate_id'];
    }

    // 时间范围
    if (!empty($params['start_time'])) {
        $where['create_time'][] = ['egt', strtotime($params['start_time'])];
    }
    if (!empty($params['end_time'])) {
        $where['create_time'][] = ['elt', strtotime($params['end_time'])];
    }

    return $where;
}
```

### 复杂查询

```php
protected function buildWhere(array $params): array
{
    $where = [];

    // 多字段搜索
    if (!empty($params['keyword'])) {
        $where['_complex'] = [
            '_logic' => 'or',
            'title' => ['like', '%' . $params['keyword'] . '%'],
            'summary' => ['like', '%' . $params['keyword'] . '%'],
        ];
    }

    // 多选过滤
    if (!empty($params['tags'])) {
        $tags = explode(',', $params['tags']);
        $where['tags'] = ['in', $tags];
    }

    // 排序
    $order = $params['order'] ?? 'id desc';

    return ['where' => $where, 'order' => $order];
}
```

## 完整示例

### RESTful CRUD 控制器

```php
<?php
namespace Api\Controller;

use Qscmf\Api\RestController;
use QscmfApiCommon\Cache\Response;
use Gy_Library\DBCont;

class ProductController extends RestController
{
    protected $modelName = 'Product';

    // 公开端点
    protected $noAuthorization = ['gets'];

    public function gets(): Response
    {
        $get_data = I('get.');

        // 如果有 id 参数，返回详情
        if (!empty($get_data['id'])) {
            $data = D($this->modelName)->find($get_data['id']);
            if (!$data) {
                return new Response('记录不存在', 0);
            }
            return new Response('成功', 1, $this->formatDetail($data));
        }

        // 否则返回列表
        $page = (int)($get_data['page'] ?? 1);
        $limit = (int)($get_data['limit'] ?? 10);

        $where = $this->buildWhere($get_data);
        $total = D($this->modelName)->where($where)->count();
        $list = D($this->modelName)
            ->where($where)
            ->page($page, $limit)
            ->order('id desc')
            ->select();

        $data = $this->formatList($list);

        return new Response('成功', 1, [
            'list' => $data,
            'total' => $total,
            'page' => $page,
            'limit' => $limit
        ]);
    }

    public function create(): Response
    {
        if (!IS_POST) {
            return new Response('请求方法错误', 0);
        }

        $data = I('post.');

        // 数据验证
        if (empty($data['product_name'])) {
            return new Response('产品名称不能为空', 0);
        }

        $data['create_time'] = time();
        $data['status'] = DBCont::NORMAL_STATUS;

        $id = D($this->modelName)->add($data);

        return $id
            ? new Response('创建成功', 1, ['id' => $id])
            : new Response('创建失败', 0);
    }

    public function update(): Response
    {
        if (!IS_PUT) {
            return new Response('请求方法错误', 0);
        }

        $data = I('put.');

        if (empty($data['id'])) {
            return new Response('记录 ID 不能为空', 0);
        }

        $data['update_time'] = time();
        $result = D($this->modelName)->where(['id' => $data['id']])->save($data);

        return $result !== false
            ? new Response('更新成功', 1)
            : new Response('更新失败', 0);
    }

    public function delete(): Response
    {
        if (!IS_DELETE) {
            return new Response('请求方法错误', 0);
        }

        $id = I('get.id', 0, 'intval');

        if (!$id) {
            return new Response('记录 ID 不能为空', 0);
        }

        $result = D($this->modelName)->delete($id);

        return $result
            ? new Response('删除成功', 1)
            : new Response('删除失败', 0);
    }

    protected function buildWhere(array $params): array
    {
        $where = [];

        if (!empty($params['keyword'])) {
            $where['product_name'] = ['like', '%' . $params['keyword'] . '%'];
        }

        if (isset($params['status']) && $params['status'] !== '') {
            $where['status'] = $params['status'];
        }

        if (!empty($params['cate_id'])) {
            $where['cate_id'] = $params['cate_id'];
        }

        return $where;
    }

    protected function formatList(array $list): array
    {
        foreach ($list as &$item) {
            $item['cover_url'] = get_image_url($item['cover']);
            $item['status_text'] = DBCont::getStatusList()[$item['status']] ?? '';
        }
        return $list;
    }

    protected function formatDetail(array $data): array
    {
        $data['tags'] = array_filter(explode(',', $data['tags']));
        $data['cover_url'] = get_image_url($data['cover']);
        return $data;
    }
}
```

## 扩展功能

### 自定义端点

```php
// 批量操作
public function batchAction(): Response
{
    if (!IS_POST) {
        return new Response('请求方法错误', 0);
    }

    $ids = I('post.ids');
    $action = I('post.action');

    if (!$ids || !$action) {
        return new Response('参数错误', 0);
    }

    switch ($action) {
        case 'enable':
            $result = D($this->modelName)
                ->where(['id' => ['in', $ids]])
                ->save(['status' => DBCont::NORMAL_STATUS]);
            break;
        case 'disable':
            $result = D($this->modelName)
                ->where(['id' => ['in', $ids]])
                ->save(['status' => DBCont::DISABLE_STATUS]);
            break;
        default:
            return new Response('未知操作', 0);
    }

    return $result !== false
        ? new Response('操作成功', 1)
        : new Response('操作失败', 0);
}

// 统计数据
public function statistics(): Response
{
    $stats = [
        'total' => D($this->modelName)->count(),
        'enabled' => D($this->modelName)->where(['status' => DBCont::NORMAL_STATUS])->count(),
        'disabled' => D($this->modelName)->where(['status' => DBCont::DISABLE_STATUS])->count(),
    ];

    return new Response('成功', 1, $stats);
}
```

### 认证与授权

```php
// 检查用户权限
protected function checkPermission(string $action): bool
{
    $user_id = $this->getUserId();

    if (!$user_id) {
        return false;
    }

    // 管理员跳过检查
    if ($this->isAdmin($user_id)) {
        return true;
    }

    // 自定义权限逻辑
    return $this->checkUserPermission($user_id, $action);
}

// 获取当前用户 ID
protected function getUserId(): int
{
    $token = I('server.HTTP_AUTHORIZATION');
    return $this->parseToken($token);
}
```

### 缓存集成

```php
use Qscmf\Lib\Cache\QscmfCache;

public function gets(): Response
{
    $cache_key = 'xxx_list_' . md5(json_encode(I('get.')));

    // 尝试从缓存读取
    $cache = new QscmfCache($cache_key, 300);
    $cached = $cache->get();
    if ($cached) {
        return new Response('成功', 1, $cached);
    }

    // 原始查询逻辑
    $get_data = I('get.');
    // ... 查询代码 ...

    $result = [
        'list' => $data,
        'total' => $total,
        'page' => $page,
        'limit' => $limit
    ];

    // 缓存结果
    $cache->set($result);

    return new Response('成功', 1, $result);
}
```

### 文件上传

```php
// 图片上传端点
public function upload(): Response
{
    if (!IS_POST) {
        return new Response('请求方法错误', 0);
    }

    $file = $_FILES['file'];
    if (!$file) {
        return new Response('请选择文件', 0);
    }

    // 验证文件类型
    $allowed_types = ['image/jpeg', 'image/png', 'image/gif'];
    if (!in_array($file['type'], $allowed_types)) {
        return new Response('不支持的文件类型', 0);
    }

    // 上传到对象存储
    $upload_result = $this->uploadToStorage($file);

    if (!$upload_result['success']) {
        return new Response('上传失败', 0);
    }

    return new Response('上传成功', 1, [
        'url' => $upload_result['url'],
        'path' => $upload_result['path']
    ]);
}
```

## 最佳实践

### 1. 使用 DBCont 常量

```php
use Gy_Library\DBCont;

DBCont::NORMAL_STATUS    // = 1 (启用)
DBCont::DISABLE_STATUS   // = 0 (禁用)
DBCont::AUDIT_STATUS     // = 2 (待审核)

DBCont::getStatusList()  // [1 => '启用', 0 => '禁用']
```

### 2. 参数验证

```php
public function create(): Response
{
    $data = I('post.');

    // 必填字段验证
    $required = ['title', 'cate_id'];
    foreach ($required as $field) {
        if (empty($data[$field])) {
            return new Response("字段 {$field} 不能为空", 0);
        }
    }

    // 数据类型验证
    if (!is_numeric($data['cate_id'])) {
        return new Response('分类 ID 必须是数字', 0);
    }

    // 业务逻辑验证
    if (D($this->modelName)->where(['title' => $data['title']])->count()) {
        return new Response('标题已存在', 0);
    }

    // ... 处理逻辑
}
```

### 3. 分页参数规范

```php
// 默认分页参数
$page = (int)($get_data['page'] ?? 1);
$limit = (int)($get_data['limit'] ?? 10);
$limit = min($limit, 100); // 限制最大每页数量

// 分页计算
$total = D($this->modelName)->where($where)->count();
$total_pages = ceil($total / $limit);
```

### 4. 错误处理

```php
// 使用 try-catch 捕获异常
public function create(): Response
{
    try {
        $data = I('post.');
        $id = D($this->modelName)->add($data);

        if (!$id) {
            return new Response('保存失败', 0);
        }

        return new Response('成功', 1, ['id' => $id]);
    } catch (\Exception $e) {
        // 记录日志
        \Think\Log::record('API Error: ' . $e->getMessage());

        return new Response('系统错误', 0);
    }
}
```

### 5. API 版本控制

```php
// 通过 URL 路径控制版本
// /v1/xxx/gets
// /v2/xxx/gets

namespace Api\Controller\V1;

class XxxController extends \Qscmf\Api\RestController
{
    // V1 版本实现
}

namespace Api\Controller\V2;

class XxxController extends \Qscmf\Api\RestController
{
    // V2 版本实现（改进的字段、逻辑等）
}
```

## 相关文档

- [Admin Controllers](admin-controllers.md) - 后台管理控制器
- [Migration Guide](migration-guide.md) - 数据库迁移指南
- [Abstract Base Patterns](abstract-base-patterns.md) - 抽象基类模式
- [Development Standards](development-standards.md) - 开发规范
