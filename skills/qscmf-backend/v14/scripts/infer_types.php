#!/usr/bin/env php
<?php
/**
 * Infer field types for AntdAdmin forms
 *
 * This script must be run from the QSCMF project root directory.
 *
 * Three-layer strategy:
 * 1. Configuration file (.claude/qscmf/field-rules.yaml)
 * 2. Learned patterns from existing code
 * 3. Default rules based on field name patterns
 *
 * Usage:
 *   cd /path/to/qscmf/project
 *   php /path/to/skills/qscmf-backend/scripts/infer_types.php <field_name>
 *   php /path/to/skills/qscmf-backend/scripts/infer_types.php --scan <directory>
 *   php /path/to/skills/qscmf-backend/scripts/infer_types.php --all
 */

// Detect project root (current working directory)
$projectRoot = getcwd();

if (!is_dir($projectRoot . '/lara') || !is_dir($projectRoot . '/app')) {
    fwrite(STDERR, "Error: This script must be run from a QSCMF project root directory.\n");
    fwrite(STDERR, "Usage: cd /path/to/qscmf/project && php infer_types.php <field_name>\n");
    exit(1);
}

/**
 * Load field type configuration from project config
 */
function loadFieldRules(): array
{
    global $projectRoot;
    $configPath = $projectRoot . '/.claude/qscmf/field-rules.yaml';

    if (!file_exists($configPath)) {
        return [];
    }

    $yaml = file_get_contents($configPath);
    $config = [];
    foreach (explode("\n", $yaml) as $line) {
        if (preg_match('/^(\w+):\s*(\w+)/', $line, $matches)) {
            $config[$matches[1]] = $matches[2];
        }
    }
    return $config;
}

/**
 * Load learned patterns from existing code
 */
function loadLearnedPatterns(): array
{
    global $projectRoot;
    $learnPath = $projectRoot . '/.claude/qscmf/learned-field-types.json';

    if (!file_exists($learnPath)) {
        return [];
    }

    $data = json_decode(file_get_contents($learnPath), true);
    return $data['patterns'] ?? [];
}

/**
 * Apply default rules based on field name patterns
 */
function applyDefaultRules(string $field): string
{
    $patterns = [
        // Content fields
        '*_content' => 'ueditor',
        '*_desc' => 'textarea',
        '*_description' => 'textarea',
        '*_remark' => 'textarea',
        '*_note' => 'textarea',

        // Date/Time fields
        '*_date' => 'date',
        '*_time' => 'time',
        '*_at' => 'datetime',

        // Foreign keys
        '*_id' => 'select',
        'cate_id' => 'select',
        'category_id' => 'select',
        'user_id' => 'select',
        'admin_id' => 'select',

        // Status fields
        'status' => 'select',
        '*_status' => 'select',
        'audit_status' => 'select',

        // Image/File fields
        'cover' => 'image',
        'cover_id' => 'image',
        '*_image' => 'image',
        '*_img' => 'image',
        '*_file' => 'file',
        'file_id' => 'file',
        '*_url' => 'link',

        // Number fields
        'sort' => 'number',
        '*_sort' => 'number',
        '*_count' => 'number',
        '*_num' => 'number',
        '*_price' => 'number',

        // Boolean/Toggle
        'is_*' => 'switch',
        'has_*' => 'switch',
        '*_enabled' => 'switch',

        // Special fields
        'email' => 'email',
        '*_email' => 'email',
        'mobile' => 'mobile',
        '*_mobile' => 'mobile',
        'phone' => 'mobile',
        '*_phone' => 'mobile',
        'password' => 'password',
    ];

    foreach ($patterns as $pattern => $type) {
        if (str_starts_with($pattern, '*')) {
            $suffix = substr($pattern, 1);
            if (str_ends_with($field, $suffix)) {
                return $type;
            }
        } elseif (str_starts_with($pattern, 'is_') || str_starts_with($pattern, 'has_')) {
            $prefix = substr($pattern, 0, strpos($pattern, '*') + 1);
            if (str_starts_with($field, rtrim($prefix, '*'))) {
                return $type;
            }
        } else {
            // Exact match
            if ($field === $pattern) {
                return $type;
            }
        }
    }

    // Default: text field
    return 'text';
}

/**
 * Infer field type using three-layer strategy
 */
function inferFieldType(string $field): string
{
    // Layer 1: Configuration file
    $config = loadFieldRules();
    if (isset($config[$field])) {
        return $config[$field];
    }

    // Layer 2: Learned patterns
    $learned = loadLearnedPatterns();
    if (isset($learned[$field])) {
        return $learned[$field];
    }

    // Layer 3: Default rules
    return applyDefaultRules($field);
}

/**
 * Scan controller files to learn field usage patterns
 */
function scanControllersForPatterns(string $directory): array
{
    $patterns = [];
    $files = glob($directory . '/*Controller.class.php');

    foreach ($files as $file) {
        $content = file_get_contents($file);

        // Match form field definitions like:
        // $container->text('field_name', 'Title')
        // $columns->select('status', 'Status')
        preg_match_all('/\$(?:container|columns)->(\w+)\([\'"](\w+)[\'"]\s*,\s*[\'"]([^\'"]*)[\'"]/', $content, $matches, PREG_SET_ORDER);

        foreach ($matches as $match) {
            $method = $match[1];  // text, select, image, etc.
            $field = $match[2];
            $title = $match[3];

            // Learn the pattern
            if (!isset($patterns[$field])) {
                $patterns[$field] = $method;
            }
        }
    }

    return $patterns;
}

/**
 * Save learned patterns to file
 */
function saveLearnedPatterns(array $patterns): void
{
    global $projectRoot;
    $learnPath = $projectRoot . '/.claude/qscmf';
    if (!is_dir($learnPath)) {
        mkdir($learnPath, 0755, true);
    }

    $data = [
        'updated_at' => date('Y-m-d H:i:s'),
        'patterns' => $patterns
    ];

    file_put_contents(
        $learnPath . '/learned-field-types.json',
        json_encode($data, JSON_PRETTY_PRINT | JSON_UNESCAPED_UNICODE)
    );
}

// CLI Interface
if (php_sapi_name() === 'cli') {
    if ($argc < 2) {
        fwrite(STDERR, "Usage: php infer_types.php <field_name> | --scan <dir> | --all\n");
        exit(1);
    }

    $command = $argv[1];

    if ($command === '--scan') {
        // Scan directory and learn patterns
        $directory = $argv[2] ?? $projectRoot . '/app/Admin/Controller/';
        echo "Scanning {$directory}...\n";

        $patterns = scanControllersForPatterns($directory);
        saveLearnedPatterns($patterns);

        echo "Learned " . count($patterns) . " field patterns.\n";
        echo "Saved to .claude/qscmf/learned-field-types.json\n";

    } elseif ($command === '--all') {
        // Scan default directory
        $directory = $projectRoot . '/app/Admin/Controller/';
        echo "Scanning {$directory}...\n";

        $patterns = scanControllersForPatterns($directory);
        saveLearnedPatterns($patterns);

        echo "Learned " . count($patterns) . " field patterns.\n";

    } else {
        // Single field inference
        $field = $command;
        $type = inferFieldType($field);
        echo "{$field}: {$type}\n";
    }
}
