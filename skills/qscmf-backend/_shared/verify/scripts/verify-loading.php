<?php
/**
 * Class Loading Verification Script
 *
 * Usage: php verify-loading.php /path/to/project "Namespace\\ClassName"
 *
 * This script is a REFERENCE TEMPLATE. AI should execute commands directly
 * in the target project directory, not deploy this script.
 */

if ($argc < 3) {
    echo "Usage: php verify-loading.php /path/to/project \"Namespace\\ClassName\"\n";
    exit(1);
}

$projectRoot = $argv[1];
$className = $argv[2];

$autoloadPath = $projectRoot . '/vendor/autoload.php';

if (!file_exists($autoloadPath)) {
    echo "[❌] Autoload not found at $autoloadPath\n";
    echo "    Run 'composer install' first\n";
    exit(1);
}

require_once $autoloadPath;

try {
    if (!class_exists($className)) {
        echo "[❌] Class not found: $className\n";
        exit(1);
    }

    // Try to instantiate (for classes with no required constructor params)
    $reflection = new ReflectionClass($className);
    if ($reflection->isInstantiable()) {
        // Don't actually instantiate, just check if it's possible
        echo "[✅] Class can be loaded: $className\n";
    } else {
        echo "[⚠️] Class exists but not instantiable: $className\n";
    }

    echo "[✅] Class loading verification passed\n";
    exit(0);

} catch (Throwable $e) {
    echo "[❌] Error loading class: $className\n";
    echo "    " . get_class($e) . ": " . $e->getMessage() . "\n";
    exit(1);
}
