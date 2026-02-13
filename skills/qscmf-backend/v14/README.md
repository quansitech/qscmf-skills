# QSCMF 后端开发技能

[QSCMF](https://github.com/quansitech/qs_cmf) 框架代码生成与开发指南。

## 快速开始

### 代码生成模式

```markdown
"创建 Product 模块，需要后台 CRUD 和 API"
"生成 User CRUD"
"QSCMF scaffold Article"
```

### 开发指南模式

```markdown
"如何实现 QsListController CRUD？"
"AntdAdmin Table 组件如何使用？"
"如何编写 PHPUnit 测试？"
```

## 功能特性

- **自动检测 QSCMF 项目**：识别 `app/` + `lara/` 目录结构、Gy_Library、AntdAdmin
- **生成 CRUD 模块**：Model、AdminController、ApiController、Migration、测试
- **解答 QSCMF 问题**：后台 UI、RESTful API、测试、模型开发

## 生成文件结构

```
Model:          app/Common/Model/{{MODEL}}Model.class.php
AdminController: app/Admin/Controller/{{MODEL}}Controller.class.php
ApiController:  app/Api/Controller/{{MODEL}}Controller.class.php
Migration:      lara/database/migrations/xxxx_create_{{table}}_table.php
Test:           lara/tests/Feature/{{MODEL}}Test.php
```

## 详细文档

查看 [SKILL.md](./SKILL.md) 了解完整工作流程：
- 代码生成模式（6 步生成流程）
- 框架开发指南（代码模式、架构）
- `references/` 目录中的参考文档

## 核心组件

| 组件 | 基类 |
|------|------|
| 后台 CRUD | `QsListController` |
| RESTful API | `RestController` |
| 模型 | `GyListModel` |
