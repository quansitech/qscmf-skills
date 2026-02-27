# QSCMF Backend - Shared Components

This directory contains shared content applicable to all QSCMF versions.

> **Note**: Version detection is handled in the root [SKILL.md](../SKILL.md). Navigate there first to determine your QSCMF version.

## Directory Structure

```
_shared/
├── concepts/           # Core framework concepts
│   ├── architecture.md     - ThinkPHP + Laravel hybrid structure
│   └── core-concepts.md    - ListBuilder API, AntdAdmin Component API, GyListModel, DBCont
├── references/         # Comprehensive reference guides
│   ├── api-controllers.md  - RESTful API patterns
│   ├── model-guide.md      - GyListModel patterns
│   ├── development-standards.md - PHP 8.2+ coding standards
│   ├── migration-metadata.md - Metadata system for code generation
│   ├── abstract-base-patterns.md - Reusable base class patterns
│   └── glossary.md         - Common terms and definitions
└── learn/              - Learning system for knowledge capture
    ├── workflow.md         - Learning workflow details
    └── deep-scan-impl.md   - Deep scan implementation
```

## Key Reference Documentation

### API Development
- **[api-controllers.md](references/api-controllers.md)** - RESTful API patterns with RestController

### Data Layer
- **[model-guide.md](references/model-guide.md)** - GyListModel patterns, validation, query methods
- **[migration-metadata.md](references/migration-metadata.md)** - Enhanced metadata system for code generation

### Development Standards
- **[development-standards.md](references/development-standards.md)** - PHP 8.2+ coding standards
- **[abstract-base-patterns.md](references/abstract-base-patterns.md)** - Reusable base class patterns

### Framework Concepts
- **[architecture.md](concepts/architecture.md)** - ThinkPHP + Laravel hybrid structure
- **[core-concepts.md](concepts/core-concepts.md)** - Core framework components

### Terminology
- **[glossary.md](references/glossary.md)** - Common terms and definitions

## Learning System

After a QSCMF development session, use `/qscmf-learn` to capture learnings:

- **[workflow.md](learn/workflow.md)** - Complete learning workflow
- **[deep-scan-impl.md](learn/deep-scan-impl.md)** - Deep scan implementation details

## Getting Started

1. Check the root [SKILL.md](../SKILL.md) for version detection
2. Navigate to your version-specific SKILL.md (v13/ or v14/)
3. Use shared references for cross-version concepts
