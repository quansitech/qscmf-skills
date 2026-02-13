<?php
/**
 * QSCMF Version Detection Script
 *
 * Detects QSCMF version from multiple sources with fallback strategy.
 * Returns: "v13", "v14", "v15", or null
 *
 * Detection Priority:
 *   1. Environment variable (QSCMF_VERSION)
 *   2. composer.json (tiderjian/think-core)
 *   3. Config file (.qscmf-version)
 *   4. Directory structure markers
 *   5. Feature detection
 *
 * Usage:
 *   php _shared/detect-version.php [project_root] [--json]
 *
 * Options:
 *   --json    Output full detection result as JSON
 *   --force   Force re-detection (ignore cache)
 */

/**
 * Version detection result
 */
class VersionDetectionResult
{
    public ?string $version;
    public string $source;
    public float $confidence;
    public array $details;
    public string $projectRoot;
    public int $detectedAt;

    public function __construct(
        ?string $version,
        string $source,
        float $confidence = 1.0,
        array $details = []
    ) {
        $this->version = $version;
        $this->source = $source;
        $this->confidence = $confidence;
        $this->details = $details;
        $this->detectedAt = time();
    }

    public function toArray(): array
    {
        return [
            'version' => $this->version,
            'source' => $this->source,
            'confidence' => $this->confidence,
            'details' => $this->details,
            'detected_at' => $this->detectedAt,
        ];
    }
}

/**
 * Main version detector class
 */
class QscmfVersionDetector
{
    private string $projectRoot;
    private bool $forceDetection;
    private ?VersionDetectionResult $result = null;

    // Version feature matrix
    private const VERSION_FEATURES = [
        'v14' => [
            'antd_admin' => true,
            'phpunit_10' => true,
            'refactored_upload' => true,
            'react_components' => true,
        ],
        'v13' => [
            'antd_admin' => false,
            'phpunit_10' => false,
            'refactored_upload' => false,
            'react_components' => false,
        ],
    ];

    // Directory markers for each version
    private const VERSION_MARKERS = [
        'v14' => [
            '/vendor/quansitech/antd-admin/',
            '/app/Node/',
            '/resources/js/',
            '/lara/tests/Pest.php',
        ],
        'v13' => [
            '/Public/Common/',
            '/app/Home/Controller/',
            '/app/Lib/',
        ],
    ];

    public function __construct(string $projectRoot, bool $forceDetection = false)
    {
        $this->projectRoot = rtrim($projectRoot, '/');
        $this->forceDetection = $forceDetection;
    }

    /**
     * Detect QSCMF version using multi-layer strategy
     */
    public function detect(): VersionDetectionResult
    {
        // Return cached result if available
        if (!$this->forceDetection && $this->result !== null) {
            return $this->result;
        }

        // Try each detection method in order of reliability
        $detectionMethods = [
            'detectFromEnvironment',
            'detectFromComposer',
            'detectFromConfigFile',
            'detectFromDirectoryMarkers',
            'detectFromFeatures',
        ];

        foreach ($detectionMethods as $method) {
            $result = $this->$method();
            if ($result !== null) {
                $this->result = $result;
                return $result;
            }
        }

        // Unable to detect
        $this->result = new VersionDetectionResult(
            null,
            'unknown',
            0.0,
            ['error' => 'Unable to detect QSCMF version']
        );

        return $this->result;
    }

    /**
     * Detect from environment variable
     */
    private function detectFromEnvironment(): ?VersionDetectionResult
    {
        $envVersion = getenv('QSCMF_VERSION');
        if ($envVersion && $this->isValidVersion($envVersion)) {
            return new VersionDetectionResult(
                $envVersion,
                'environment',
                1.0,
                ['variable' => 'QSCMF_VERSION']
            );
        }
        return null;
    }

    /**
     * Detect from composer.json
     */
    private function detectFromComposer(): ?VersionDetectionResult
    {
        $composerJson = $this->projectRoot . '/composer.json';

        if (!file_exists($composerJson)) {
            return null;
        }

        $composer = json_decode(file_get_contents($composerJson), true);
        if (json_last_error() !== JSON_ERROR_NONE) {
            return null;
        }

        // Check think-core version
        $thinkCoreVersion = $composer['require']['tiderjian/think-core'] ?? null;
        if ($thinkCoreVersion) {
            if (preg_match('/\^(\d+)\.\d+/', $thinkCoreVersion, $matches)) {
                $version = "v{$matches[1]}";
                return new VersionDetectionResult(
                    $version,
                    'composer',
                    1.0,
                    [
                        'think_core' => $thinkCoreVersion,
                        'php_version' => $composer['require']['php'] ?? 'unknown',
                    ]
                );
            }
        }

        // Check antd-admin dependency (v14 specific)
        if (isset($composer['require']['quansitech/antd-admin'])) {
            return new VersionDetectionResult(
                'v14',
                'composer_dependency',
                0.95,
                ['antd_admin' => $composer['require']['quansitech/antd-admin']]
            );
        }

        return null;
    }

    /**
     * Detect from .qscmf-version config file
     */
    private function detectFromConfigFile(): ?VersionDetectionResult
    {
        $configFile = $this->projectRoot . '/.qscmf-version';

        if (!file_exists($configFile)) {
            return null;
        }

        $version = trim(file_get_contents($configFile));
        if ($this->isValidVersion($version)) {
            return new VersionDetectionResult(
                $version,
                'config_file',
                1.0,
                ['file' => '.qscmf-version']
            );
        }

        return null;
    }

    /**
     * Detect from directory structure markers
     */
    private function detectFromDirectoryMarkers(): ?VersionDetectionResult
    {
        $scores = [];

        foreach (self::VERSION_MARKERS as $version => $markers) {
            $matchedCount = 0;
            foreach ($markers as $marker) {
                if (is_dir($this->projectRoot . $marker) || file_exists($this->projectRoot . $marker)) {
                    $matchedCount++;
                }
            }
            if ($matchedCount > 0) {
                $scores[$version] = $matchedCount / count($markers);
            }
        }

        if (empty($scores)) {
            return null;
        }

        // Get version with highest score
        arsort($scores);
        $bestVersion = array_key_first($scores);
        $confidence = $scores[$bestVersion];

        return new VersionDetectionResult(
            $bestVersion,
            'directory_markers',
            $confidence,
            ['scores' => $scores]
        );
    }

    /**
     * Detect from feature presence
     */
    private function detectFromFeatures(): ?VersionDetectionResult
    {
        $featureScores = [];

        foreach (self::VERSION_FEATURES as $version => $features) {
            $matchCount = 0;
            $totalFeatures = count($features);

            foreach ($features as $feature => $expectedValue) {
                $actualValue = $this->detectFeature($feature);
                if ($actualValue === $expectedValue) {
                    $matchCount++;
                }
            }

            if ($matchCount > 0) {
                $featureScores[$version] = $matchCount / $totalFeatures;
            }
        }

        if (empty($featureScores)) {
            return null;
        }

        arsort($featureScores);
        $bestVersion = array_key_first($featureScores);
        $confidence = $featureScores[$bestVersion];

        // Only accept if confidence is above threshold
        if ($confidence < 0.5) {
            return null;
        }

        return new VersionDetectionResult(
            $bestVersion,
            'feature_detection',
            $confidence,
            ['feature_scores' => $featureScores]
        );
    }

    /**
     * Detect individual feature presence
     */
    private function detectFeature(string $feature): bool
    {
        return match ($feature) {
            'antd_admin' => is_dir($this->projectRoot . '/vendor/quansitech/antd-admin'),
            'phpunit_10' => file_exists($this->projectRoot . '/vendor/bin/phpunit')
                && str_contains(file_get_contents($this->projectRoot . '/composer.lock') ?: '', '"version": "10.'),
            'refactored_upload' => file_exists($this->projectRoot . '/app/Common/Service/UploadService.php'),
            'react_components' => is_dir($this->projectRoot . '/resources/js/components'),
            default => false,
        };
    }

    /**
     * Validate version string
     */
    private function isValidVersion(string $version): bool
    {
        return (bool) preg_match('/^v\d+$/', $version);
    }

    /**
     * Get version-specific configuration file path
     */
    public function getConfigPath(): string
    {
        $result = $this->detect();
        $version = $result->version ?? 'v14';

        // Return path relative to skill root
        return dirname(__DIR__) . "/_shared/config/{$version}.yaml";
    }

    /**
     * Get version-specific template directory
     */
    public function getTemplateDir(): string
    {
        $result = $this->detect();
        $version = $result->version ?? 'v14';

        return dirname(__DIR__) . "/_shared/templates/{$version}";
    }
}

// CLI interface
function main(array $argv): int
{
    $projectRoot = getcwd();
    $outputJson = false;
    $forceDetection = false;

    // Parse arguments
    for ($i = 1; $i < count($argv); $i++) {
        if ($argv[$i] === '--json') {
            $outputJson = true;
        } elseif ($argv[$i] === '--force') {
            $forceDetection = true;
        } elseif (!str_starts_with($argv[$i], '-')) {
            $projectRoot = $argv[$i];
        }
    }

    // Run detection
    $detector = new QscmfVersionDetector($projectRoot, $forceDetection);
    $result = $detector->detect();

    // Cache result
    if ($result->version !== null) {
        $cacheDir = ($_SERVER['HOME'] ?? '/tmp') . '/.claude/cache/qscmf';
        if (!is_dir($cacheDir)) {
            mkdir($cacheDir, 0755, true);
        }

        $cacheFile = $cacheDir . '/detected-version.json';
        $cacheData = array_merge($result->toArray(), [
            'project_root' => $projectRoot,
        ]);
        file_put_contents($cacheFile, json_encode($cacheData, JSON_PRETTY_PRINT));
    }

    // Output result
    if ($outputJson) {
        echo json_encode(array_merge($result->toArray(), [
            'project_root' => $projectRoot,
            'config_path' => $detector->getConfigPath(),
            'template_dir' => $detector->getTemplateDir(),
        ]), JSON_PRETTY_PRINT);
    } else {
        echo $result->version ?? 'null';
    }

    return 0;
}

// Run if executed directly
if (php_sapi_name() === 'cli') {
    exit(main($argv));
}
