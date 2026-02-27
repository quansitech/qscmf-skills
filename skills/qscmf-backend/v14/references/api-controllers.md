# API Controllers Reference

Complete guide for building RESTful API controllers in QSCMF v14.

## Base Class

```php
use Api\Controller\RestController;
use QscmfApiCommon\Cache\Response;

class ProductController extends RestController
{
    protected $modelName = 'Product';

    // 不需要认证的端点
    protected $noAuthorization = ['gets'];
}
```

## $noAuthorization 属性

用于指定不需要登录认证的公开端点：

```php
class LoginController extends RestController
{
    protected $noAuthorization = [
        'create',  // POST /api/login
        'gets',    // GET /api/login
    ];
}
```

**注意**:
- 数组值是方法名（不带 HTTP 后缀）
- `gets` → GET 请求
- `create` → POST 请求
- `update` → PUT 请求
- `delete` → DELETE 请求
- 其他方法默认需要认证

## Standard Methods

| 方法 | HTTP | 路径 | 说明 |
|------|------|------|------|
| `gets()` | GET | /api/xxx | 列表/详情查询 |
| `create()` | POST | /api/xxx | 创建记录 |
| `update()` | PUT | /api/xxx | 更新记录 |
| `delete()` | DELETE | /api/xxx | 删除记录 |

```php
// GET /api/product
public function gets(): Response
{
    $list = D($this->modelName)->select();
    return new Response('成功', 1, $list);
}

// POST /api/product
public function create(): Response
{
    if (!IS_POST) {
        return new Response('请求方法错误', 0);
    }
    $data = I('post.');
    $id = D($this->modelName)->add($data);
    return new Response('创建成功', 1, ['id' => $id]);
}

// PUT /api/product
public function update(): Response
{
    if (!IS_PUT) {
        return new Response('请求方法错误', 0);
    }
    $data = I('put.');
    D($this->modelName)->save($data);
    return new Response('更新成功', 1);
}

// DELETE /api/product
public function delete(): Response
{
    if (!IS_DELETE) {
        return new Response('请求方法错误', 0);
    }
    $id = I('get.id', 0, 'intval');
    D($this->modelName)->delete($id);
    return new Response('删除成功', 1);
}
```

## Response Format

```php
// 使用 Response 对象（推荐）
return new Response('成功', 1, $data);
return new Response('错误信息', 0);

// 使用 response() 方法
$this->response('成功', 1, $data);
$this->response('错误信息', 0, null, 404);
```

---

## Related Documentation
- [API Response Format](../rules/api/api-response-format.md)
- [API Pagination](../rules/api/api-pagination-cursor.md)
