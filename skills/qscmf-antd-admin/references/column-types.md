# Column Types Reference

Complete reference for all available column types in AntdAdmin components.

## Basic Fields

### text
**Use for**: Short text (names, titles, IDs)

**Table**: ✅ | **Form**: ✅

```php
// Table
$container->text('name', '名称')
          ->setSearch(false);  // Disable search

// Form
$container->text('name', '名称')
          ->addRule(new Required());
```

**Key Methods**: `setSearch(bool)`, `editable(bool)`

---

### textarea
**Use for**: Long text (descriptions, content)

**Table**: ✅ | **Form**: ✅

```php
$container->textarea('description', '描述')
          ->setFormItemWidth(24);  // Full width
```

**Key Methods**: `setFormItemWidth(int $md, int $lg)`

---

### digit
**Use for**: Numbers (price, quantity, sort)

**Table**: ✅ | **Form**: ✅

```php
// Table with inline editing
$container->digit('sort', '排序')->editable();

// Form with constraints
$container->digit('price', '价格')
          ->setFormItemProps(['min' => 0, 'precision' => 2]);
```

**Key Methods**: `editable()`, `setFormItemProps()`

---

### password
**Use for**: Password fields

**Table**: ✅ | **Form**: ✅

```php
$container->password('password', '密码');
```

---

## Date & Time Fields

### date
**Use for**: Date only (YYYY-MM-DD)

**Table**: ✅ | **Form**: ✅

```php
$container->date('birth_date', '出生日期');
```

---

### dateTime
**Use for**: Date and time (YYYY-MM-DD HH:mm:ss)

**Table**: ✅ | **Form**: ✅

```php
$container->dateTime('created_at', '创建时间');
```

---

### dateRange
**Use for**: Date range picker

**Table**: ✅ | **Form**: ✅

```php
$container->dateRange('date_range', '日期范围');
```

---

### dateTimeRange
**Use for**: DateTime range

**Table**: ✅ | **Form**: ✅

```php
$container->dateTimeRange('time_range', '时间范围');
```

---

### dateMonth
**Use for**: Month picker (YYYY-MM)

**Table**: ✅ | **Form**: ✅

```php
$container->dateMonth('month', '月份');
```

---

### dateYear
**Use for**: Year picker (YYYY)

**Table**: ✅ | **Form**: ✅

```php
$container->dateYear('year', '年份');
```

---

### time
**Use for**: Time only (HH:mm:ss)

**Table**: ✅ | **Form**: ✅

```php
$container->time('start_time', '开始时间');
```

---

### timeRange
**Use for**: Time range

**Table**: ✅ | **Form**: ✅

```php
$container->timeRange('work_hours', '工作时间');
```

---

## Selection Fields

### select
**Use for**: Dropdown selection

**Table**: ✅ | **Form**: ✅

```php
// Simple options
$container->select('status', '状态')
          ->setValueEnum([
              1 => '启用',
              0 => '禁用'
          ]);

// From database
$container->select('cate_id', '分类')
          ->setValueEnum(D('Category')->getField('id,name'));
```

**Key Methods**: `setValueEnum(Map $valueEnum)`

---

### radio
**Use for**: Radio buttons

**Table**: ✅ | **Form**: ✅

```php
$container->radio('gender', '性别')
          ->setValueEnum([
              'male' => '男',
              'female' => '女'
          ]);
```

**Key Methods**: `setValueEnum(Map $valueEnum)`

---

### radioButton
**Use for**: Radio button style

**Table**: ✅ | **Form**: ✅

```php
$container->radioButton('type', '类型')
          ->setValueEnum([
              'personal' => '个人',
              'company' => '企业'
          ]);
```

**Key Methods**: `setValueEnum(Map $valueEnum)`

---

### checkbox
**Use for**: Multiple selection

**Table**: ✅ | **Form**: ✅

```php
$container->checkbox('tags', '标签')
          ->setValueEnum([
              'tech' => '技术',
              'design' => '设计',
              'marketing' => '营销'
          ]);
```

**Key Methods**: `setValueEnum(Map $valueEnum)`

---

### switchType
**Use for**: On/off toggle

**Table**: ✅ | **Form**: ✅

```php
$container->switchType('is_active', '是否启用');
```

---

## Upload Fields

### image
**Use for**: Image upload

**Table**: ✅ | **Form**: ✅

```php
use FormItem\ObjectStorage\Lib\Common;

$container->image('cover_id', '封面图')
          ->setUploadRequest(Common::genItemDataUrl('image'))
          ->setCrop('16/9')        // Crop ratio: width/height
          ->setMaxCount(1);        // Max number of images
```

**Key Methods**:
- `setUploadRequest(string $url)` - Upload endpoint
- `setCrop(string $ratio)` - Crop ratio (e.g., '16/9', '1/1')
- `setMaxCount(int $count)` - Max files

---

### file
**Use for**: File upload

**Table**: ✅ | **Form**: ✅

```php
use FormItem\ObjectStorage\Lib\Common;

$container->file('attachment_id', '附件')
          ->setUploadRequest(Common::genItemDataUrl('file'))
          ->setMaxCount(5);
```

**Key Methods**:
- `setUploadRequest(string $url)` - Upload endpoint
- `setMaxCount(int $count)` - Max files

---

## Special Fields

### ueditor
**Use for**: Rich text editor

**Table**: ❌ | **Form**: ✅

```php
$container->ueditor('content', '内容')
          ->setFormItemWidth(24)
          ->setUeditorPath('/ueditor');  // Default path
```

**Note**: Only available in Form, not in Table

**Key Methods**:
- `setUeditorPath(string $path)` - Frontend path
- `setUeditorConfig(array $config)` - UEditor config

---

### area
**Use for**: China area cascader (province/city/district)

**Table**: ✅ | **Form**: ✅

```php
$container->area('location', '地区')
          ->setMaxLevel(3);  // Default: 3 levels
```

**Key Methods**: `setMaxLevel(int $level)`

---

### cascader
**Use for**: Custom cascader

**Table**: ✅ | **Form**: ✅

```php
// Static options
$container->cascader('category', '分类')
          ->setOptions([...]);

// Dynamic loading
$container->cascader('category', '分类')
          ->setLoadDataUrl(U('getCategories'));
```

**Key Methods**:
- `setOptions(List $options)` - Static options
- `setLoadDataUrl(string $url)` - Dynamic loading

---

### money
**Use for**: Currency input

**Table**: ✅ | **Form**: ✅

```php
$container->money('amount', '金额');
```

---

### progress
**Use for**: Progress bar

**Table**: ✅ | **Form**: ✅

```php
$container->progress('completion', '完成度');
```

---

### link
**Use for**: Link display

**Table**: ✅ | **Form**: ❌

```php
$container->link('website', '网站');
```

**Note**: Only available in Table

---

### selectText
**Use for**: Select + text search hybrid

**Table**: ✅ | **Form**: ❌

```php
// Field name format: "key:value"
$container->selectText('type:value', '类型')
          ->setValueEnum([
              'name' => '按名称',
              'id' => '按ID'
          ]);
```

**Note**: Only available in Table

**Key Methods**: `setValueEnum(Map $valueEnum)`

---

### formList
**Use for**: Dynamic form list (nested forms)

**Table**: ❌ | **Form**: ✅

```php
$container->formList('members', '成员')
          ->columns(function (Form\ColumnsContainer $container) {
              $container->text('name', '姓名');
              $container->text('phone', '电话');
          });
```

**Note**: Only available in Form

**Key Methods**: `columns(Closure $callback)`

---

## Quick Reference Table

| Type | Table | Form | Common Use Case | Key Method |
|------|-------|------|-----------------|------------|
| **text** | ✅ | ✅ | Names, titles | `setSearch()` |
| **textarea** | ✅ | ✅ | Descriptions | `setFormItemWidth()` |
| **digit** | ✅ | ✅ | Numbers | `editable()` |
| **password** | ✅ | ✅ | Passwords | - |
| **date** | ✅ | ✅ | Date | - |
| **dateTime** | ✅ | ✅ | DateTime | - |
| **dateRange** | ✅ | ✅ | Date range | - |
| **dateTimeRange** | ✅ | ✅ | DateTime range | - |
| **dateMonth** | ✅ | ✅ | Month | - |
| **dateYear** | ✅ | ✅ | Year | - |
| **time** | ✅ | ✅ | Time | - |
| **timeRange** | ✅ | ✅ | Time range | - |
| **select** | ✅ | ✅ | Dropdown | `setValueEnum()` |
| **radio** | ✅ | ✅ | Radio buttons | `setValueEnum()` |
| **radioButton** | ✅ | ✅ | Radio buttons | `setValueEnum()` |
| **checkbox** | ✅ | ✅ | Multi-select | `setValueEnum()` |
| **switchType** | ✅ | ✅ | Toggle | - |
| **image** | ✅ | ✅ | Image upload | `setCrop()`, `setUploadRequest()` |
| **file** | ✅ | ✅ | File upload | `setUploadRequest()` |
| **ueditor** | ❌ | ✅ | Rich text | `setUeditorPath()` |
| **area** | ✅ | ✅ | Area cascader | `setMaxLevel()` |
| **cascader** | ✅ | ✅ | Custom cascader | `setOptions()` |
| **money** | ✅ | ✅ | Currency | - |
| **progress** | ✅ | ✅ | Progress bar | - |
| **link** | ✅ | ❌ | Links | - |
| **selectText** | ✅ | ❌ | Select+text | `setValueEnum()` |
| **formList** | ❌ | ✅ | Dynamic forms | `columns()` |
