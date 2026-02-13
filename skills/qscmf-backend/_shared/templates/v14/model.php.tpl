<?php
namespace Common\Model;

use Gy_Library\GyListModel;
use Gy_Library\DBCont;
use Qscmf\Lib\Cache\QscmfCache;

/**
 * {{MODEL_TITLE}} Model
 */
class {{MODEL_NAME}}Model extends GyListModel
{
    protected $tableName = '{{TABLE_NAME}}';
    protected $pk = 'id';

    /**
     * 验证规则
     */
    protected $_validate = [
{{VALIDATE_RULES}}
    ];

    /**
     * 自动完成
     */
    protected $_auto = [
        ['create_time', 'time', self::MODEL_INSERT, 'function'],
        ['update_time', 'time', self::MODEL_UPDATE, 'function'],
    ];

    /**
     * 解析查询条件
     */
    public function parse{{MODEL_NAME}}Map(array $get_data = [], array &$map = []): void
    {
        // 分类过滤
        if (isset($get_data['cate_id']) && !qsEmpty($get_data['cate_id'])) {
            $map['cate_id'] = $get_data['cate_id'];
        }

        // 状态过滤（支持 0 值）
        if (isset($get_data['status']) && $get_data['status'] !== '') {
            $map['status'] = $get_data['status'];
        }

        // 关键词搜索
        if (isset($get_data['keyword']) && !qsEmpty($get_data['keyword'])) {
            $map['title'] = ['like', '%' . $get_data['keyword'] . '%'];
        }

        // 时间范围
        if (isset($get_data['start_time']) && !qsEmpty($get_data['start_time'])) {
            $map['create_time'][] = ['egt', strtotime($get_data['start_time'])];
        }
        if (isset($get_data['end_time']) && !qsEmpty($get_data['end_time'])) {
            $map['create_time'][] = ['elt', strtotime($get_data['end_time'])];
        }
    }

    /**
     * 获取记录数量
     */
    public function get{{MODEL_NAME}}Count(array $map = []): int
    {
        return (int)$this->where($map)->count();
    }

    /**
     * 获取列表
     */
    public function get{{MODEL_NAME}}List(array $map = [], ?int $page = null, ?int $per_page = 20): array
    {
        $model = $this->where($map);

        if (!is_null($page)) {
            $model->page($page, $per_page);
        }

        $list = (array)$model->order('sort asc, id desc')->select();

        // 格式化列表数据
        $this->formatList($list);

        return $list;
    }

    /**
     * 获取详情
     */
    public function get{{MODEL_NAME}}Detail(int $id): ?array
    {
        $cache = new QscmfCache('{{TABLE_NAME_SNAKE}}_detail_' . $id, 3600);

        return $cache->remember(function() use ($id) {
            $data = $this->where(['id' => $id])->find();
            return $data ?: null;
        });
    }

    /**
     * 添加记录
     */
    public function add{{MODEL_NAME}}(array $data): int
    {
        $this->startTrans();
        try {
            $id = $this->createAdd($data);
            if ($id === false) {
                E($this->getError());
            }

            // TODO: 添加关联数据（标签、分类等）
            // if (isset($data['tags'])) {
            //     D('{{MODEL_NAME}}Tag')->add{{MODEL_NAME}}Tags($id, $data['tags']);
            // }

            $this->commit();
            return $id;
        } catch (\Exception $e) {
            $this->rollback();
            $this->error = $e->getMessage();
            return 0;
        }
    }

    /**
     * 更新记录
     */
    public function update{{MODEL_NAME}}(int $id, array $data): bool
    {
        $this->startTrans();
        try {
            $result = $this->where(['id' => $id])->save($data);
            if ($result === false) {
                E($this->getError());
            }

            // 清除详情缓存
            $cache = new QscmfCache('{{TABLE_NAME_SNAKE}}_detail_' . $id);
            $cache->clear();

            // 清除列表缓存
            QscmfCache::clearByTag('{{TABLE_NAME_SNAKE}}_list');

            $this->commit();
            return true;
        } catch (\Exception $e) {
            $this->rollback();
            $this->error = $e->getMessage();
            return false;
        }
    }

    /**
     * 删除记录
     */
    public function delete{{MODEL_NAME}}(int $id): bool
    {
        $this->startTrans();
        try {
            $result = $this->where(['id' => $id])->delete();
            if ($result === false) {
                E($this->getError());
            }

            // 清除缓存
            $cache = new QscmfCache('{{TABLE_NAME_SNAKE}}_detail_' . $id);
            $cache->clear();
            QscmfCache::clearByTag('{{TABLE_NAME_SNAKE}}_list');

            $this->commit();
            return true;
        } catch (\Exception $e) {
            $this->rollback();
            $this->error = $e->getMessage();
            return false;
        }
    }

    /**
     * 禁用记录
     */
    public function forbid($ids): array
    {
        return $this->changeStatus($ids, DBCont::NORMAL_STATUS, DBCont::DISABLE_STATUS);
    }

    /**
     * 启用记录
     */
    public function resume($ids): array
    {
        return $this->changeStatus($ids, DBCont::DISABLE_STATUS, DBCont::NORMAL_STATUS);
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

        // 清除缓存
        QscmfCache::clearByTag('{{TABLE_NAME_SNAKE}}_list');

        return $need_change_ids;
    }

    /**
     * 格式化列表数据
     */
    public function formatList(array &$list): void
    {
        if (empty($list)) {
            return;
        }

        // 批量获取关联数据（避免 N+1 查询）
        $cate_ids = array_column($list, 'cate_id');
        $cate_ids = array_filter(array_unique($cate_ids));

        $cate_list = [];
        if (!empty($cate_ids)) {
            $cate_list = D('Cate')
                ->where(['id' => ['IN', $cate_ids]])
                ->getField('id,name', true);
        }

        // 格式化每条记录
        foreach ($list as &$item) {
            $item['cate_name'] = $cate_list[$item['cate_id']]['name'] ?? '';
            $item['status_text'] = DBCont::getStatusList()[$item['status']] ?? '';
            $item['cover_url'] = !empty($item['cover']) ? get_image_url($item['cover']) : '';
            $item['create_time_text'] = !empty($item['create_time']) ? date('Y-m-d H:i', $item['create_time']) : '';
        }
    }
}
