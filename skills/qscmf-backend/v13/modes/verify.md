---
title: Verify Mode (v13)
version: v13
impact: HIGH
when: "通过 /qscmf-verify 命令验证生成的代码质量"
---

# Verify Mode (v13)

## Trigger

```
/qscmf-verify
```

验证 scaffold 生成的代码质量。

---

## Workflow

### Level 1: PHP 语法检查

执行位置：目标项目根目录

```bash
php -l app/Admin/Controller/{Name}Controller.class.php
php -l app/Common/Model/{Name}Model.class.php
php -l app/Api/Controller/{Name}Controller.class.php
```

**预期输出**: `No syntax errors detected`

### Level 2: 类加载检查

执行位置：目标项目根目录

```bash
php -r "require 'vendor/autoload.php'; new Admin\Controller\{Name}Controller();"
php -r "require 'vendor/autoload.php'; new Common\Model\{Name}Model();"
```

**预期输出**: 无 Fatal Error

### Level 3: 继承关系验证

```bash
php -r "require 'vendor/autoload.php'; $rc = new ReflectionClass('Admin\Controller\{Name}Controller'); var_dump($rc->getParentClass()->getName());"
```

**预期输出**: `QsListController` (AdminController) 或 `RestController` (ApiController)

---

## PHPUnit 测试验证 (v13 特有)

执行位置：目标项目根目录

```bash
vendor/bin/phpunit lara/tests/Feature/{Name}Test.php --verbose
```

**预期输出**: 测试通过

---

## Report Format

```markdown
## Verification Report

### Level 1: Syntax Check
- [✅] AdminController - No syntax errors
- [✅] Model - No syntax errors
- [❌] ApiController - Syntax error on line 45

### Level 2: Class Loading
- [✅] AdminController - Class loaded successfully
- [❌] Model - Class not found: Missing dependency

### Level 3: Inheritance Check
- [✅] AdminController extends QsListController
- [✅] ApiController extends RestController
- [❌] Model does not extend GyListModel

### Level 4: PHPUnit Tests (v13)
- [✅] ProductTest - All tests passed
- [❌] OrderTest - 2 failed, 1 passed

### Summary
- Total: 5 files
- Passed: 4
- Failed: 1

### Recommended Actions
1. Fix syntax error in ApiController line 45
2. Add missing dependency to Model
3. Update Model to extend GyListModel
4. Fix failing tests in OrderTest
```

---

## Integration with Scaffold

Verify mode is automatically triggered at the end of scaffold workflow (Step 6).

See: [scaffold.md](scaffold.md)

---

## Related Rules

- [Generate Code](../rules/scaffold/scaffold-generate-code.md) - Code generation rules
- [Development Standards](../references/development-standards.md) - PHP 8.2 coding standards