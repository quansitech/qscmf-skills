# Mock External APIs (Wall Pattern)

## Mock Wall Classes

When testing controllers that call external APIs, mock the Wall class:

```php
namespace Tests\Feature;
use Tests\TestCase;
use Common\Wall\ExternalServiceWall;

class ProductControllerTest extends TestCase
{
    public function testSyncWithExternalSuccess()
    {
        // Create mock
        $mockWall = $this->createMock(ExternalServiceWall::class);

        // Configure mock behavior
        $mockWall->method('fetchData')
            ->with('ext-123')
            ->willReturn([
                'name' => 'External Product',
                'price' => 100.00,
                'stock' => 50
            ]);

        // Inject mock into container
        $this->app->instance(ExternalServiceWall::class, $mockWall);

        // Test controller action
        $controller = new \Admin\Controller\ProductController();
        $response = $controller->syncWithExternal(['id' => 1]);

        $this->assertTrue($response['success']);
    }

    public function testSyncWithExternalFailure()
    {
        $mockWall = $this->createMock(ExternalServiceWall::class);
        $mockWall->method('fetchData')
            ->willReturn(null); // API failure

        $this->app->instance(ExternalServiceWall::class, $mockWall);

        $controller = new \Admin\Controller\ProductController();

        $this->expectException(\Exception::class);
        $controller->syncWithExternal(['id' => 1]);
    }
}
```

## Mock with Data Provider

```php
/**
 * @dataProvider externalApiDataProvider
 */
public function testSyncProduct(array $externalData, array $expectedLocalData)
{
    $mockWall = $this->createMock(ExternalServiceWall::class);
    $mockWall->method('fetchData')
        ->willReturn($externalData);

    $this->app->instance(ExternalServiceWall::class, $mockWall);

    $controller = new \Admin\Controller\ProductController();
    $controller->syncWithExternal(['id' => 1]);

    // Verify database update
    $product = D('Product')->find(1);
    foreach ($expectedLocalData as $key => $value) {
        $this->assertEquals($value, $product[$key]);
    }
}

public static function externalApiDataProvider(): array
{
    return [
        'Full data' => [
            [
                'name' => 'Product A',
                'price' => 100,
                'stock' => 50
            ],
            [
                'name' => 'Product A',
                'price' => 100,
                'stock' => 50
            ]
        ],
        'Partial data' => [
            [
                'name' => 'Product B',
                'price' => 200
            ],
            [
                'name' => 'Product B',
                'price' => 200,
                'stock' => 0 // Default value
            ]
        ]
    ];
}
```

## Mock with PHPUnit Prophecy

```php
use PHPUnit\Framework\MockObject\MockObject;

public function testSyncWithRetry()
{
    /** @var ExternalServiceWall|MockObject $mockWall */
    $mockWall = $this->createMock(ExternalServiceWall::class);

    // First call fails, second succeeds
    $mockWall->expects($this->exactly(2))
        ->method('fetchData')
        ->willReturnOnConsecutiveCalls(
            null, // First call fails
            ['name' => 'Product', 'price' => 100] // Second succeeds
        );

    $this->app->instance(ExternalServiceWall::class, $mockWall);

    $controller = new \Admin\Controller\ProductController();
    $result = $controller->syncWithExternal(['id' => 1]);

    $this->assertTrue($result['success']);
}
```

## Test Queue Jobs with Mock

```php
public function testProcessImageJob()
{
    // Mock image processing library
    $mockImageLib = $this->createMock(\Common\Lib\ImageProcessor::class);
    $mockImageLib->expects($this->once())
        ->method('resize')
        ->with($this->equalTo('image.jpg'), 800, 600)
        ->willReturn(true);

    $this->app->instance(\Common\Lib\ImageProcessor::class, $mockImageLib);

    // Create and execute job
    $job = new \Common\Job\ProcessImageJob([
        'image_id' => 1,
        'operations' => [
            ['type' => 'resize', 'width' => 800, 'height' => 600]
        ]
    ]);

    $job->handle(new \Think\Queue\Job(), []);

    // Verify result
    $image = D('Image')->find(1);
    $this->assertEquals(1, $image['status']);
}
```

→ [Wall Class Pattern](rules/pattern/pattern-wall-class.md)
→ [Testing Guide](references/testing.md)
