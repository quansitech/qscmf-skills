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
