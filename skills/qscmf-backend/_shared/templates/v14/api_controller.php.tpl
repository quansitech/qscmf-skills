<?php
namespace Api\Controller;
use Qscmf\Api\RestController;
use QscmfApiCommon\Cache\Response;

/**
 * {{MODEL_TITLE}} API Controller
 */
class {{MODEL}}Controller extends RestController
{
    protected $modelName = '{{MODEL_NAME}}';

    // endpoints that don't require authentication
    protected $noAuthorization = ['gets', 'detail'];

    /**
     * Get list with pagination
     *
     * GET /api.php/{{MODEL}}/gets
     * Query: page, limit, keyword, status
     */
    public function gets(): Response
    {
        $get_data = I('get.');

        $page = (int)($get_data['page'] ?? 1);
        $limit = (int)($get_data['limit'] ?? 10);
        $keyword = $get_data['keyword'] ?? '';
        $status = $get_data['status'] ?? '';

        // Build query
        $where = [];
        if ($keyword) {
            $where['{{SEARCH_FIELD}}'] = ['like', '%' . $keyword . '%'];
        }
        if ($status !== '') {
            $where['status'] = $status;
        }

        // Get total count
        $total = D('{{MODEL_NAME}}')->where($where)->count();

        // Get list
        $list = D('{{MODEL_NAME}}')
            ->where($where)
            ->page($page, $limit)
            ->order('id desc')
            ->select();

        // Format data
        $data = $this->formatList($list);

        return new Response('成功', 1, [
            'list' => $data,
            'total' => $total,
            'page' => $page,
            'limit' => $limit
        ]);
    }

    /**
     * Get detail by ID
     *
     * GET /api.php/{{MODEL}}/detail
     * Query: id
     */
    public function detail(): Response
    {
        $id = I('get.id', 0, 'intval');

        if (!$id) {
            return new Response('参数错误', 0);
        }

        $data = D('{{MODEL_NAME}}')->find($id);

        if (!$data) {
            return new Response('记录不存在', 0);
        }

        $data = $this->formatDetail($data);

        return new Response('成功', 1, $data);
    }

    /**
     * Create new record
     *
     * POST /api.php/{{MODEL}}/save
     */
    public function save(): Response
    {
        if (!IS_POST) {
            return new Response('请求方法错误', 0);
        }

        $data = I('post.');

        // TODO: Add validation
        // TODO: Add business logic

        $id = D('{{MODEL_NAME}}')->add($data);

        if ($id) {
            return new Response('创建成功', 1, ['id' => $id]);
        }

        return new Response('创建失败', 0);
    }

    /**
     * Update record
     *
     * PUT /api.php/{{MODEL}}/update
     */
    public function update(): Response
    {
        if (!IS_PUT) {
            return new Response('请求方法错误', 0);
        }

        $data = I('put.');
        $id = $data['id'] ?? 0;

        if (!$id) {
            return new Response('参数错误', 0);
        }

        // TODO: Add validation
        // TODO: Add business logic

        $result = D('{{MODEL_NAME}}')->where(['id' => $id])->save($data);

        if ($result !== false) {
            return new Response('更新成功', 1);
        }

        return new Response('更新失败', 0);
    }

    /**
     * Delete record
     *
     * DELETE /api.php/{{MODEL}}/delete
     */
    public function delete(): Response
    {
        if (!IS_DELETE) {
            return new Response('请求方法错误', 0);
        }

        $id = I('get.id', 0, 'intval');

        if (!$id) {
            return new Response('参数错误', 0);
        }

        // TODO: Add business logic (e.g., check dependencies)

        $result = D('{{MODEL_NAME}}')->delete($id);

        if ($result) {
            return new Response('删除成功', 1);
        }

        return new Response('删除失败', 0);
    }

    /**
     * Format list data
     */
    protected function formatList(array $list): array
    {
{{DATA_FORMAT}}
    }

    /**
     * Format detail data
     */
    protected function formatDetail(array $data): array
    {
        // TODO: Add custom formatting
        return $data;
    }
}
