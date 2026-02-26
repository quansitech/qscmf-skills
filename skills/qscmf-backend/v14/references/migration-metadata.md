# Migration Metadata

Code generation hints in migration comments.

## Format

```php
$table->string('cover_id')->comment('封面图 @type=image @crop=16/9');
$table->text('content')->comment('内容 @type=ueditor');
$table->tinyInteger('status')->comment('状态 @type=select @options=DBCont::getStatusList()');
```

## Supported Tags

| Tag | Description |
|-----|-------------|
| `@type` | Field type |
| `@title` | Field label |
| `@crop` | Image crop ratio |
| `@options` | Options source |
| `@required` | Required field |
| `@search` | Searchable |
| `@hidden` | Hidden in table |
| `@editable` | Inline editable |

---

## Related Documentation
- [Migration Guide](migration-guide.md)
- [Field Type Inference](../rules/field-type-inference.md)
