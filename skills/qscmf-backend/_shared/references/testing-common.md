# Testing Common Commands

> QSCMF 通用测试命令（适用于 v13 和 v14）

## 基础命令（推荐）

关闭 xdebug 以加速测试：

```bash
# 定义基础命令
PHPUNIT="php -d display_errors=on -d xdebug.mode=off -d xdebug.start_with_request=0 vendor/bin/phpunit"
```

## 运行测试

| 场景 | 命令 |
|------|------|
| 全部测试 | `$PHPUNIT` |
| 单个测试类 | `$PHPUNIT lara/tests/Feature/ProductTest.php` |
| 单个测试方法 | `$PHPUNIT --filter "testMethodName" lara/tests/Feature/ProductTest.php` |
| 模糊匹配 | `$PHPUNIT --filter "Create"` |
| 特定测试套件 | `$PHPUNIT --testsuite Feature` |
| 详细输出 | `$PHPUNIT -v` |

## --filter 用法详解

```bash
# 精确匹配方法名
--filter "testCreate"

# 模糊匹配（包含 Create 的所有测试）
--filter "Create"

# 匹配类名
--filter "ProductTest"

# 匹配命名空间路径
--filter "Lara\\Tests\\Feature\\Product"

# 正则表达式匹配
--filter "/testCreate|testUpdate/"
```

## 其他命令

```bash
# 生成代码覆盖率报告（需要开启 xdebug）
vendor/bin/phpunit --coverage-html coverage

# 并行测试
vendor/bin/paratest

# 排除慢测试
$PHPUNIT --exclude-group slow
```

## 版本特定文档

- [v13 Testing](../v13/references/testing.md) - v13 特有测试模式（runTp wrapper 等）
- [v14 Testing](../v14/references/testing.md) - v14 特有测试模式
