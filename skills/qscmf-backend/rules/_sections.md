# Rules Sections

This file defines all sections, their ordering, impact levels, and descriptions.

## 1. Workflow (workflow)
**Impact:** CRITICAL
**Description:** Essential workflows for module creation and code generation.

## 2. Scaffold (scaffold)
**Impact:** CRITICAL
**Description:** Generate Model, Controller, Test code from migration metadata.

## 3. CRUD (crud)
**Impact:** HIGH
**Description:** Admin CRUD patterns, QsListController, AntdAdmin.

## 4. API (api)
**Impact:** HIGH
**Description:** RESTful API, RestController, authentication.

## 5. Test (test)
**Impact:** MEDIUM-HIGH
**Description:** PHPUnit testing, TDD, Wall class mocking.

## 6. Pattern (pattern)
**Impact:** MEDIUM
**Description:** Architectural patterns, abstract base, queue jobs.

## Version Prefixes

- `v13`: v13 specific (Legacy jQuery, PHPUnit 9)
- `v14`: v14 specific (antd-admin, PHPUnit 10)
- No prefix: Both versions compatible
