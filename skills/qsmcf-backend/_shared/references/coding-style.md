> This file extends [../../../rules/common/coding-style.md](../../../rules/common/coding-style.md) with PHP 8.2+ specific content for QSMCF development.

# PHP 8.2+ Coding Standards for QSMCF

This document extends the common coding style rules with PHP 8.2+ specific patterns and conventions used in QSMCF development.

## Modern PHP Features

### Type Declarations

Use strict type declarations on all methods and properties:

```php
// Good - explicit return types
public function getUserById(int $id): ?User
{
    return $this->model->find($id);
}

// Good - union types where appropriate
public function getStatus(): int|string
{
    return $this->status;
}

// Good - nullable return types
public function findUser(int $id): ?User
{
    return User::find($id);
}
```

### Property Promotions

Use constructor property promotion for simple DTOs:

```php
public function __construct(
    private string $name,
    private int $age,
    private ?string $email = null
) {}
```

### Attributes

Use PHP 8+ attributes for validation and model definitions:

```php
#[ORM\Entity]
#[Table(name: 'users')]
class User extends Model
{
    #[ORM\Id]
    #[ORM\Column(type: 'integer')]
    #[ORM\GeneratedValue]
    private int $id;

    #[ORM\Column(type: 'string', length: 100)]
    #[Required]
    #[MaxLength(100)]
    private string $name;

    #[ORM\Column(type: 'string', unique: true)]
    #[Email]
    private string $email;
}
```

### Constructor Property Promotion with Interfaces

Use promoted properties with interfaces for better type safety:

```php
interface UserRepositoryInterface
{
    public function findById(int $id): ?User;
    public function save(User $user): void;
}

class EloquentUserRepository implements UserRepositoryInterface
{
    public function __construct(
        private User $user,
        private LoggerInterface $logger
    ) {}

    public function findById(int $id): ?User
    {
        $this->logger->info('Finding user', ['id' => $id]);
        return $this->user->newQuery()->find($id);
    }

    public function save(User $user): void
    {
        $this->logger->info('Saving user', ['id' => $user->id]);
        $user->save();
    }
}
```

## Modern PHP Patterns

### Null Objects Pattern

Instead of null checks, use null objects:

```php
// Before
if ($user === null) {
    return 'Guest';
}
return $user->name;

// After
return $user?->name ?? 'Guest';

// Or use Null Object pattern
class NullUser extends User
{
    public function getName(): string
    {
        return 'Guest';
    }
    
    public function getEmail(): string
    {
        return '';
    }
}
```

### Builder Pattern

Use builder pattern for complex objects:

```php
class UserBuilder
{
    private string $name = '';
    private string $email = '';
    private int $age = 0;
    private array $roles = [];

    public function setName(string $name): self
    {
        $this->name = $name;
        return $this;
    }

    public function setEmail(string $email): self
    {
        $this->email = $email;
        return $this;
    }

    public function setAge(int $age): self
    {
        $this->age = $age;
        return $this;
    }

    public function setRoles(array $roles): self
    {
        $this->roles = $roles;
        return $this;
    }

    public function build(): User
    {
        return new User(
            name: $this->name,
            email: $this->email,
            age: $this->age,
            roles: $this->roles
        );
    }
}
```

### Enumerations

Use enums for status and types:

```php
enum UserStatus: string
{
    case ACTIVE = 'active';
    case INACTIVE = 'inactive';
    case SUSPENDED = 'suspended';

    public function label(): string
    {
        return match($this) {
            self::ACTIVE => 'Active',
            self::INACTIVE => 'Inactive',
            self::SUSPENDED => 'Suspended'
        };
    }
}

enum UserRole: int
{
    case ADMIN = 1;
    case MODERATOR = 2;
    case USER = 3;

    public function canManageUsers(): bool
    {
        return match($this) {
            self::ADMIN, self::MODERATOR => true,
            self::USER => false
        };
    }
}
```

### Match Expressions

Use match expressions instead of switch:

```php
// Before
switch ($status) {
    case 'active':
        return 'Active';
    case 'inactive':
        return 'Inactive';
    case 'suspended':
        return 'Suspended';
    default:
        return 'Unknown';
}

// After
return match($status) {
    'active' => 'Active',
    'inactive' => 'Inactive',
    'suspended' => 'Suspended',
    default => 'Unknown'
};
```

### Readonly Properties

Use readonly properties for immutable data:

```php
class UserProfile
{
    public function __construct(
        public readonly int $id,
        public readonly string $name,
        public readonly string $email,
        private string $password
    ) {}

    // Cannot modify readonly properties
    public function updateEmail(string $email): self
    {
        return new self(
            id: $this->id,
            name: $this->name,
            email: $email,
            password: $this->password
        );
    }
}
```

### Str and Array Classes

Use modern string and array processing:

```php
// Use Str class
use Illuminate\Support\Str;

$name = '  John Doe  ';
$trimmed = Str::trim($name); // 'John Doe'
$camel = Str::camel('user_name'); // 'userName'
$slug = Str::slug('Hello World'); // 'hello-world'

// Use Arr class
use Illuminate\Support\Arr;

$data = [
    'user' => [
        'name' => 'John',
        'email' => 'john@example.com'
    ]
];

$email = Arr::get($data, 'user.email'); // 'john@example.com'
```

## Modern Testing Patterns

### Test Data Objects

Use DTOs for test data:

```php
final class UserDataFactory
{
    public static function make(array $overrides = []): array
    {
        return [
            'name' => $overrides['name'] ?? 'John Doe',
            'email' => $overrides['email'] ?? 'john@example.com',
            'password' => $overrides['password'] ?? 'password123',
            'status' => $overrides['status'] ?? 'active'
        ];
    }

    public static function makeMany(int $count, array $overrides = []): array
    {
        return array_map(
            fn() => self::make($overrides),
            range(1, $count)
        );
    }
}

// Usage
$userData = UserDataFactory::make(['name' => 'Jane Doe']);
$users = UserDataFactory::makeMany(5, ['status' => 'inactive']);
```

### Mocking with PHPUnit 9+

Use modern mocking syntax:

```php
use PHPUnit\Framework\MockObject\MockObject;

class UserControllerTest extends TestCase
{
    private UserRepositoryInterface|MockObject $userRepository;

    protected function setUp(): void
    {
        parent::setUp();
        $this->userRepository = $this->createMock(UserRepositoryInterface::class);
    }

    public function test_get_user(): void
    {
        $this->userRepository
            ->expects($this->once())
            ->method('findById')
            ->with(1)
            ->willReturn(new User(['id' => 1, 'name' => 'John']));

        $controller = new UserController($this->userRepository);
        $user = $controller->getUser(1);

        $this->assertSame('John', $user->name);
    }
}
```

### PestPHP Features

If using PestPHP:

```php
// Use Pest's expect syntax
test('user can be created', function () {
    $user = User::factory()->create();
    
    expect($user)->toBeInstanceOf(User::class)
        ->and($user->name)->toBeString();
});

// Use Pest's hooks
beforeEach(function () {
    $this->user = User::factory()->create();
});

// Use Pest's dataset
dataset('user statuses', ['active', 'inactive', 'suspended']);

test('user has valid status', fn ($status) => {
    $user = User::factory()->create(['status' => $status]);
    
    expect($user->status)->toBe($status);
});
```

## Performance Patterns

### Use Enum for Status Fields

```php
// Before
class User extends Model
{
    const STATUS_ACTIVE = 1;
    const STATUS_INACTIVE = 0;
    
    public function getStatusAttribute(): string
    {
        return $this->attributes['status'] == self::STATUS_ACTIVE ? 'active' : 'inactive';
    }
}

// After
enum UserStatus: int
{
    case ACTIVE = 1;
    case INACTIVE = 0;
    
    public function label(): string
    {
        return $this->name;
    }
}

class User extends Model
{
    protected $casts = [
        'status' => UserStatus::class
    ];
}
```

### Use Enum for Role-Based Access

```php
enum Role: string
{
    case ADMIN = 'admin';
    case EDITOR = 'editor';
    case VIEWER = 'viewer';
    
    public function hasPermission(string $permission): bool
    {
        $permissions = match($this) {
            self::ADMIN => ['create', 'read', 'update', 'delete'],
            self::EDITOR => ['read', 'update'],
            self::VIEWER => ['read']
        };
        
        return in_array($permission, $permissions);
    }
}

// Usage
if (auth()->user()->role->hasPermission('update')) {
    // Allow update
}
```

## Security Patterns

### Use Hash::make with Strong Hashing

```php
// Good - using default Laravel hashing
public function setPasswordAttribute(string $value): void
{
    $this->attributes['password'] = Hash::make($value);
}

// Good - explicit cost for important passwords
public function setImportantPasswordAttribute(string $value): void
{
    $this->attributes['important_password'] = Hash::make($value, [
        'rounds' => 12
    ]);
}
```

### Use Str::random for Tokens

```php
// Generate secure random tokens
$token = Str::random(60); // 60 character random string
$uuid = Str::uuid()->toString(); // UUID v4

// For API tokens
$token = Str::random(32);
$hashedToken = Hash::make($token);

// Store hashed token in database
```

## Common Anti-Patterns to Avoid

### 1. Avoid Deep Nesting

```php
// Bad - deep nesting
if ($user) {
    if ($user->active) {
        if ($user->hasPermission('view')) {
            // Do something
        }
    }
}

// Good - early returns
if (!$user || !$user->active || !$user->hasPermission('view')) {
    return;
}

// Do something
```

### 2. Avoid Passing Multiple Parameters

```php
// Bad
processUser($name, $email, $age, $status, $role);

// Good
$user = new UserDTO(name: $name, email: $email, age: $age, status: $status, role: $role);
processUser($user);
```

### 3. Avoid Static Dependencies

```php
// Bad
class UserController extends Controller
{
    public function store(Request $request)
    {
        User::create($request->all());
    }
}

// Good
class UserController extends Controller
{
    public function __construct(
        private UserService $userService
    ) {}
    
    public function store(Request $request)
    {
        $this->userService->create($request->all());
    }
}
```

### 4. Avoid God Objects

```php
// Bad - User does everything
class User extends Model
{
    public function canCreatePost(): bool
    {
        return $this->role === 'admin' || $this->role === 'editor';
    }
    
    public function canEditPost(Post $post): bool
    {
        return $this->role === 'admin' || $post->user_id === $this->id;
    }
    
    public function canDeletePost(Post $post): bool
    {
        return $this->role === 'admin';
    }
}

// Good - Separate permissions
class User extends Model
{
    public function can(string $action, ?Model $subject = null): bool
    {
        $permission = new Permission($this, $action, $subject);
        return $permission->check();
    }
}
```
