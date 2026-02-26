---
title: Legacy jQuery Rendering (v13)
impact: HIGH
impactDescription: v13-specific jQuery/Bootstrap quirks (50% of debugging)
tags: v13, jquery, bootstrap, legacy, rendering
---

## Legacy jQuery Rendering (v13)

v13 uses jQuery + Bootstrap 3 for admin rendering. This document covers v13-specific behaviors and quirks.

### When to Use This Rule

- Debugging v13 admin UI issues
- Adding custom JavaScript interactions
- Handling Bootstrap modal issues
- Working with DataTables integration

---

## Rendering Mode

v13 uses legacy jQuery rendering by default:

```php
// Environment configuration
ANTD_ADMIN_BUILDER_ENABLE = false  // v13 default (jQuery rendering)
```

To switch to React rendering (v14 feature), set:
```php
ANTD_ADMIN_BUILDER_ENABLE = true
```

---

## Bootstrap 3 CSS Classes

v13 admin pages use Bootstrap 3 classes:

### Status Badges

```html
<!-- Standard status display -->
<span class="label label-success">启用</span>
<span class="label label-default">禁用</span>
<span class="label label-warning">待审核</span>
<span class="label label-danger">已拒绝</span>
<span class="label label-info">进行中</span>
<span class="label label-primary">重要</span>
```

### Buttons

```html
<!-- Button styles -->
<button class="btn btn-primary">主要按钮</button>
<button class="btn btn-success">成功</button>
<button class="btn btn-danger">危险</button>
<button class="btn btn-warning">警告</button>
<button class="btn btn-info">信息</button>
<button class="btn btn-default">默认</button>
<button class="btn btn-link">链接</button>

<!-- Button sizes -->
<button class="btn btn-primary btn-lg">大按钮</button>
<button class="btn btn-primary btn-sm">小按钮</button>
<button class="btn btn-primary btn-xs">超小按钮</button>
```

### Tables

```html
<table class="table table-striped table-bordered table-hover">
    <thead>
        <tr>
            <th>ID</th>
            <th>名称</th>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td>1</td>
            <td>示例</td>
        </tr>
    </tbody>
</table>
```

### Forms

```html
<div class="form-group">
    <label class="col-sm-2 control-label">名称</label>
    <div class="col-sm-10">
        <input type="text" class="form-control" name="name" placeholder="请输入名称">
    </div>
</div>
```

---

## jQuery Event Handling

### Form Submission

```javascript
// Custom form submission
$('#myForm').on('submit', function(e) {
    e.preventDefault();

    var $form = $(this);
    var formData = $form.serialize();

    $.post($form.attr('action'), formData, function(res) {
        if (res.status) {
            // Success
            location.reload();
        } else {
            // Error
            alert(res.msg || '操作失败');
        }
    }, 'json').fail(function() {
        alert('网络错误，请重试');
    });
});
```

### AJAX Button Click

```javascript
// AJAX button handler
$('.ajax-btn').on('click', function(e) {
    e.preventDefault();

    var $btn = $(this);
    var url = $btn.data('url') || $btn.attr('href');
    var confirmMsg = $btn.data('confirm');

    if (confirmMsg && !confirm(confirmMsg)) {
        return false;
    }

    $.post(url, {}, function(res) {
        if (res.status) {
            location.reload();
        } else {
            alert(res.msg || '操作失败');
        }
    }, 'json');
});
```

### Before Search Event

```javascript
// Validate before search
$('body').on('beforeSearch', '.builder #search', function() {
    var keyword = $("input[name='keyword']").val();

    if (!keyword) {
        $(this).data('jump', 0);  // Prevent form submission
        alert('关键词不能为空');
    }
});
```

### Dynamic Content Events

```javascript
// Event delegation for dynamic content
$('body').on('click', '.dynamic-element', function(e) {
    // Handle click on dynamically added elements
});

// Custom event trigger
$('.my-element').trigger('custom:event', [param1, param2]);
```

---

## DataTables Integration

v13 uses DataTables for table rendering:

### Basic Configuration

```javascript
$('#data-table').DataTable({
    processing: true,
    serverSide: false,
    pageLength: 20,
    order: [[0, 'desc']],
    language: {
        processing: '加载中...',
        search: '搜索:',
        lengthMenu: '显示 _MENU_ 条记录',
        info: '显示第 _START_ 至 _END_ 条记录，共 _TOTAL_ 条',
        infoEmpty: '没有数据',
        infoFiltered: '(由 _MAX_ 条记录过滤)',
        paginate: {
            first: '首页',
            previous: '上一页',
            next: '下一页',
            last: '末页'
        },
        emptyTable: '表中数据为空',
        zeroRecords: '没有找到匹配的记录'
    }
});
```

### Server-Side Processing

```javascript
$('#data-table').DataTable({
    processing: true,
    serverSide: true,
    ajax: {
        url: '/api/data',
        type: 'POST'
    },
    columns: [
        { data: 'id' },
        { data: 'name' },
        { data: 'status' },
        { data: 'created_at' }
    ]
});
```

---

## Bootstrap Modal Issues

### Z-Index Problems

```javascript
// Fix z-index issues with multiple modals
$(document).on('show.bs.modal', '.modal', function() {
    var zIndex = 1040 + (10 * $('.modal:visible').length);
    $(this).css('z-index', zIndex);
    setTimeout(function() {
        $('.modal-backdrop').not('.modal-stack').css('z-index', zIndex - 1).addClass('modal-stack');
    }, 0);
});
```

### Modal with data-backdrop

```html
<!-- Disable backdrop for z-index issues -->
<div class="modal" data-backdrop="false">

<!-- Static backdrop (can't close by clicking outside) -->
<div class="modal" data-backdrop="static">
```

### Modal Events

```javascript
// Modal events
$('#myModal').on('show.bs.modal', function(e) {
    // Before modal shows
});

$('#myModal').on('shown.bs.modal', function(e) {
    // After modal is fully shown
});

$('#myModal').on('hide.bs.modal', function(e) {
    // Before modal hides
});

$('#myModal').on('hidden.bs.modal', function(e) {
    // After modal is fully hidden
    // Clean up form data
    $(this).find('form')[0].reset();
});
```

---

## AJAX Form Upload

### FormData Upload

```javascript
// AJAX file upload with FormData
$('#uploadForm').on('submit', function(e) {
    e.preventDefault();

    var formData = new FormData(this);

    $.ajax({
        url: $(this).attr('action'),
        type: 'POST',
        data: formData,
        processData: false,
        contentType: false,
        success: function(res) {
            if (res.status) {
                alert('上传成功');
            } else {
                alert(res.msg || '上传失败');
            }
        },
        error: function() {
            alert('网络错误');
        }
    });
});
```

### Single File Upload Preview

```javascript
// Image preview before upload
$('input[type="file"]').on('change', function(e) {
    var file = e.target.files[0];
    if (!file) return;

    if (!file.type.match('image.*')) {
        alert('请选择图片文件');
        return;
    }

    var reader = new FileReader();
    reader.onload = function(e) {
        $('#preview').attr('src', e.target.result);
    };
    reader.readAsDataURL(file);
});
```

---

## Known Quirks

### 1. IE11 Compatibility

v13 jQuery is more compatible with IE11:

```javascript
// Avoid ES6 features for IE11
// BAD
const func = () => { };
let arr = [1, 2, 3].map(x => x * 2);

// GOOD
var func = function() { };
var arr = [1, 2, 3].map(function(x) { return x * 2; });
```

### 2. Event Binding After AJAX

```javascript
// Use event delegation for AJAX content
$(document).on('click', '.ajax-content .btn', function() {
    // This works for dynamically added content
});

// Instead of
$('.ajax-content .btn').on('click', function() {
    // This only works for existing content
});
```

### 3. Form Reset Issues

```javascript
// Proper form reset
$('#myForm')[0].reset();

// Reset with select2
$('#myForm')[0].reset();
$('select').select2('val', '');

// Reset with file input
$('#myForm')[0].reset();
$('input[type="file"]').val('');
```

### 4. Checkbox Value Handling

```javascript
// Get checkbox values correctly
var checked = [];
$('input[name="ids[]"]:checked').each(function() {
    checked.push($(this).val());
});

// Or using map
var checked = $('input[name="ids[]"]:checked').map(function() {
    return $(this).val();
}).get();
```

### 5. CSRF Token

```javascript
// Include CSRF token in AJAX requests
$.ajaxSetup({
    headers: {
        'X-CSRF-TOKEN': $('meta[name="csrf-token"]').attr('content')
    }
});
```

---

## Browser Compatibility

| Feature | Chrome | Firefox | Safari | IE11 |
|---------|--------|---------|--------|------|
| jQuery 1.x | Full | Full | Full | Full |
| Bootstrap 3 | Full | Full | Full | Partial* |
| DataTables | Full | Full | Full | Full |
| FormData | Full | Full | Full | 10+ |

*Bootstrap 3 in IE11 has some layout issues with grid system.

---

## Migration to v14

To migrate from v13 jQuery to v14 React:

1. **Controller code stays the same** - ListBuilder API is identical
2. **Custom JavaScript needs rewrite** - Convert to React components
3. **Bootstrap classes change** - Use Ant Design classes instead
4. **DataTables replaced** - Use Ant Design Table component

### Switching Rendering Mode

```php
// In .env or config
ANTD_ADMIN_BUILDER_ENABLE = true  // Enable React rendering

// Controllers remain unchanged
// The same ListBuilder code renders with React components
```

---

## Debugging Tips

### Console Debugging

```javascript
// Check jQuery loaded
console.log($.fn.jquery);

// Check Bootstrap loaded
console.log($.fn.modal);

// Debug AJAX
$(document).ajaxComplete(function(e, xhr, settings) {
    console.log('AJAX Complete:', settings.url, xhr.responseJSON);
});
```

### Common Errors

| Error | Cause | Solution |
|-------|-------|----------|
| `$ is not defined` | jQuery not loaded | Add jQuery script tag |
| `modal is not a function` | Bootstrap JS not loaded | Add Bootstrap JS |
| `DataTables is not a function` | DataTables not loaded | Add DataTables script |
| Form submit refreshes page | Event not prevented | Add `e.preventDefault()` |
| AJAX 500 error | Server error | Check PHP error logs |

---

## Related Rules

- [ListBuilder API](listbuilder-api.md) - Core table API
- [FormBuilder API](formbuilder-api.md) - Form configuration
- [CRUD Table Columns v13](crud/crud-table-columns-v13.md) - Column configuration
