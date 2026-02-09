# QSCMF Skills

QSCMF 框架 AI 智能体开发技能集合。

## 包含的 Skills

| Skill | 描述 |
|-------|------|
| [qscmf-backend](skills/qscmf-backend/) | 后端开发 |

## 安装

1. 克隆本项目

```bash
git clone https://github.com/quansitech/qscmf-skills.git
```

2. 将具体的技能创建软链接到智能体 skills 目录

**Claude Code 默认目录**：
```bash
ln -s /path/to/qscmf-skills/skills/qscmf-backend/ /root/.claude/skills/qscmf-backend
```

**其他 AI 智能体**：根据具体配置调整目标路径

查看各 skill 目录下的 README.md 了解详细用法。

## 许可证

MIT License
