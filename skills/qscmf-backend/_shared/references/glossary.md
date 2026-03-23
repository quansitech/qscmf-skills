# Glossary of QSCMF Terms

This glossary defines key terms and concepts used throughout the QSCMF framework and documentation.

## Core Concepts

### QSCMF (QuickStart Content Management Framework)
A hybrid PHP framework combining ThinkPHP 3.2 (legacy layer) and Laravel (modern tooling) for rapid application development.

### Version Detection
QSCMF version is detected from `composer.json` by reading `tiderjian/think-core` version constraint. See the root SKILL.md for current version mapping.

### Rendering Modes
- **jQuery Mode**: Traditional rendering using jQuery + Bootstrap (legacy)
- **React Mode**: Modern rendering using React + Ant Design with Inertia.js

### Base Classes
- **GyListModel**: Base model class with CRUD methods, validation, and caching
- **QsListController**: Base admin controller for CRUD operations with AntdAdmin
- **RestController**: Base API controller for RESTful endpoints
- **ListBuilder**: Dynamic list building component for admin tables

## Database Terms

### DBCont (Database Constants)
Constants for common status values:
- `DBCont::NORMAL_STATUS` = 1 (enabled/active)
- `DBCont::FORBIDDEN_STATUS` = 0 (disabled/inactive)
- `DBCont::AUDIT_STATUS` = 2 (pending review)

### DBCont 常量模式 (Magic Static Pattern)
DBCont 使用魔术函数 `__callStatic` 实现常量映射系统，只需定义常量和私有数组即可自动获得 getter 方法。

#### 核心设计
```php
class DBCont {
    // 常量定义 - 使用语义化的名称和值
    public const ENUM_TYPE_A = 'type_a';
    public const ENUM_TYPE_B = 'type_b';
    public const ENUM_TYPE_C = 'type_c';

    // 私有数组映射 - 将常量值映射为可读文本
    static private array $_enum_type = [
        self::ENUM_TYPE_A => 'Type A',
        self::ENUM_TYPE_B => 'Type B',
        self::ENUM_TYPE_C => 'Type C',
    ];

    // 魔术方法自动生成 getter
    static public function __callStatic($name, $arguments)
    {
        // 自动解析 getXXXList() 和 getXXX() 格式的方法
        // 例如：getEnumTypeList() -> $_enum_type
        //       getEnumType('type_a') -> $_enum_type['type_a']
    }
}
```

#### 自动生成的方法
```php
// 获取完整枚举列表
DBCont::getEnumTypeList();
// 返回: ['type_a' => 'Type A', 'type_b' => 'Type B', 'type_c' => 'Type C']

// 获取单个枚举值
DBCont::getEnumType('type_a');
// 返回: 'Type A'
```

#### 优势
1. **类型安全**：使用常量避免字符串拼写错误
2. **易于维护**：只需定义常量和映射数组，方法自动生成
3. **一致性**：所有枚举遵循相同的命名和调用方式
4. **减少重复**：避免为每个枚举写重复的 getter 方法

#### 命名规范
- 常量：`UPPER_SNAKE_CASE` + 语义化前缀（如 `ENUM_TYPE_`）
- 私有数组：`$_` + `lower_case` 名称
- 方法：自动生成 `getXXXList()` 和 `getXXX()`

### Migration Metadata
System for storing and using table schema information for code generation:
- Field types and validation rules
- Relationship definitions
- Form and list configurations

### ULID
Universally Unique Lexicographically Sortable Identifier

## Frontend Terms

### AntdAdmin
Admin UI framework based on Ant Design. Rendering mode depends on configuration:
- jQuery Mode: Uses jQuery for DOM manipulation with Bootstrap
- React Mode: Uses React with Ant Design components

### ListBuilder API
Dynamic table building system for admin interfaces:
- Field configuration
- Sorting and filtering
- Pagination
- Bulk actions

### FormBuilder API
Form generation system:
- Dynamic form fields
- Validation rules
- File uploads
- Image handling

### Inertia.js
Modern framework for building SPAs without full JavaScript:
- Server-side rendering
- Client-side navigation
- No API required

## Backend Terms

### Repository Pattern
Layer for data access:
- Separates business logic from data access
- Provides clean interface
- Easier to test and maintain

### Service Layer
Business logic layer:
- Coordinates between repositories
- Handles business rules
- Manages transactions

### Dependency Injection
Design pattern for managing dependencies:
- Constructor injection
- Interface-based contracts
- Decoupled components

### Queue Jobs
Asynchronous task processing:
- Background jobs
- Email sending
- File processing
- Bulk operations

### Redis Lock
Mechanism for distributed locking:
- Prevents race conditions
- Ensures exclusive access
- Timeout handling

### Wall Class
Mocking pattern for external services:
- Interface-based mocks
- Configurable behavior
- Easy testing

## Testing Terms

### TDD (Test-Driven Development)
Development methodology:
- Write tests first (RED)
- Write minimal code (GREEN)
- Refactor (IMPROVE)

### PHPUnit
Unit testing framework for PHP:
- Assertion methods
- Test fixtures
- Mock objects
- Version depends on QSCMF version

### Feature Tests
Integration testing:
- HTTP requests
- Database interactions
- User flows

### Unit Tests
Testing individual units:
- Isolated components
- Fast execution
- Clear assertions

## Development Patterns

### CRUD Operations
Basic data operations:
- Create
- Read
- Update
- Delete

### RESTful API
API design pattern:
- HTTP methods
- Resource URLs
- HTTP status codes
- JSON responses

### Batch Actions
Operations on multiple records:
- Activate/deactivate
- Delete
- Export
- Custom actions

### Field Type Inference
Automatic field type detection:
- Database type mapping
- Configuration layer
- Learning layer
- Default patterns

### Code Generation
Automated code creation:
- From database schema
- Templates
- Consistent structure
- Best practices

## Configuration Terms

### .env
Environment configuration file:
- Database settings
- API keys
- Debug settings
- Feature flags

### composer.json
PHP dependency management:
- Project dependencies
- Autoload configuration
- Scripts
- Version constraints

### artisan
Laravel command-line tool:
- Code generation
- Database migrations
- Queue workers
- Cache management

### Blade Templating
Laravel's templating engine:
- Template inheritance
- Includes
- Directives
- Component tags

## Performance Terms

### Caching
Data storage optimization:
- Query caching
- Fragment caching
- Full page caching
- Redis caching

### Pagination
Data chunking:
- Limit-offset
- Cursor-based
- Memory efficient
- Infinite scroll

### Indexes
Database optimization:
- Primary keys
- Foreign keys
- Composite indexes
- Full-text search

### Eager Loading
Database optimization:
- Prevent N+1 queries
- Load relationships upfront
- Memory efficient
- Performance boost

## Security Terms

### JWT (JSON Web Token)
Authentication method:
- Stateless
- Secure
- Expiration
- Refresh tokens

### CSRF Protection
Cross-Site Request Forgery protection:
- Tokens
- Headers
- Validation
- Secure by default

### Input Validation
Data sanitization:
- Rules
- Filters
- Sanitization
- Error messages

### Rate Limiting
API protection:
- Request limits
- Time windows
- IP-based
- User-based

## Deployment Terms

### Environment
Deployment context:
- Local development
- Testing
- Staging
- Production

### Version Control
Code management:
- Git
- Branching
- Merging
- Tags

### CI/CD
Continuous Integration/Deployment:
- Automated testing
- Deployment pipelines
- Environment management
- Monitoring

### Monitoring
Application health:
- Logging
- Error tracking
- Performance metrics
- User analytics
