<?php
namespace Common\Model;
use Gy_Library\GyListModel;

/**
 * {{MODEL_TITLE}} Model
 */
class {{MODEL_NAME}}Model extends GyListModel
{
    protected $tableName = '{{TABLE_NAME}}';

    // TODO: Add validation rules
    // protected $_validate = [
{{VALIDATE_RULES}}
    // ];

    /**
     * Auto-complete fields
     */
    protected $_auto = [
        // ['create_time', 'time', self::MODEL_INSERT, 'function'],
        // ['update_time', 'time', self::MODEL_UPDATE, 'function'],
    ];
}
