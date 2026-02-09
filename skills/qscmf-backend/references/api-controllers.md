# API Controllers Reference

> QSCMF RESTful API 开发指南
>
> 基础文档：`app/Api/Controller/` 目录

## Base Class

继承 `RestController`：

```php
<?php
namespace Api\Controller;
use Qscmf\Api\RestController;
use QscmfApiCommon\Cache\Response;

class DemoController extends RestController
{
    protected $modelName = 'Demo';

    // 不需要认证的端点
    protected $noAuthorization = ['gets', 'detail'];
}
```

## Standard Endpoints

### GET List

```php
public function gets(): Response
{
    $get_data = I('get.');
    $page = (int)($get_data['page'] ?? 1);
    $limit = (int)($get_data['limit'] ?? 10);

    $where = $this->buildWhere($get_data);
    $total = D('Demo')->where($where)->count();
    $list = D('Demo')->where($where)->page($page, $limit)->select();

    $data = $this->formatList($list);

    return new Response('成功', 1, [
        'list' => $data,
        'total' => $total,
        'page' => $page,
        'limit' => $limit
    ]);
}
```

### GET Detail

```php
public function detail(): Response
{
    $id = I('get.id', 0, 'intval');

    $data = D('Demo')->find($id);
    if (!$data) {
        return new Response('记录不存在', 0);
    }

    $data = $this->formatDetail($data);

    return new Response('成功', 1, $data);
}
```

### POST Create

```php
public function save(): Response
{
    if (!IS_POST) {
        return new Response('请求方法错误', 0);
    }

    $data = I('post.');
    $id = D('Demo')->add($data);

    return new Response('创建成功', 1, ['id' => $id]);
}
```

### PUT Update

```php
public function update(): Response
{
    if (!IS_PUT) {
        return new Response('请求方法错误', 0);
    }

    $data = I('put.');
    $result = D('Demo')->where(['id' => $data['id']])->save($data);

    return $result !== false
        ? new Response('更新成功', 1)
        : new Response('更新失败', 0);
}
```

### DELETE Delete

```php
public function delete(): Response
{
    if (!IS_DELETE) {
        return new Response('请求方法错误', 0);
    }

    $id = I('get.id', 0, 'intval');
    $result = D('Demo')->delete($id);

    return $result
        ? new Response('删除成功', 1)
        : new Response('删除失败', 0);
}
```

## Response Format

```php
// Success
return new Response('成功', 1, $data);

// Error
return new Response('错误信息', 0);
```

## Data Formatting

```php
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
    $data['tags'] = explode(',', $data['tags']);
    return $data;
}
```

## Pagination & Filtering

```php
protected function buildWhere(array $params): array
{
    $where = [];

    if (!empty($params['keyword'])) {
        $where['title'] = ['like', '%' . $params['keyword'] . '%'];
    }

    if (isset($params['status']) && $params['status'] !== '') {
        $where['status'] = $params['status'];
    }

    if (!empty($params['cate_id'])) {
        $where['cate_id'] = $params['cate_id'];
    }

    return $where;
}
```

---

**更多示例**：
- `app/Api/Controller/ProductController.class.php`
- `app/Api/Controller/ArticleController.class.php`
