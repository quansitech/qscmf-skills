# AntdAdmin Component Library Reference Documentation

This folder contains detailed reference documentation for AntdAdmin components.

## 🧭 Quick Navigation

### By Component

**Working with Table?**
- [Table Patterns](patterns.md#table-patterns) - Search, CRUD actions, inline editing
- [Table API](api-reference.md#table-api) - Methods and configuration
- [Table Troubleshooting](troubleshooting.md#table-issues) - Common issues

**Working with Form?**
- [Form Patterns](patterns.md#form-patterns) - Validation, upload, dependencies
- [Form API](api-reference.md#form-api) - Methods and configuration
- [Form Troubleshooting](troubleshooting.md#form-issues) - Common issues

**Working with Modal?**
- [Modal Patterns](patterns.md#modal-patterns) - Form modal, URL modal
- [Modal API](api-reference.md#modal-api) - Configuration

**Working with Tabs?**
- [Tabs Patterns](patterns.md#tabs-patterns) - Basic tabs, lazy load, mixed content
- [Tabs API](api-reference.md#tabs-api) - Tab configuration

**Need Column Types?**
- [Column Types Reference](column-types.md) - All 20+ column types

**Something not working?**
- [Troubleshooting Guide](troubleshooting.md) - Debug step by step

---

## 📚 Reference Documents

### [column-types.md](column-types.md)
Complete reference for all 20+ column types available in AntdAdmin.

**What you'll find**:
- Basic fields: text, textarea, digit, password
- Date & time fields: date, dateTime, dateRange, time, etc.
- Selection fields: select, radio, checkbox, switchType
- Upload fields: image, file
- Special fields: ueditor, area, cascader, money, progress, etc.

**When to use**: When you need to know which column type to use or how to configure a specific field type.

---

### [patterns.md](patterns.md)
Detailed patterns and complete examples for common use cases.

**What you'll find**:
- **Table patterns**: Search, CRUD actions, inline editing, tree tables
- **Form patterns**: Validation, image upload, dependencies, tabs
- **Modal patterns**: Form modal, URL modal, nested modals
- **Tabs patterns**: Basic tabs, lazy load, mixed content, tabs in modal, conditional tabs
- **Advanced patterns**: Permissions, batch operations, conditional rendering

**When to use**: When you need complete, working examples for implementing specific features.

---

### [api-reference.md](api-reference.md)
Complete API documentation for all AntdAdmin components.

**What you'll find**:
- **Table API**: Core methods, search, pagination, editing
- **Form API**: Core methods, submission, validation
- **Column API**: Base methods, table-only, form-only methods
- **Action API**: Shortcuts, button/link methods
- **Modal & Tabs API**: Modal and tabs configuration

**When to use**: When you need to look up specific method signatures or parameters.

---

### [troubleshooting.md](troubleshooting.md)
Comprehensive troubleshooting guide for common issues.

**What you'll find**:
- **Table issues**: Column not showing, search not working, pagination problems
- **Form issues**: Not submitting, validation, upload failing
- **Modal issues**: Not opening, content not loading
- **Action issues**: Buttons not working, batch operations
- **Performance issues**: Slow loading, N+1 queries
- **Security issues**: XSS vulnerability, file upload security

**When to use**: When something isn't working and you need step-by-step debugging guidance.

---

## 📖 How These Docs Work with SKILL.md

- **SKILL.md** contains quick start examples and key concepts
- **This folder** contains detailed, comprehensive documentation
- Links from SKILL.md point to specific sections here
- Use SKILL.md for quick reference, come here for deep dives

**Navigation tip**: Use the "By Component" section above to quickly find what you need for a specific component.

---

## 🎯 Common Tasks

| I want to... | Go to |
|-------------|-------|
| Add search to table | [Table Patterns → Basic Table with Search](patterns.md#1-basic-table-with-search) |
| Upload images in form | [Form Patterns → Image Upload](patterns.md#2-form-with-image-upload) |
| Create modal popup | [Modal Patterns](patterns.md#modal-patterns) |
| Build tabbed interface | [Tabs Patterns](patterns.md#tabs-patterns) |
| Choose column type | [Column Types → Quick Reference Table](column-types.md#quick-reference-table) |
| Look up API method | [API Reference](api-reference.md) |
| Debug an issue | [Troubleshooting](troubleshooting.md) |

---

## 🔗 Related Resources

- **Official Documentation**: `/mnt/www/antd-admin/doc/` (original project docs)
- **Source Code**: `/mnt/www/antd-admin/src/Component/` (component implementation)
- **Examples**: Look in your QSCMF project's `app/Admin/Controller/` directory

---

## 💡 Contributing

Found an error or have a suggestion? These docs are part of the qscmf-antd-admin skill. Submit improvements to the skill repository.
