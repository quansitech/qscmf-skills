> This file extends common patterns with QSMCF-specific abstract base class patterns.

# Abstract Base Class Patterns for QSMCF

This document provides comprehensive patterns for implementing abstract base classes in QSMCF, promoting code reusability and consistency across your application.

## Abstract Base Controllers

### Base Admin Controller

```php
namespace App\Common\Controllers\Admin;

use App\Common\Controllers\QsListController;
use Illuminate\Database\Eloquent\Builder;
use Illuminate\Http\Request;

abstract class BaseAdminController extends QsListController
{
    /**
     * The model class this controller handles.
     */
    protected abstract function getModelClass(): string;
    
    /**
     * Get the list fields configuration.
     */
    protected abstract function getListFields(): array;
    
    /**
     * Get the form fields configuration.
     */
    protected abstract function getFormFields(): array;
    
    /**
     * Customize the query for listing.
     */
    protected function customizeQuery(Builder $query): Builder
    {
        return $query;
    }
    
    /**
     * Get the base search fields.
     */
    protected function getSearchFields(): array
    {
        return [];
    }
    
    /**
     * Get the base filter fields.
     */
    protected function getFilterFields(): array
    {
        return [];
    }
    
    /**
     * Get the default order.
     */
    protected function getDefaultOrder(): array
    {
        return ['created_at' => 'desc'];
    }
    
    /**
     * Check if user has permission for the action.
     */
    protected function checkPermission(string $action): bool
    {
        $user = auth()->user();
        $permission = $this->getPermissionName($action);
        
        return $user->can($permission) || $user->isAdmin();
    }
    
    /**
     * Get permission name for the action.
     */
    protected function getPermissionName(string $action): string
    {
        $modelClass = class_basename($this->getModelClass());
        return strtolower("{$action}-{$modelClass}");
    }
    
    /**
     * Handle unauthorized access.
     */
    protected function unauthorized(): \Illuminate\Http\JsonResponse
    {
        return response()->json([
            'success' => false,
            'message' => 'Unauthorized access'
        ], 403);
    }
    
    /**
     * Apply common query modifications.
     */
    protected function applyCommonFilters(Builder $query, Request $request): Builder
    {
        // Apply search
        if ($request->has('search') && !empty($request->search)) {
            $search = $request->search;
            $query->where(function($q) use ($search) {
                foreach ($this->getSearchFields() as $field) {
                    $q->orWhere($field, 'like', "%{$search}%");
                }
            });
        }
        
        // Apply filters
        foreach ($this->getFilterFields() as $field => $value) {
            if ($request->has($field) && $value !== null) {
                $query->where($field, $request->input($field));
            }
        }
        
        // Apply sorting
        if ($request->has('sortField') && $request->has('sortOrder')) {
            $query->orderBy($request->sortField, $request->sortOrder);
        } else {
            $defaultOrder = $this->getDefaultOrder();
            $query->orderBy(key($defaultOrder), current($defaultOrder));
        }
        
        return $query;
    }
}
```

### Abstract API Controller

```php
namespace App\Common\Controllers\Api;

use App\Common\Controllers\RestController;
use Illuminate\Http\Request;
use Illuminate\Database\Eloquent\Builder;
use Illuminate\Support\Facades\DB;

abstract class BaseApiController extends RestController
{
    /**
     * The model class this controller handles.
     */
    protected abstract function getModelClass(): string;
    
    /**
     * The resource class for API responses.
     */
    protected abstract function getResourceClass(): string;
    
    /**
     * Get relationships to eager load.
     */
    protected function getRelationships(): array
    {
        return [];
    }
    
    /**
     * Get appends for the model.
     */
    protected function getAppends(): array
    {
        return [];
    }
    
    /**
     * Customize the listing query.
     */
    protected function listQuery(): Builder
    {
        $query = $this->getModelClass()::query();
        
        // Eager load relationships
        if ($this->getRelationships()) {
            $query->with($this->getRelationships());
        }
        
        return $query;
    }
    
    /**
     * Apply search functionality.
     */
    protected function applySearch(Builder $query, string $search): Builder
    {
        // Override this method to implement custom search logic
        return $query;
    }
    
    /**
     * Apply filters.
     */
    protected function applyFilters(Builder $query, array $filters): Builder
    {
        // Override this method to implement custom filtering
        return $query;
    }
    
    /**
     * Apply sorting.
     */
    protected function applySorting(Builder $query, string $field, string $direction): Builder
    {
        return $query->orderBy($field, $direction);
    }
    
    /**
     * Handle bulk actions.
     */
    protected function handleBulkAction(Request $request, string $action): mixed
    {
        $ids = $request->input('ids', []);
        
        switch ($action) {
            case 'delete':
                return $this->getModelClass()::whereIn('id', $ids)->delete();
                
            case 'activate':
                return $this->getModelClass()::whereIn('id', $ids)->update(['status' => 'active']);
                
            case 'deactivate':
                return $this->getModelClass()::whereIn('id', $ids)->update(['status' => 'inactive']);
                
            default:
                throw new \InvalidArgumentException("Unknown bulk action: {$action}");
        }
    }
    
    /**
     * Get the success response message.
     */
    protected function getSuccessMessage(string $action, string $resource = null): string
    {
        $resource = $resource ?: strtolower(class_basename($this->getModelClass()));
        
        return match($action) {
            'create' => ucfirst($resource) . ' created successfully',
            'update' => ucfirst($resource) . ' updated successfully',
            'delete' => ucfirst($resource) . ' deleted successfully',
            default => ucfirst($action) . ' completed successfully'
        };
    }
    
    /**
     * Wrap response in resource collection.
     */
    protected function wrapResources($data)
    {
        $resourceClass = $this->getResourceClass();
        
        if ($data instanceof \Illuminate\Pagination\LengthAwarePaginator) {
            return $resourceClass::collection($data);
        }
        
        return $resourceClass::collection($data->collect());
    }
    
    /**
     * Standard index response.
     */
    public function index(Request $request)
    {
        $query = $this->listQuery();
        
        // Apply search
        if ($request->has('search')) {
            $query = $this->applySearch($query, $request->search);
        }
        
        // Apply filters
        if ($request->has('filters')) {
            $query = $this->applyFilters($query, $request->filters);
        }
        
        // Apply sorting
        if ($request->has('sortField') && $request->has('sortOrder')) {
            $query = $this->applySorting($query, $request->sortField, $request->sortOrder);
        }
        
        // Paginate
        $perPage = $request->input('per_page', 15);
        $data = $query->paginate($perPage);
        
        return $this->successResponse($this->wrapResources($data));
    }
    
    /**
     * Standard store method with transaction.
     */
    public function store(Request $request)
    {
        DB::beginTransaction();
        
        try {
            $model = $this->getModelClass()::create($request->validated());
            DB::commit();
            
            return $this->successResponse(
                $this->wrapResources(collect([$model])),
                $this->getSuccessMessage('create')
            );
            
        } catch (\Exception $e) {
            DB::rollBack();
            
            return $this->errorResponse(
                'Failed to create resource: ' . $e->getMessage(),
                500
            );
        }
    }
}
```

### Abstract Base Model

```php
namespace App\Common\Models;

use Gy_Library\GyListModel;
use Illuminate\Database\Eloquent\Builder;
use Illuminate\Support\Facades\Cache;
use Illuminate\Support\Facades\Log;

abstract class BaseModel extends GyListModel
{
    /**
     * The connection name for the model.
     */
    protected $connection = 'mysql';
    
    /**
     * Whether the model should use timestamp.
     */
    public $timestamps = true;
    
    /**
     * The attributes that are mass assignable.
     */
    protected $fillable = [];
    
    /**
     * The attributes that should be cast.
     */
    protected $casts = [];
    
    /**
     * Default attributes.
     */
    protected $attributes = [];
    
    /**
     * Cache tags for the model.
     */
    protected $cacheTags = [];
    
    /**
     * Cache TTL in seconds.
     */
    protected $cacheTTL = 3600;
    
    /**
     * Boot the model.
     */
    protected static function boot()
    {
        parent::boot();
        
        static::creating(function ($model) {
            if (method_exists($model, 'beforeCreate')) {
                $model->beforeCreate();
            }
        });
        
        static::created(function ($model) {
            if (method_exists($model, 'afterCreate')) {
                $model->afterCreate();
            }
        });
        
        static::updating(function ($model) {
            if (method_exists($model, 'beforeUpdate')) {
                $model->beforeUpdate();
            }
        });
        
        static::updated(function ($model) {
            if (method_exists($model, 'afterUpdate')) {
                $model->afterUpdate();
            }
        });
        
        static::deleting(function ($model) {
            if (method_exists($model, 'beforeDelete')) {
                $model->beforeDelete();
            }
        });
        
        static::deleted(function ($model) {
            if (method_exists($model, 'afterDelete')) {
                $model->afterDelete();
            }
        });
    }
    
    /**
     * Get the model's cache key.
     */
    public function getCacheKey(): string
    {
        return $this->getTable() . ':' . $this->getKey();
    }
    
    /**
     * Clear model cache.
     */
    public function clearCache(): void
    {
        if ($this->cacheTags) {
            Cache::tags($this->cacheTags)->flush();
        }
        
        Cache::forget($this->getCacheKey());
    }
    
    /**
     * Create a new model instance with default attributes.
     */
    public static function create(array $attributes = []): static
    {
        $model = new static;
        
        // Merge with default attributes
        $attributes = array_merge($model->attributes, $attributes);
        
        return parent::create($attributes);
    }
    
    /**
     * Scope for active records.
     */
    public function scopeActive(Builder $query): Builder
    {
        return $query->where('status', 'active');
    }
    
    /**
     * Scope for inactive records.
     */
    public function scopeInactive(Builder $query): Builder
    {
        return $query->where('status', 'inactive');
    }
    
    /**
     * Scope for deleted records.
     */
    public function scopeOnlyTrashed(Builder $query): Builder
    {
        return $query->onlyTrashed();
    }
    
    /**
     * Scope for records within date range.
     */
    public function scopeBetweenDates(Builder $query, string $field, string $start, string $end): Builder
    {
        return $query->whereBetween($field, [$start, $end]);
    }
    
    /**
     * Scope for records with specified status.
     */
    public function scopeWhereStatus(Builder $query, string $status): Builder
    {
        return $query->where('status', $status);
    }
    
    /**
     * Get formatted created_at.
     */
    public function getFormattedCreatedAtAttribute(): string
    {
        return $this->created_at->format('Y-m-d H:i:s');
    }
    
    /**
     * Get formatted updated_at.
     */
    public function getFormattedUpdatedAtAttribute(): string
    {
        return $this->updated_at->format('Y-m-d H:i:s');
    }
    
    /**
     * Check if model is active.
     */
    public function isActive(): bool
    {
        return $this->status === 'active';
    }
    
    /**
     * Check if model is inactive.
     */
    public function isInactive(): bool
    {
        return $this->status === 'inactive';
    }
    
    /**
     * Get model's age in days.
     */
    public function getAgeInDays(): int
    {
        return now()->diffInDays($this->created_at);
    }
    
    /**
     * Log model event.
     */
    protected function logEvent(string $event, array $data = []): void
    {
        Log::info("Model {$event}", [
            'model' => static::class,
            'id' => $this->id,
            'user_id' => auth()->id(),
            'data' => $data
        ]);
    }
}
```

## Abstract ListBuilder Classes

### Base ListBuilder

```php
namespace App\Common\ListBuilder;

use App\Common\Controllers\BaseAdminController;
use Illuminate\Database\Eloquent\Builder;
use Illuminate\Http\Request;

abstract class BaseListBuilder
{
    /**
     * The admin controller instance.
     */
    protected BaseAdminController $controller;
    
    /**
     * The request instance.
     */
    protected Request $request;
    
    /**
     * The query builder instance.
     */
    protected Builder $query;
    
    public function __construct(BaseAdminController $controller, Request $request)
    {
        $this->controller = $controller;
        $this->request = $request;
        $this->query = $this->controller->getModelClass()::query();
    }
    
    /**
     * Get the list fields configuration.
     */
    abstract public function getListFields(): array;
    
    /**
     * Get the form fields configuration.
     */
    abstract public function getFormFields(): array;
    
    /**
     * Build the query for listing.
     */
    public function buildQuery(): Builder
    {
        $this->applySearch();
        $this->applyFilters();
        $this->applySorting();
        $this->applyJoins();
        $this->applyScopes();
        
        return $this->query;
    }
    
    /**
     * Apply search functionality.
     */
    protected function applySearch(): void
    {
        $search = $this->request->input('search');
        
        if ($search) {
            $searchFields = $this->getSearchFields();
            
            $this->query->where(function($q) use ($search, $searchFields) {
                foreach ($searchFields as $field) {
                    if (str_contains($field, '.')) {
                        // Relationship field
                        [$relation, $column] = explode('.', $field);
                        $q->orWhereHas($relation, function($query) use ($column, $search) {
                            $query->where($column, 'like', "%{$search}%");
                        });
                    } else {
                        // Direct field
                        $q->orWhere($field, 'like', "%{$search}%");
                    }
                }
            });
        }
    }
    
    /**
     * Apply filters.
     */
    protected function applyFilters(): void
    {
        $filters = $this->request->input('filters', []);
        
        foreach ($filters as $field => $value) {
            if ($value !== null && $value !== '') {
                $this->query->where($field, $value);
            }
        }
    }
    
    /**
     * Apply sorting.
     */
    protected function applySorting(): void
    {
        $sortField = $this->request->input('sortField');
        $sortOrder = $this->request->input('sortOrder', 'asc');
        
        if ($sortField) {
            if (str_contains($sortField, '.')) {
                // Relationship sorting
                [$relation, $column] = explode('.', $sortField);
                $this->query->join($relation . 's', $relation . '_id', '=', $relation . 's.id')
                           ->orderBy($relation . 's.' . $column, $sortOrder);
            } else {
                // Direct sorting
                $this->query->orderBy($sortField, $sortOrder);
            }
        } else {
            // Default sorting
            $defaultOrder = $this->getDefaultOrder();
            $this->query->orderBy(key($defaultOrder), current($defaultOrder));
        }
    }
    
    /**
     * Apply table joins.
     */
    protected function applyJoins(): void
    {
        $this->query->with($this->getRelationships());
    }
    
    /**
     * Apply additional scopes.
     */
    protected function applyScopes(): void
    {
        // Override in child classes to apply specific scopes
    }
    
    /**
     * Get searchable fields.
     */
    protected function getSearchFields(): array
    {
        return ['name', 'description'];
    }
    
    /**
     * Get relationships to load.
     */
    protected function getRelationships(): array
    {
        return [];
    }
    
    /**
     * Get default order.
     */
    protected function getDefaultOrder(): array
    {
        return ['created_at' => 'desc'];
    }
    
    /**
     * Get pagination settings.
     */
    protected function getPagination(): array
    {
        return [
            'perPage' => $this->request->input('per_page', 15),
            'page' => $this->request->input('page', 1)
        ];
    }
    
    /**
     * Execute the query and return results.
     */
    public function getResults(): array
    {
        $query = $this->buildQuery();
        $pagination = $this->getPagination();
        
        $results = $query->paginate($pagination['perPage'], ['*'], 'page', $pagination['page']);
        
        return [
            'data' => $results->items(),
            'total' => $results->total(),
            'per_page' => $results->perPage(),
            'current_page' => $results->currentPage(),
            'last_page' => $results->lastPage()
        ];
    }
    
    /**
     * Export data to CSV.
     */
    public function exportToCSV(): string
    {
        $query = $this->buildQuery();
        $results = $query->get();
        
        $filename = $this->controller->getModelClass() . '_export_' . date('YmdHis') . '.csv';
        
        $headers = [
            'Content-Type' => 'text/csv',
            'Content-Disposition' => "attachment; filename={$filename}"
        ];
        
        return response()->streamDownload(function () use ($results) {
            $handle = fopen('php://output', 'w');
            
            // Write header
            fputcsv($handle, array_keys($results->first()->toArray()));
            
            // Write data
            foreach ($results as $result) {
                fputcsv($handle, $result->toArray());
            }
            
            fclose($handle);
        }, $filename, $headers);
    }
}
```

### Product ListBuilder Example

```php
namespace App\Common\ListBuilder;

use App\Common\Controllers\Admin\ProductController;
use App\Common\Models\Category;
use Illuminate\Http\Request;

class ProductListBuilder extends BaseListBuilder
{
    protected function getListFields(): array
    {
        return [
            'id' => [
                'title' => 'ID',
                'width' => 80,
                'fixed' => 'left',
                'sorter' => true,
                'searchable' => false
            ],
            'name' => [
                'title' => '名称',
                'minWidth' => 120,
                'searchable' => true,
                'ellipsis' => true
            ],
            'category.name' => [
                'title' => '分类',
                'width' => 100,
                'searchable' => true,
                'filterOptions' => Category::pluck('name', 'id')->toArray()
            ],
            'price' => [
                'title' => '价格',
                'type' => 'money',
                'width' => 120,
                'sorter' => true,
                'prefix' => '¥'
            ],
            'stock' => [
                'title' => '库存',
                'width' => 100,
                'sorter' => true,
                'align' => 'right'
            ],
            'status' => [
                'title' => '状态',
                'width' => 100,
                'type' => 'select',
                'options' => [
                    'active' => '启用',
                    'inactive' => '禁用',
                    'out_of_stock' => '缺货'
                ],
                'filterOptions' => ['active', 'inactive', 'out_of_stock']
            ],
            'created_at' => [
                'title' => '创建时间',
                'width' => 160,
                'sorter' => true,
                'format' => 'YYYY-MM-DD HH:mm:ss'
            ]
        ];
    }
    
    protected function getFormFields(): array
    {
        return [
            'name' => [
                'label' => '产品名称',
                'type' => 'text',
                'rules' => 'required|string|max:255'
            ],
            'category_id' => [
                'label' => '分类',
                'type' => 'select',
                'rules' => 'required|exists:categories,id',
                'options' => Category::pluck('name', 'id')->toArray()
            ],
            'price' => [
                'label' => '价格',
                'type' => 'number',
                'rules' => 'required|numeric|min:0',
                'step' => '0.01'
            ],
            'stock' => [
                'label' => '库存',
                'type' => 'number',
                'rules' => 'required|integer|min:0'
            ],
            'status' => [
                'label' => '状态',
                'type' => 'radio',
                'rules' => 'required|string',
                'options' => [
                    'active' => '启用',
                    'inactive' => '禁用',
                    'out_of_stock' => '缺货'
                ],
                'default' => 'active'
            ]
        ];
    }
    
    protected function getSearchFields(): array
    {
        return ['name', 'description', 'category.name'];
    }
    
    protected function getRelationships(): array
    {
        return ['category'];
    }
    
    protected function applyFilters(): void
    {
        parent::applyFilters();
        
        // Custom filter for low stock products
        if ($this->request->has('low_stock') && $this->request->low_stock == '1') {
            $this->query->where('stock', '<=', 10);
        }
        
        // Custom filter for price range
        if ($this->request->has('min_price')) {
            $this->query->where('price', '>=', $this->request->min_price);
        }
        
        if ($this->request->has('max_price')) {
            $this->query->where('price', '<=', $this->request->max_price);
        }
    }
    
    protected function applySorting(): void
    {
        $sortField = $this->request->input('sortField');
        $sortOrder = $this->request->input('sortOrder', 'asc');
        
        // Custom sorting by stock status
        if ($sortField === 'stock_status') {
            $this->query->orderByRaw(
                "CASE 
                    WHEN stock = 0 THEN 0
                    WHEN stock <= 10 THEN 1
                    ELSE 2 
                END {$sortOrder}, 
                created_at DESC"
            );
        } else {
            parent::applySorting();
        }
    }
}
```

## Abstract Service Classes

### Base Service

```php
namespace App\Common\Services;

use App\Common\Repositories\BaseRepository;
use Illuminate\Database\Eloquent\Model;
use Illuminate\Support\Facades\DB;

abstract class BaseService
{
    /**
     * The repository instance.
     */
    protected BaseRepository $repository;
    
    /**
     * The model class.
     */
    protected string $modelClass;
    
    public function __construct(BaseRepository $repository)
    {
        $this->repository = $repository;
    }
    
    /**
     * Get all records.
     */
    public function all(): \Illuminate\Support\Collection
    {
        return $this->repository->all();
    }
    
    /**
     * Find record by ID.
     */
    public function find(int $id): ?Model
    {
        return $this->repository->find($id);
    }
    
    /**
     * Create a new record.
     */
    public function create(array $data): Model
    {
        return DB::transaction(function () use ($data) {
            return $this->repository->create($data);
        });
    }
    
    /**
     * Update a record.
     */
    public function update(int $id, array $data): Model
    {
        return DB::transaction(function () use ($id, $data) {
            return $this->repository->update($id, $data);
        });
    }
    
    /**
     * Delete a record.
     */
    public function delete(int $id): bool
    {
        return DB::transaction(function () use ($id) {
            return $this->repository->delete($id);
        });
    }
    
    /**
     * Paginate records.
     */
    public function paginate(int $perPage = 15, array $columns = ['*']): \Illuminate\Pagination\LengthAwarePaginator
    {
        return $this->repository->paginate($perPage, $columns);
    }
    
    /**
     * Get records with conditions.
     */
    public function where(array $conditions): \Illuminate\Support\Collection
    {
        return $this->repository->where($conditions);
    }
    
    /**
     * Get record by conditions.
     */
    public function firstWhere(array $conditions): ?Model
    {
        return $this->repository->firstWhere($conditions);
    }
    
    /**
     * Check if record exists.
     */
    public function exists(int $id): bool
    {
        return $this->repository->exists($id);
    }
    
    /**
     * Get model class.
     */
    public function getModelClass(): string
    {
        return $this->modelClass;
    }
}
```

## Best Practices

### 1. Consistent Naming Conventions

- Use descriptive names for abstract classes
- Follow PSR-12 naming standards
- Prefix abstract classes with `Abstract` or `Base`

### 2. Proper Inheritance Hierarchy

```
BaseAdminController (abstract)
    ↓
CategoryAdminController
    ↓
ProductAdminController

BaseApiController (abstract)
    ↓
CategoryApiController
    ↓
ProductApiController
```

### 3. Template Method Pattern

Use template methods to define the skeleton of algorithms while letting subclasses override specific steps.

### 4. Dependency Injection

Inject dependencies through constructor injection for better testability.

### 5. Interface Segregation

Create specific interfaces for different functionalities rather than one large interface.

### 6. Single Responsibility

Each abstract class should have a single, well-defined responsibility.

### 7. Open/Closed Principle

Design classes to be open for extension but closed for modification.

### 8. Liskov Substitution

Subclasses should be substitutable for their base classes.

### 9. Interface Segregation

Clients should not be forced to depend on interfaces they don't use.

### 10. Dependency Inversion

Depend on abstractions, not concretions.
