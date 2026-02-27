# Admin Controllers Reference

> QSCMF v13 后台管理控制器开发指南

## 概述

QSCMF v13 后台管理系统使用 `QsListController` 作为基础控制器，配合 `\Qscmf\Builder\ListBuilder` 和 `\Qscmf\Builder\FormBuilder` 实现 CRUD 功能。

## 版本特性

| 特性 | v13 |
|------|-----|
| PHP 版本 | >= 8.1 |
| PHPUnit | ^9.3.0 |
| 前端框架 | jQuery 3.7 |
| 列表构建器 | ListBuilder |
| 表单构建器 | FormBuilder |
| 富文本 | UEditor |

## 标准模式

### 基本结构

```php
<?php
namespace Admin\Controller;

use Admin\Controller\QsListController;
use Qscmf\Builder\ListBuilder;
use Qscmf\Builder\FormBuilder;

class XxxController extends QsListController
{
    protected $modelName = 'Xxx';

    public function index()
    {
        $get_data = I('get.');
        $map = [];
        $this->buildSearchWhere($get_data, $map);

        $model = D($this->modelName);
        $count = $model->where($map)->count();
        $per_page = C('ADMIN_PER_PAGE_NUM', null, 20);

        $page = new \Gy_Library\GyPage($count, $per_page);
        $data_list = $model->where($map)
            ->page($page->nowPage, $page->listRows)
            ->order('sort asc, id desc')
            ->select();

        $builder = new ListBuilder();
        $builder->setMetaTitle('列表管理')
            ->setTableName($this->modelName)
            ->addTopButton('addnew')
            ->addTopButton('forbid')
            ->addTopButton('resume')
            ->addTopButton('delete')
            ->addTableColumn('id', 'ID')
            ->addTableColumn('title', '标题')
            ->addTableColumn('status', '状态', 'status')
            ->addTableColumn('sort', '排序', '', '', true)
            ->addTableColumn('right_button', '操作', 'right_button')
            ->addRightButton('edit')
            ->addRightButton('forbid')
            ->addRightButton('delete')
            ->setListData($data_list)
            ->setPage($page->show())
            ->build();
    }

    public function add()
    {
        $builder = new FormBuilder();
        $builder->setMetaTitle('新增')
            ->setPostUrl(U('add'))
            ->addFormItem('title', 'text', '标题', '', '', '', 'required')
            ->addFormItem('status', 'select', '状态', '', DBCont::getStatusList())
            ->addFormItem('sort', 'number', '排序', '', '', '', 'min="0"');

        if (IS_POST) {
            $data = $builder->getFormData();
            $result = D($this->modelName)->add($data);
            if ($result) {
                $this->success('添加成功', U('index'));
            } else {
                $this->error('添加失败');
            }
        }

        $builder->build();
    }

    public function edit($id = 0)
    {
        $data = D($this->modelName)->find($id);
        if (!$data) {
            $this->error('记录不存在');
        }

        $builder = new FormBuilder();
        $builder->setMetaTitle('编辑')
            ->setPostUrl(U('edit'))
            ->addFormItem('id', 'hidden', '', '')
            ->addFormItem('title', 'text', '标题', '', '', '', 'required')
            ->addFormItem('status', 'select', '状态', '', DBCont::getStatusList())
            ->addFormItem('sort', 'number', '排序', '', '', '', 'min="0"')
            ->setFormData($data);

        if (IS_POST) {
            $data = $builder->getFormData();
            $result = D($this->modelName)->save($data);
            if ($result !== false) {
                $this->success('保存成功', U('index'));
            } else {
                $this->error('保存失败');
            }
        }

        $builder->build();
    }
}
```

## ListBuilder API

### 核心方法

| 方法 | 说明 | 参数 |
|------|------|------|
| `setMetaTitle($title)` | 设置页面标题 | 标题字符串 |
| `setTableName($name)` | 设置表名 | 模型名称 |
| `setListData($data)` | 设置列表数据 | 数组数据 |
| `setPage($page_html)` | 设置分页HTML | 分页HTML |
| `setCheckBox($show, $callback)` | 设置复选框 | 是否显示, 回调 |
| `build()` | 构建并输出页面 | - |

### 顶部按钮

```php
// 新增按钮
->addTopButton('addnew', ['title' => '新增', 'href' => U('add')])

// 禁用按钮
->addTopButton('forbid', ['title' => '禁用'])

// 启用按钮
->addTopButton('resume', ['title' => '启用'])

// 删除按钮
->addTopButton('delete', ['title' => '删除'])

// 自定义按钮
->addTopButton('self', [
    'title' => '导出',
    'class' => 'btn btn-info',
    'href' => U('export')
])
```

### 表格列

```php
// 文本列
->addTableColumn('title', '标题')

// 状态列（自动显示启用/禁用）
->addTableColumn('status', '状态', 'status')

// 日期列
->addTableColumn('create_time', '创建时间', 'time')

// 图片列
->addTableColumn('cover', '封面', 'picture')

// 可编辑列（行内编辑）
->addTableColumn('sort', '排序', '', '', true)

// 数字列
->addTableColumn('price', '价格', 'num')

// 下拉选择列
->addTableColumn('cate_id', '分类', 'select', $cate_list)

// 右侧操作按钮
->addTableColumn('right_button', '操作', 'right_button')
```

### 列类型参考

| 类型 | 说明 | value 参数 |
|------|------|-----------|
| `status` | 状态显示 | 可选自定义状态映射 |
| `time` | 时间格式化 | 可选日期格式，默认 'Y-m-d H:i:s' |
| `date` | 日期格式化 | 可选日期格式，默认 'Y-m-d' |
| `picture` | 图片显示 | 可选缩略图回调 |
| `pictures` | 多图显示 | 可选代理配置 |
| `num` | 数字显示 | - |
| `select` | 下拉文本 | 选项数组 |
| `icon` | 图标显示 | - |
| `a` | 链接显示 | 链接配置 |
| `fun` | 自定义函数 | 回调函数 |
| `checkbox` | 复选框 | - |
| `textarea` | 长文本 | - |
| `arr` | 数组显示 | - |

### 右侧按钮

```php
// 编辑按钮
->addRightButton('edit', ['title' => '编辑'])

// 禁用按钮
->addRightButton('forbid', ['title' => '禁用'])

// 启用按钮
->addRightButton('resume', ['title' => '启用'])

// 删除按钮
->addRightButton('delete', ['title' => '删除'])

// 自定义按钮（使用占位符）
->addRightButton('self', [
    'title' => '查看详情',
    'class' => 'label label-primary',
    'href' => U('detail', ['id' => '__data_id__'])
])
```

### 搜索栏

```php
// 文本搜索
->addSearchItem('keyword', 'text', '关键词')

// 下拉搜索
->addSearchItem('status', 'select', '状态', DBCont::getStatusList())

// 日期范围搜索
->addSearchItem('create_time', 'date_range', '创建时间')

// 城市选择
->addSearchItem('city_id', 'select_city', '城市')

// 隐藏字段
->addSearchItem('cate_id', 'hidden', '', $cate_id)
```

### 搜索项解析

```php
use Qscmf\Builder\ListSearchItem\DateRange;
use Qscmf\Builder\ListSearchItem\Hidden;
use Qscmf\Builder\ListSearchItem\Text;

// 日期范围解析
$map = array_merge($map, DateRange::parse('date_range', 'create_time', $get_data));

// 文本解析（模糊匹配）
$map = array_merge($map, Text::parse('keyword', 'title', $get_data, 'fuzzy'));

// 文本解析（精确匹配）
$map = array_merge($map, Text::parse('status', 'status', $get_data, 'exact'));

// 隐藏字段解析
$map = array_merge($map, Hidden::parse('cate_id', 'cate_id', $get_data));
```

## FormBuilder API

### 核心方法

| 方法 | 说明 | 参数 |
|------|------|------|
| `setMetaTitle($title)` | 设置页面标题 | 标题字符串 |
| `setPostUrl($url)` | 设置提交URL | URL地址 |
| `setFormData($data)` | 设置表单数据 | 数据数组 |
| `setShowBtn($show)` | 是否显示按钮 | 布尔值 |
| `setReadOnly($readonly)` | 设置只读模式 | 布尔值 |
| `build()` | 构建并输出页面 | - |

### 表单字段类型

```php
// 文本输入
->addFormItem('title', 'text', '标题', '提示信息', '', '', 'required')

// 隐藏字段
->addFormItem('id', 'hidden', '', '')

// 多行文本
->addFormItem('summary', 'textarea', '摘要', '', '', '', 'rows="3"')

// 数字输入
->addFormItem('sort', 'number', '排序', '', '', '', 'min="0" max="999"')

// 下拉选择
->addFormItem('cate_id', 'select', '分类', '', $cate_list)

// 下拉多选
->addFormItem('tag_ids', 'select2', '标签', '', $tag_list, '', 'multiple="multiple"')

// 单选框
->addFormItem('type', 'radio', '类型', '', $type_list)

// 复选框
->addFormItem('is_top', 'checkbox', '置顶', '', ['1' => '是'])

// 日期选择
->addFormItem('publish_date', 'date', '发布日期')

// 日期时间选择
->addFormItem('datetime', 'datetime', '日期时间', '', ['format' => 'yyyy-mm-dd hh:ii:ss'])

// 图片上传
->addFormItem('cover_id', 'picture', '封面图', '', '', '', 'data-size="2"')

// 多图上传
->addFormItem('images', 'pictures', '图片集', '', '', '', 'data-limit="9"')

// 文件上传
->addFormItem('file_id', 'file', '附件', '', '', '', 'data-ext="doc,docx,pdf"')

// 富文本编辑器
->addFormItem('content', 'ueditor', '内容', '', '', '', 'data-url="/Public/ueditor/php/controller.php"')

// 省市区选择
->addFormItem('city_id', 'district', '地区', '', ['level' => 3])
```

### 表单验证

```php
// HTML5 验证
->addFormItem('title', 'text', '标题', '', '', '', 'required maxlength="200"')
->addFormItem('price', 'number', '价格', '', '', '', 'required min="0" step="0.01"')
->addFormItem('email', 'text', '邮箱', '', '', '', 'type="email"')
```

### 表单底部扩展

```php
use Qscmf\Builder\DividerBuilder;
use Qscmf\Builder\TableBuilder;

// 添加分割线
->addBottom((new DividerBuilder())->setTitle('附加信息'))

// 添加表格
$table = new TableBuilder();
$table->addColumn(['title' => '名称', 'dataIndex' => 'name'])
      ->addRow(['name' => '测试数据']);
->addBottom($table)
```

### 自定义按钮

```php
// 隐藏默认按钮，添加自定义按钮
->setShowBtn(false)
->addButton('forbid')
->addButton('delete')
->addButton('self', [
    'title' => '查看',
    'class' => 'btn btn-info',
    'onclick' => "window.location.href='" . U('view', ['id' => '__data_id__']) . "'"
])
```

## QsListController 核心属性

| 属性 | 类型 | 说明 |
|------|------|------|
| `$modelName` | string | 关联的模型名称（如 'Demo', 'User'） |

## QsListController 核心方法

| 方法 | 说明 | 是否可重写 |
|------|------|-----------|
| `index()` | 列表页 | ✅ 推荐 |
| `add()` | 新增页 | ✅ 推荐 |
| `edit($id)` | 编辑页 | ✅ 推荐 |
| `save()` | 保存（批量更新排序） | ⚠️ 可选 |
| `delete()` | 删除 | ⚠️ 可选 |
| `forbid()` | 禁用 | ⚠️ 可选 |
| `resume()` | 启用 | ⚠️ 可选 |

## 扩展功能

### 批量操作

```php
public function batchProcess()
{
    $ids = I('ids');
    if (!$ids) {
        $this->error('请选择要操作的数据');
    }

    // 批量处理逻辑
    $result = D($this->modelName)
        ->where(['id' => ['in', $ids]])
        ->save(['status' => DBCont::NORMAL_STATUS]);

    $this->success('操作成功');
}
```

### Redis 锁

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
    } finally {
        $lock->release();
    }
}
```

### 权限控制

```php
// 在添加按钮/字段时指定权限点
->addTopButton('addnew', ['title' => '新增'], '', 'admin.Xxx.add')
->addRightButton('delete', ['title' => '删除'], '', 'admin.Xxx.delete')

// 多权限逻辑（AND）
->addRightButton('edit', ['title' => '编辑'], '', [
    'node' => ['admin.Xxx.edit', 'admin.Xxx.view'],
    'logic' => 'and'
])

// 多权限逻辑（OR）
->addRightButton('export', ['title' => '导出'], '', [
    'node' => ['admin.Xxx.export', 'admin.Xxx.all'],
    'logic' => 'or'
])
```

## 完整示例

```php
<?php
namespace Admin\Controller;

use Admin\Controller\QsListController;
use Qscmf\Builder\ListBuilder;
use Qscmf\Builder\FormBuilder;
use Gy_Library\DBCont;

class ProductController extends QsListController
{
    protected $modelName = 'Product';

    public function index()
    {
        $get_data = I('get.');
        $map = [];

        // 搜索条件
        if (!empty($get_data['keyword'])) {
            $map['product_name'] = ['like', '%' . $get_data['keyword'] . '%'];
        }
        if (isset($get_data['status']) && $get_data['status'] !== '') {
            $map['status'] = $get_data['status'];
        }
        if (!empty($get_data['cate_id'])) {
            $map['cate_id'] = $get_data['cate_id'];
        }

        $model = D($this->modelName);
        $count = $model->where($map)->count();
        $per_page = C('ADMIN_PER_PAGE_NUM', null, 20);
        $page = new \Gy_Library\GyPage($count, $per_page);

        $data_list = $model->where($map)
            ->page($page->nowPage, $page->listRows)
            ->order('sort asc, id desc')
            ->select();

        $cate_list = D('Cate')->getField('id,name');

        $builder = new ListBuilder();
        $builder->setMetaTitle('产品列表')
            ->setTableName($this->modelName)
            ->addSearchItem('keyword', 'text', '产品名称')
            ->addSearchItem('status', 'select', '状态', DBCont::getStatusList())
            ->addSearchItem('cate_id', 'select', '分类', $cate_list)
            ->addTopButton('addnew')
            ->addTopButton('forbid')
            ->addTopButton('resume')
            ->addTopButton('delete')
            ->addTableColumn('id', 'ID')
            ->addTableColumn('product_name', '产品名称')
            ->addTableColumn('cate_id', '分类', 'select', $cate_list)
            ->addTableColumn('price', '价格', 'num')
            ->addTableColumn('status', '状态', 'status')
            ->addTableColumn('sort', '排序', '', '', true)
            ->addTableColumn('right_button', '操作', 'right_button')
            ->addRightButton('edit')
            ->addRightButton('forbid')
            ->addRightButton('delete')
            ->setListData($data_list)
            ->setPage($page->show())
            ->build();
    }

    public function add()
    {
        $cate_list = D('Cate')->getField('id,name');

        $builder = new FormBuilder();
        $builder->setMetaTitle('新增产品')
            ->setPostUrl(U('add'))
            ->addFormItem('product_name', 'text', '产品名称', '', '', '', 'required maxlength="200"')
            ->addFormItem('cate_id', 'select', '分类', '', $cate_list, '', 'required')
            ->addFormItem('price', 'number', '价格', '', '', '', 'required min="0" step="0.01"')
            ->addFormItem('cover_id', 'picture', '封面图')
            ->addFormItem('summary', 'textarea', '简介', '', '', '', 'rows="3"')
            ->addFormItem('content', 'ueditor', '详情', '', '', '', 'data-url="/Public/ueditor/php/controller.php"')
            ->addFormItem('sort', 'number', '排序', '', '', '', 'min="0"')
            ->addFormItem('status', 'select', '状态', '', DBCont::getStatusList());

        if (IS_POST) {
            $data = $builder->getFormData();
            $result = D($this->modelName)->add($data);
            if ($result) {
                $this->success('添加成功', U('index'));
            } else {
                $this->error('添加失败：' . D($this->modelName)->getError());
            }
        }

        $builder->build();
    }

    public function edit($id = 0)
    {
        $data = D($this->modelName)->find($id);
        if (!$data) {
            $this->error('记录不存在');
        }

        $cate_list = D('Cate')->getField('id,name');

        $builder = new FormBuilder();
        $builder->setMetaTitle('编辑产品')
            ->setPostUrl(U('edit'))
            ->addFormItem('id', 'hidden', '', '')
            ->addFormItem('product_name', 'text', '产品名称', '', '', '', 'required maxlength="200"')
            ->addFormItem('cate_id', 'select', '分类', '', $cate_list, '', 'required')
            ->addFormItem('price', 'number', '价格', '', '', '', 'required min="0" step="0.01"')
            ->addFormItem('cover_id', 'picture', '封面图')
            ->addFormItem('summary', 'textarea', '简介', '', '', '', 'rows="3"')
            ->addFormItem('content', 'ueditor', '详情', '', '', '', 'data-url="/Public/ueditor/php/controller.php"')
            ->addFormItem('sort', 'number', '排序', '', '', '', 'min="0"')
            ->addFormItem('status', 'select', '状态', '', DBCont::getStatusList())
            ->setFormData($data);

        if (IS_POST) {
            $data = $builder->getFormData();
            $result = D($this->modelName)->save($data);
            if ($result !== false) {
                $this->success('保存成功', U('index'));
            } else {
                $this->error('保存失败：' . D($this->modelName)->getError());
            }
        }

        $builder->build();
    }
}
```

## 最佳实践

### 1. 使用 DBCont 常量

```php
use Gy_Library\DBCont;

DBCont::NORMAL_STATUS    // = 1 (启用)
DBCont::FORBIDDEN_STATUS   // = 0 (禁用)
DBCont::AUDIT_STATUS     // = 2 (待审核)

DBCont::getStatusList()  // [1 => '启用', 0 => '禁用']
```

### 2. 日志记录

```php
sysLogs('操作描述, id:' . $id);
```

### 3. 表单宽度规范

v13 使用 CSS 类控制表单布局，通过 `extra_class` 参数设置。

### 4. 锁定表格行列

```php
// 锁定行
$builder->setLockRow(1);

// 锁定左侧列
$builder->setLockCol(1);

// 锁定右侧列
$builder->setLockColRight(1);
```

### 5. 下拉分页风格

```php
use Qscmf\Lib\QsPage;

// 开启下拉风格
QsPage::setPullStyle(true);
```

## 相关文档

- [Abstract Base Patterns](abstract-base-patterns.md) - 抽象基类模式
- [Migration Metadata](migration-metadata.md) - 迁移文件元数据
- [Migration Guide](migration-guide.md) - 数据库迁移指南
- [Development Standards](development-standards.md) - 开发规范
