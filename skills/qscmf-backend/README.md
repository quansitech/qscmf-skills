# QSCMF Backend Skill

Code generation and development guide for [QSCMF](https://github.com/baijunyao/thinkphp-bjy) framework (ThinkPHP 3.2 + Laravel hybrid).

## Quick Start

### Scaffold Mode (Code Generation)

```markdown
"创建 Product 模块，需要后台 CRUD 和 API"
"生成 User CRUD"
"QSCMF scaffold Article"
```

### Guide Mode (Development Q&A)

```markdown
"如何实现 QsListController CRUD?"
"AntdAdmin Table 组件如何使用?"
"如何编写 PHPUnit 测试?"
```

## What It Does

- **Detects QSCMF projects**: `app/` + `lara/` directories, Gy_Library, AntdAdmin
- **Generates CRUD modules**: Model, AdminController, ApiController, Migration, Tests
- **Answers QSCMF questions**: Admin UI, RESTful API, Testing, Models

## Output Structure

```
Model:          app/Common/Model/{{MODEL}}Model.class.php
AdminController: app/Admin/Controller/{{MODEL}}Controller.class.php
ApiController:  app/Api/Controller/{{MODEL}}Controller.class.php
Migration:      lara/database/migrations/xxxx_create_{{table}}_table.php
Test:           lara/tests/Feature/{{MODEL}}Test.php
```

## Documentation

See [SKILL.md](./SKILL.md) for complete workflow:
- Scaffold Mode (6-step generation process)
- Framework Guide (code patterns, architecture)
- Reference guides in `references/`

## Core Components

| Component | Base Class |
|-----------|-----------|
| Admin CRUD | `QsListController` |
| RESTful API | `RestController` |
| Model | `GyListModel` |
