# Abstract Base Pattern

## When to Use

When you have multiple similar modules (e.g., Article, News, Blog), create an abstract base class to reduce duplication.

## Architecture

```
ACateController (abstract)
    ├── CategoryController
    ├── TagController
    └── TypeController

ACateModel (abstract)
    ├── CategoryModel
    ├── TagModel
    └── TypeModel
```

## Abstract Base Controller

```php
namespace Admin\Controller;
use Admin\Controller\QsListController;
use Think\Db;

abstract class ACateController extends QsListController
{
    /**
     * Subclass must define table name
     */
    abstract protected function getTableName(): string;

    /**
     * Subclass must define module title
     */
    abstract protected function getModuleTitle(): string;

    /**
     * Common list page
     */
    public function index()
    {
        $table = new \Qscmf\Lib\AntdAdmin\Views\Table($this, $this->buildTableColumns(...));
        return $this->display($table);
    }

    /**
     * Build common table columns
     */
    protected function buildTableColumns($container)
    {
        $container->text('id', 'ID')->setWidth(80)->setSortable(true);
        $container->text('name', '名称')->setEllipsis(true);
        $container->text('sort', '排序')->setWidth(100)->setSortable(true);
        $container->switch('status', '状态');

        // Allow subclass to add custom columns
        $this->customTableColumns($container);
    }

    /**
     * Hook for subclass customization
     */
    protected function customTableColumns($container)
    {
        // Override in subclass if needed
    }

    /**
     * Common form
     */
    public function add()
    {
        $form = new \Qscmf\Lib\AntdAdmin\Views\Form($this, $this->buildFormColumns(...));
        return $this->display($form);
    }

    /**
     * Build common form columns
     */
    protected function buildFormColumns($columns)
    {
        $columns->text('name', '名称')
            ->setRequired(true)
            ->addRule(new Required());

        $columns->number('sort', '排序')
            ->setDefault(0);

        $columns->switch('status', '状态')
            ->setDefault(1);

        // Allow subclass to add custom fields
        $this->customFormColumns($columns);
    }

    /**
     * Hook for subclass customization
     */
    protected function customFormColumns($columns)
    {
        // Override in subclass if needed
    }
}
```

## Concrete Implementation

```php
namespace Admin\Controller;

/**
 * Category Management
 */
class CategoryController extends ACateController
{
    protected function getTableName(): string
    {
        return 'category';
    }

    protected function getModuleTitle(): string
    {
        return '分类';
    }

    /**
     * Add category-specific columns
     */
    protected function customTableColumns($container)
    {
        $container->text('icon', '图标');
        $container->number('article_count', '文章数');
    }

    /**
     * Add category-specific form fields
     */
    protected function customFormColumns($columns)
    {
        $columns->text('icon', '图标');
        $columns->select('parent_id', '父分类')
            ->setOptions(function() {
                return D('Category')->where([
                    'parent_id' => 0
                ])->getField('id,name', true);
            });
    }
}
```

## Abstract Base Model

```php
namespace Common\Model;
use Gy_Library\GyListModel;

abstract class ACateModel extends GyListModel
{
    protected $pk = 'id';

    /**
     * Get tree structure
     */
    public function getTree(int $parentId = 0): array
    {
        $list = $this->where(['parent_id' => $parentId])->select();
        $tree = [];

        foreach ($list as $item) {
            $item['children'] = $this->getTree($item['id']);
            $tree[] = $item;
        }

        return $tree;
    }

    /**
     * Get path to root
     */
    public function getPath(int $id): array
    {
        $path = [];

        while ($id > 0) {
            $item = $this->find($id);
            if (!$item) break;

            array_unshift($path, $item);
            $id = $item['parent_id'];
        }

        return $path;
    }
}
```

→ [Abstract Base Patterns](references/abstract-base-patterns.md)
