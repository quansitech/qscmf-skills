#!/usr/bin/env php
<?php
/**
 * Parse table schema from migration file or database
 *
 * Usage:
 *   php scripts/parse_schema.php <table_name>
 *
 * Output (JSON):
 *   {
 *     "table": "qs_product",
 *     "fields": [
 *       {"name": "product_name", "type": "varchar(200)", "comment": "产品名称", "form_type": "text"}
 *     ]
 *   }
 */

// Bootstrap Laravel
$projectRoot = __DIR__ . '/../../../../../../';
require_once $projectRoot . 'lara/bootstrap/app.php';

use Illuminate\Support\Facades\Schema;
use Illuminate\Support\Facades\DB;

$table = $argv[1] ?? null;

if (!$table) {
    fwrite(STDERR, "Usage: php parse_schema.php <table_name>\n");
    exit(1);
}

// Normalize table name (add qs_ prefix if needed)
if (!str_starts_with($table, 'qs_')) {
    $table = 'qs_' . strtolower($table);
}

$result = [
    'table' => $table,
    'fields' => []
];

// Option 1: Parse migration file
$migration_path = $projectRoot . 'lara/database/migrations';
$files = glob($migration_path . '/*' . str_replace('qs_', '', $table) . '*');

if (!empty($files)) {
    $migration_file = $files[0];
    $content = file_get_contents($migration_file);

    // Parse Schema::create from migration
    if (preg_match('/Schema::create\([\'"]' . preg_quote($table, '/') . '[\'"]\s*,\s*function\s*\(\$table\)\s*\{(.*?)\}/s', $content, $matches)) {
        $schema_body = $matches[1];

        // Parse column definitions
        preg_match_all('/\$table->(\w+)\([\'"](\w+)[\'"](?:\s*,\s*[^)]+)?\)(?:->comment\([\'"]([^\'"]*)[\'"]\))?(?:->nullable\(\))?(?:->default\([^)]+\))?;/', $schema_body, $columns, PREG_SET_ORDER);

        foreach ($columns as $col) {
            $field_name = $col[2];
            $field_type = $col[1];
            $comment = $col[3] ?? '';

            // Map Laravel types to form types
            $form_type = null;
            if ($comment) {
                // Parse @type=text from comment
                if (preg_match('/@type=(\w+)/', $comment, $type_match)) {
                    $form_type = $type_match[1];
                }
                // Parse @title from comment
                $comment = preg_replace('/@title=[^;]+;?\s*/', '', $comment);
            }

            $result['fields'][] = [
                'name' => $field_name,
                'type' => $field_type,
                'comment' => $comment,
                'form_type' => $form_type
            ];
        }
    }
}

// Option 2: Fallback to database query
if (empty($result['fields']) && Schema::hasTable($table)) {
    $columns = DB::select("SHOW FULL COLUMNS FROM `{$table}`");

    foreach ($columns as $col) {
        $result['fields'][] = [
            'name' => $col->Field,
            'type' => $col->Type,
            'comment' => $col->Comment,
            'form_type' => null
        ];
    }
}

// Output JSON
echo json_encode($result, JSON_PRETTY_PRINT | JSON_UNESCAPED_UNICODE);
