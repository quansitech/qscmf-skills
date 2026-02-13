<?php
namespace Admin\Controller;
use Admin\Controller\QsListController;

/**
 * {{MODEL_TITLE}} Management
 */
class {{MODEL}}Controller extends QsListController
{
    protected $modelName = '{{MODEL_NAME}}';

    /**
     * List page with Table builder
     */
    public function index()
    {
        $table = new \Qscmf\Lib\AntdAdmin\Views\Table($this, $this->buildTableColumns(...));

        return $this->display($table);
    }

    /**
     * Build table columns
     */
    protected function buildTableColumns($container)
    {
{{TABLE_COLUMNS}}
    }

    /**
     * Add/Edit form
     */
    public function add()
    {
        $form = new \Qscmf\Lib\AntdAdmin\Views\Form($this, $this->buildFormColumns(...));

        return $this->display($form);
    }

    /**
     * Build form columns
     */
    protected function buildFormColumns($columns)
    {
{{FORM_ITEMS}}
    }

    /**
     * Save record (create or update)
     */
    public function save()
    {
        // TODO: Add business logic
        // TODO: Knowledge store sync if needed
        return parent::save();
    }

    /**
     * Delete record
     */
    public function delete()
    {
        // TODO: Add business logic (e.g., check dependencies)
        return parent::delete();
    }
}
