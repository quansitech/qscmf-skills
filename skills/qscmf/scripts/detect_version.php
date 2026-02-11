#!/usr/bin/env php
<?php
/**
 * QSCMF Version Detector
 *
 * Detects the current QSCMF version from composer.lock or composer.json
 * Priority: composer.lock > composer.json
 *
 * Usage: php detect_version.php [--format=json|text]
 *
 * Output formats:
 *   - json: {"version": "v14", "source": "composer.lock", "raw": "1.4.0"}
 *   - text: v14
 */

$options = getopt('', ['format:']);
$format = isset($options['format']) ? $options['format'] : 'text';

// Detect version
$result = detectQSCMFVersion(getcwd());

// Output based on format
if ($format === 'json') {
    echo json_encode($result, JSON_PRETTY_PRINT);
} else {
    echo $result['version'] . "\n";
}

exit(0);

/**
 * Detect QSCMF version from project directory
 *
 * @param string $projectDir Project directory path
 * @return array Detection result with version, source, and raw version
 */
function detectQSCMFVersion($projectDir)
{
    // Try composer.lock first (highest priority)
    $composerLock = $projectDir . '/composer.lock';
    if (file_exists($composerLock)) {
        $version = getVersionFromComposerLock($composerLock);
        if ($version) {
            return [
                'version' => normalizeVersion($version),
                'source' => 'composer.lock',
                'raw' => $version
            ];
        }
    }

    // Fallback to composer.json
    $composerJson = $projectDir . '/composer.json';
    if (file_exists($composerJson)) {
        $version = getVersionFromComposerJson($composerJson);
        if ($version) {
            return [
                'version' => normalizeVersion($version),
                'source' => 'composer.json',
                'raw' => $version
            ];
        }
    }

    // Not found
    return [
        'version' => null,
        'source' => null,
        'raw' => null
    ];
}

/**
 * Get version from composer.lock
 *
 * @param string $file Path to composer.lock
 * @return string|null Version string or null if not found
 */
function getVersionFromComposerLock($file)
{
    $content = file_get_contents($file);
    $data = json_decode($content, true);

    if (!$data || !isset($data['packages'])) {
        return null;
    }

    // Search for qscmf package
    foreach ($data['packages'] as $package) {
        if (isset($package['name']) && $package['name'] === 'tiderjian/qscmf') {
            return isset($package['version']) ? ltrim($package['version'], 'v') : null;
        }
    }

    return null;
}

/**
 * Get version from composer.json
 *
 * @param string $file Path to composer.json
 * @return string|null Version string or null if not found
 */
function getVersionFromComposerJson($file)
{
    $content = file_get_contents($file);
    $data = json_decode($content, true);

    if (!$data) {
        return null;
    }

    // Check require section
    if (isset($data['require']['tiderjian/qscmf'])) {
        $constraint = $data['require']['tiderjian/qscmf'];
        return extractVersionFromConstraint($constraint);
    }

    // Check require-dev section
    if (isset($data['require-dev']['tiderjian/qscmf'])) {
        $constraint = $data['require-dev']['tiderjian/qscmf'];
        return extractVersionFromConstraint($constraint);
    }

    return null;
}

/**
 * Extract version from composer constraint
 *
 * @param string $constraint Composer version constraint (e.g., "^1.4", "~1.4.0", "1.4.*")
 * @return string|null Extracted version or null
 */
function extractVersionFromConstraint($constraint)
{
    // Remove operators and extract version
    $constraint = trim($constraint);
    $constraint = preg_replace('/^[~^><=*]+/', '', $constraint);
    $constraint = preg_replace('/[^0-9.].*$/', '', $constraint);

    return $constraint ?: null;
}

/**
 * Normalize version to v{major} format
 *
 * @param string $version Version string (e.g., "13.0.0", "14.5", "15.2.1")
 * @return string Normalized version (e.g., "v13", "v14", "v15")
 */
function normalizeVersion($version)
{
    // Remove 'v' prefix if present
    $version = ltrim($version, 'v');

    // Parse version parts
    $parts = explode('.', $version);
    $major = isset($parts[0]) ? (int)$parts[0] : 0;

    // QSCMF 13.x.x -> v13, 14.x.x -> v14, 15.x.x -> v15
    return 'v' . $major;
}
