<?php
namespace Lara\Tests\Feature;

use Lara\Tests\TestCase;
use Illuminate\Support\Facades\DB;

/**
 * {{MODEL_TITLE}} Test Case
 */
class {{MODEL}}Test extends TestCase
{
    protected string $table = '{{TABLE_NAME}}';

    /**
     * Test getting list
     */
    public function testGetList(): void
    {
        $response = $this->get('/api.php/{{MODEL}}/gets');

        $response->assertStatus(200)
            ->assertJson(['status' => 1])
            ->assertJsonStructure([
                'data' => [
                    'list',
                    'total',
                    'page',
                    'limit'
                ]
            ]);
    }

    /**
     * Test getting detail
     */
    public function testGetDetail(): void
    {
        // Create test data
        $id = DB::table($this->table)->insertGetId([
            // 'name' => 'Test',
            // 'status' => 1,
            // 'created_at' => now(),
            // 'updated_at' => now(),
        ]);

        $response = $this->get('/api.php/{{MODEL}}/detail?id=' . $id);

        $response->assertStatus(200)
            ->assertJson(['status' => 1]);

        // Cleanup
        DB::table($this->table)->delete($id);
    }

    /**
     * Test creating record
     */
    public function testCreate(): void
    {
        $data = [
            // 'name' => 'Test Record',
            // 'status' => 1,
        ];

        $response = $this->post('/api.php/{{MODEL}}/save', $data);

        $response->assertStatus(200)
            ->assertJson(['status' => 1])
            ->assertJsonStructure([
                'data' => ['id']
            ]);

        // Cleanup
        $result = json_decode($response->getContent(), true);
        if (isset($result['data']['id'])) {
            DB::table($this->table)->delete($result['data']['id']);
        }
    }

    /**
     * Test updating record
     */
    public function testUpdate(): void
    {
        // Create test data
        $id = DB::table($this->table)->insertGetId([
            // 'name' => 'Original Name',
            // 'status' => 1,
        ]);

        $updateData = [
            'id' => $id,
            // 'name' => 'Updated Name',
        ];

        $response = $this->put('/api.php/{{MODEL}}/update', $updateData);

        $response->assertStatus(200)
            ->assertJson(['status' => 1]);

        // Cleanup
        DB::table($this->table)->delete($id);
    }

    /**
     * Test deleting record
     */
    public function testDelete(): void
    {
        // Create test data
        $id = DB::table($this->table)->insertGetId([
            // 'name' => 'To Delete',
            // 'status' => 1,
        ]);

        $response = $this->delete('/api.php/{{MODEL}}/delete?id=' . $id);

        $response->assertStatus(200)
            ->assertJson(['status' => 1]);

        // Verify deletion
        $this->assertDatabaseMissing($this->table, ['id' => $id]);
    }

    /**
     * Test with mocked external service
     */
    public function testWithMockedApi(): void
    {
        // TODO: Create mock for external service
        // Example:
        // $mock = $this->createMock(ExternalService::class);
        // $mock->method('fetch')->willReturn(['success' => true]);
        // app()->instance(ExternalService::class, $mock);

        // $result = D('{{MODEL_NAME}}')->syncWithExternal();
        // $this->assertTrue($result);

        $this->assertTrue(true);
    }
}
