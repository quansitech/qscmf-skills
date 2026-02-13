---
title: Custom Components and Renderers (v14 AntdAdmin)
impact: HIGH
impactDescription: Used in 40% of advanced UI customizations
tags: crud, custom, components, react, v14
---

## Custom Components and Renderers (v14 AntdAdmin)

Create custom table columns and form fields using React components in QSCMF v14.

### When to Use This Rule

- You need custom table column rendering beyond built-in types
- You want to integrate React components (Badge, Tag, Progress, etc.)
- You need conditional rendering based on data values
- You want to create reusable custom components
- You need to understand the v14 custom renderer system

---

## Why Custom Renderers?

**Built-in columns** are great for standard cases:
- `text()` - Simple text display
- `select()` - Dropdown with enum values
- `date()` - Date formatting
- `image()` - Image display

**Custom renderers** enable:
- Complex visual presentations
- Interactive components
- Conditional logic
- Third-party React component integration
- Data transformation before display

---

## Custom Renderer API

### setRenderer() Method

```php
$container->custom('field_name', 'Column Title')
    ->setRenderer(callable $renderer);
```

**Parameters:**
- `$value` - Mixed: The field value from database
- `$row` - Array: Complete row data (all fields)

**Returns:**
- React component definition (array format)

---

## Basic Custom Renderers

### Example 1: Status Badge

```php
$container->custom('status', '状态')
    ->setRenderer(function($value, $row) {
        $statusMap = [
            0 => ['text' => '禁用', 'color' => 'default'],
            1 => ['text' => '启用', 'color' => 'success'],
            2 => ['text' => '审核中', 'color' => 'processing'],
            3 => ['text' => '已拒绝', 'color' => 'error']
        ];

        $status = $statusMap[$value] ?? ['text' => '未知', 'color' => 'default'];

        return [
            'type' => 'Badge',
            'props' => [
                'status' => $status['color'],
                'text' => $status['text']
            ]
        ];
    });
```

**Rendered as:** Ant Design Badge component

### Example 2: Colored Tags

```php
$container->custom('priority', '优先级')
    ->setRenderer(function($value) {
        $priorityMap = [
            1 => ['text' => '低', 'color' => 'green'],
            2 => ['text' => '中', 'color' => 'orange'],
            3 => ['text' => '高', 'color' => 'red'],
            4 => ['text' => '紧急', 'color' => 'magenta']
        ];

        $priority = $priorityMap[$value] ?? ['text' => '未知', 'color' => 'default'];

        return [
            'type' => 'Tag',
            'props' => [
                'color' => $priority['color'],
                'children' => $priority['text']
            ]
        ];
    });
```

**Rendered as:** Ant Design Tag component

### Example 3: Conditional Text Styling

```php
$container->custom('stock', '库存')
    ->setRenderer(function($value) {
        if ($value <= 0) {
            return [
                'type' => 'Text',
                'props' => [
                    'type' => 'danger',
                    'children' => '缺货'
                ]
            ];
        } elseif ($value < 10) {
            return [
                'type' => 'Text',
                'props' => [
                    'type' => 'warning',
                    'children' => "库存紧张 ({$value})"
                ]
            ];
        } else {
            return [
                'type' => 'Text',
                'props' => [
                    'children' => (string)$value
                ]
            ];
        }
    });
```

### Example 4: Custom Date Format

```php
$container->custom('create_time', '创建时间')
    ->setRenderer(function($value) {
        if (empty($value)) return '-';

        $timestamp = is_numeric($value) ? $value : strtotime($value);
        $now = time();
        $diff = $now - $timestamp;

        // Less than 1 hour
        if ($diff < 3600) {
            $minutes = floor($diff / 60);
            return "{$minutes} 分钟前";
        }

        // Less than 1 day
        if ($diff < 86400) {
            $hours = floor($diff / 3600);
            return "{$hours} 小时前";
        }

        // Less than 7 days
        if ($diff < 604800) {
            $days = floor($diff / 86400);
            return "{$days} 天前";
        }

        // Otherwise show full date
        return date('Y-m-d H:i', $timestamp);
    });
```

---

## Advanced Custom Renderers

### Example 5: Progress Bar

```php
$container->custom('progress', '完成进度')
    ->setRenderer(function($value) {
        $percentage = min(100, max(0, (int)$value));

        return [
            'type' => 'Progress',
            'props' => [
                'percent' => $percentage,
                'status' => $percentage >= 100 ? 'success' : 'active',
                'strokeColor' => $percentage >= 80 ? '#52c41a' :
                              ($percentage >= 50 ? '#faad14' : '#ff4d4f')
            ]
        ];
    });
```

### Example 6: Avatar with Name

```php
$container->custom('username', '用户')
    ->setRenderer(function($value, $row) {
        $avatar = $row['avatar'] ?? '/default/avatar.png';

        return [
            'type' => 'Space',
            'props' => [
                'size' => 'middle',
                'children' => [
                    [
                        'type' => 'Avatar',
                        'props' => [
                            'src' => $avatar,
                            'size' => 'small'
                        ]
                    ],
                    [
                        'type' => 'Text',
                        'props' => [
                            'children' => $value
                        ]
                    ]
                ]
            ]
        ]
        ];
    });
```

### Example 7: Multiple Images Gallery

```php
$container->custom('images', '产品图片')
    ->setRenderer(function($value) {
        if (empty($value)) return '-';

        $images = is_array($value) ? $value : json_decode($value, true);
        if (empty($images)) return '-';

        return [
            'type' => 'Image.PreviewGroup',
            'props' => [
                'preview' => [
                    'children' => array_map(function($img) {
                        return [
                            'type' => 'Image',
                            'props' => [
                                'src' => $img,
                                'width' => 60,
                                'height' => 60,
                                'style' => ['marginRight' => '8px']
                            ]
                        ];
                    }, $images)
                ]
            ]
        ];
    });
```

### Example 8: Link to Related Record

```php
$container->custom('category_id', '分类')
    ->setRenderer(function($value, $row) {
        $categoryName = $row['category_name'] ?? '未知分类';

        return [
            'type' => 'Link',
            'props' => [
                'href' => "/admin/product/index?category_id={$value}",
                'children' => $categoryName,
                'target' => '_self'
            ]
        ];
    });
```

### Example 9: Rating Stars

```php
$container->custom('rating', '评分')
    ->setRenderer(function($value) {
        $rating = min(5, max(0, (float)$value));
        $fullStars = floor($rating);
        $hasHalfStar = ($rating - $fullStars) >= 0.5;

        $stars = [];
        for ($i = 0; $i < $fullStars; $i++) {
            $stars[] = ['type' => 'StarFilled', 'props' => ['style' => ['color' => '#faad14']]];
        }
        if ($hasHalfStar) {
            $stars[] = ['type' => 'StarHalfFilled', 'props' => ['style' => ['color' => '#faad14']]];
        }

        return [
            'type' => 'Space',
            'props' => [
                'children' => array_merge($stars, [
                    ['type' => 'Text', 'props' => ['children' => " ({$rating})"]]
                ])
            ]
        ];
    });
```

### Example 10: Action Buttons in Column

```php
$container->custom('actions', '操作')
    ->setRenderer(function($value, $row) {
        return [
            'type' => 'Space',
            'props' => [
                'children' => [
                    [
                        'type' => 'Link',
                        'props' => [
                            'href' => "/admin/product/edit/id/{$row['id']}",
                            'children' => '编辑'
                        ]
                    ],
                    [
                        'type' => 'Popconfirm',
                        'props' => [
                            'title' => '确定要删除吗?',
                            'onConfirm' => "deleteItem({$row['id']})",
                            'children' => [
                                [
                                    'type' => 'Button',
                                    'props' => [
                                        'type' => 'link',
                                        'danger' => true,
                                        'children' => '删除'
                                    ]
                                ]
                            ]
                        ]
                    ]
                ]
            ]
        ];
    });
```

---

## Supported React Components

### Ant Design Components

QSCMF v14 supports most Ant Design components:

| Component | Type Value | Common Props | Use Case |
|-----------|-------------|---------------|-----------|
| **Badge** | `Badge` | status, text, color | Status indicators |
| **Tag** | `Tag` | color, children, closable | Labels, categories |
| **Progress** | `Progress` | percent, status, strokeColor | Progress bars |
| **Avatar** | `Avatar` | src, size, shape, icon | User avatars |
| **Image** | `Image` | src, width, height, preview | Image display |
| **Image.PreviewGroup** | `Image.PreviewGroup` | preview | Image galleries |
| **Space** | `Space` | size, direction, children | Layout spacing |
| **Link** | `Link` | href, target, children | Navigation links |
| **Button** | `Button` | type, size, danger, icon | Action buttons |
| **Popconfirm** | `Popconfirm` | title, onConfirm, children | Confirmation dialogs |
| **Tooltip** | `Tooltip` | title, children | Hover information |
| **Switch** | `Switch` | checked, disabled, onChange | Toggle switches |
| **Rate** | `Rate` | count, value, disabled | Star ratings |
| **Text** | `Text` | type, copyable, children | Text with styling |
| **Divider** | `Divider` | orientation, dashed | Content separation |

### Component Type Mapping

```php
// Badge - Status indicator
return ['type' => 'Badge', 'props' => ['status' => 'success', 'text' => '启用']];

// Tag - Label
return ['type' => 'Tag', 'props' => ['color' => 'blue', 'children' => '分类']];

// Progress - Progress bar
return ['type' => 'Progress', 'props' => ['percent' => 75]];

// Space - Layout wrapper
return ['type' => 'Space', 'props' => ['children' => [...components]]];

// Avatar - User avatar
return ['type' => 'Avatar', 'props' => ['src' => $avatarUrl, 'size' => 'large']];

// Image - Display image
return ['type' => 'Image', 'props' => ['src' => $imageUrl, 'width' => 100]];
```

---

## Custom Renderer Patterns

### Pattern 1: Value Mapping

```php
$container->custom('type', '类型')
    ->setRenderer(function($value) {
        $map = [
            1 => ['text' => '类型A', 'icon' => 'apple'],
            2 => ['text' => '类型B', 'icon' => 'android'],
            3 => ['text' => '类型C', 'icon' => 'windows']
        ];

        return $map[$value] ?? ['text' => '未知', 'icon' => 'question'];
    });
```

### Pattern 2: Complex Conditional Logic

```php
$container->custom('price', '价格')
    ->setRenderer(function($value, $row) {
        // Apply discount if user is VIP
        if ($row['is_vip'] == 1) {
            $discountedPrice = $value * 0.9;
            return [
                'type' => 'Space',
                'props' => [
                    'direction' => 'vertical',
                    'size' => 0,
                    'children' => [
                        ['type' => 'Text', 'props' => ['delete' => true, 'children' => '¥' . $value]],
                        ['type' => 'Text', 'props' => ['type' => 'success', 'children' => 'VIP: ¥' . $discountedPrice]]
                    ]
                ]
            ]
            ];
        }

        return ['type' => 'Text', 'props' => ['children' => '¥' . $value]];
    });
```

### Pattern 3: Data Aggregation

```php
$container->custom('stats', '统计')
    ->setRenderer(function($value, $row) {
        $views = $row['views'] ?? 0;
        $likes = $row['likes'] ?? 0;
        $shares = $row['shares'] ?? 0;

        return [
            'type' => 'Space',
            'props' => [
                'children' => [
                    ['type' => 'Text', 'props' => ['children' => "👁️ {$views}"]],
                    ['type' => 'Text', 'props' => ['children' => "👍 {$likes}"]],
                    ['type' => 'Text', 'props' => ['children' => "🔗 {$shares}"]]
                ]
            ]
        ];
    });
```

### Pattern 4: External Data Integration

```php
$container->custom('user_id', '用户')
    ->setRenderer(function($value) {
        if (empty($value)) return '-';

        // Fetch user data asynchronously
        return [
            'type' => 'AsyncText',
            'props' => [
                'url' => "/api/user/{$value}",
                'dataField' => 'username',
                'defaultText' => "用户 #{$value}"
            ]
        ];
    });
```

---

## v13 vs v14 Custom Renderers

### v14 (AntdAdmin) - React Components

```php
$container->custom('status', '状态')
    ->setRenderer(function($value) {
        return [
            'type' => 'Badge',
            'props' => [
                'status' => $value == 1 ? 'success' : 'default',
                'text' => $value == 1 ? '启用' : '禁用'
            ]
        ];
    });
```

**Advantages:**
- Component-based architecture
- Type-safe props
- Reusable components
- Modern React patterns

### v13 (Legacy jQuery) - HTML Callbacks

```php
$builder->addTableColumn('status', '状态', function($value) {
    if ($value == 1) {
        return '<span class="label label-success">启用</span>';
    } elseif ($value == 0) {
        return '<span class="label label-default">禁用</span>';
    }
    return '<span class="label label-warning">未知</span>';
});
```

**Advantages:**
- Simple HTML string output
- Direct control over markup
- No React knowledge needed

**Limitations:**
- Manual HTML escaping required
- Harder to maintain
- No component reusability
- Inconsistent styling

---

## Advanced Features

### Inline Editing with Custom Renderer

```php
$container->custom('stock', '库存')
    ->setRenderer(function($value, $row) {
        return [
            'type' => 'InputNumber',
            'props' => [
                'value' => (int)$value,
                'min' => 0,
                'onChange' => "updateStock({$row['id']}, value)",
                'style' => ['width' => '100px']
            ]
        ];
    });
```

### Custom Actions with Confirmation

```php
$container->custom('quick_actions', '快捷操作')
    ->setRenderer(function($value, $row) {
        return [
            'type' => 'Dropdown',
            'props' => [
                'menu' => [
                    'items' => [
                        ['key' => 'publish', 'label' => '发布'],
                        ['key' => 'top', 'label' => '置顶'],
                        ['key' => 'delete', 'label' => '删除', 'danger' => true]
                    ]
                ],
                'onSelect' => "handleQuickAction({$row['id']}, key)",
                'children' => [
                    ['type' => 'Button', 'props' => ['children' => '更多']]
                ]
            ]
        ];
    });
```

### Nested Data Display

```php
$container->custom('options', '规格选项')
    ->setRenderer(function($value) {
        if (empty($value)) return '-';

        $options = json_decode($value, true);

        return [
            'type' => 'Descriptions',
            'props' => [
                'column' => 1,
                'size' => 'small',
                'items' => array_map(function($opt) {
                    return ['label' => $opt['name'], 'children' => $opt['value']];
                }, $options)
            ]
        ];
    });
```

---

## Best Practices

### 1. Always Handle Edge Cases

```php
$container->custom('status', '状态')
    ->setRenderer(function($value) {
        // Handle null/empty
        if ($value === null || $value === '') {
            return ['type' => 'Text', 'props' => ['children' => '-']];
        }

        // Handle unexpected values
        $statusMap = [0 => '禁用', 1 => '启用'];
        $text = $statusMap[$value] ?? "未知({$value})";

        return ['type' => 'Badge', 'props' => ['text' => $text]];
    });
```

### 2. Use Type Casting

```php
$container->custom('price', '价格')
    ->setRenderer(function($value) {
        // Ensure numeric
        $price = (float)$value;

        return ['type' => 'Text', 'props' => ['children' => '¥' . number_format($price, 2)]];
    });
```

### 3. Escape User Content

```php
$container->custom('title', '标题')
    ->setRenderer(function($value) {
        // Ant Design components auto-escape, but be explicit for custom HTML
        return ['type' => 'Text', 'props' => ['children' => htmlspecialchars($value)]];
    });
```

### 4. Cache Expensive Operations

```php
$container->custom('category', '分类')
    ->setRenderer(function($value, $row) use (&$categoryCache) {
        if (!isset($categoryCache)) {
            $categoryCache = [];
        }

        $categoryId = $row['category_id'];

        if (!isset($categoryCache[$categoryId])) {
            $categoryCache[$categoryId] = D('Category')->getFieldById($categoryId, 'title');
        }

        return ['type' => 'Text', 'props' => ['children' => $categoryCache[$categoryId]]];
    });
```

### 5. Provide Fallbacks

```php
$container->custom('avatar', '头像')
    ->setRenderer(function($value, $row) {
        $avatar = $value ?: '/assets/default-avatar.png';

        return [
            'type' => 'Avatar',
            'props' => [
                'src' => $avatar,
                'size' => 'large',
                'alt' => $row['username'] ?? 'User'
            ]
        ];
    });
```

---

## Troubleshooting

| Problem | Cause | Solution |
|---------|--------|----------|
| Renderer not called | Wrong column name or field not selected | Check column name matches database field |
| React component not rendering | Invalid component type or props | Verify component name and props structure |
| Array values display as "Array" | Missing array handling | Check for `is_array()` and handle appropriately |
| Performance slow | Expensive operations in renderer | Cache data or optimize queries |
| XSS vulnerability | Unescaped user content | Always use React components (auto-escape) instead of raw HTML |
| Error "undefined index" | Accessing non-existent row fields | Use `??` operator: `$row['field'] ?? 'default'` |
| Component props not working | Wrong prop names or types | Check Ant Design documentation for correct prop names |

---

## Complete Working Example

### Product Table with Custom Renderers

```php
<?php
// app/Admin/Controller/ProductController.class.php

namespace Admin\Controller;
use Gy_Library\Components\TableContainer;

class ProductController extends \QsAdmin\Controller\QsListController
{
    protected $tableName = 'product';

    protected function tableContainer(TableContainer $container): void
    {
        // Standard columns
        $container->text('id', 'ID')->setWidth(80);
        $container->text('name', '产品名称')->setEllipsis(true);

        // Custom: Price with discount
        $container->custom('price', '价格')
            ->setRenderer(function($value, $row) {
                $price = (float)$value;
                $originalPrice = (float)($row['market_price'] ?? $value);

                if ($originalPrice > $price) {
                    $discount = round(($originalPrice - $price) / $originalPrice * 100, 1);
                    return [
                        'type' => 'Space',
                        'props' => [
                            'children' => [
                                ['type' => 'Text', 'props' => ['delete' => true, 'children' => '¥' . $originalPrice]],
                                ['type' => 'Text', 'props' => ['type' => 'danger', 'children' => "¥{$price} (省{$discount}%)"]]
                            ]
                        ]
                    ];
                }

                return ['type' => 'Text', 'props' => ['children' => '¥' . number_format($price, 2)]];
            });

        // Custom: Stock status
        $container->custom('stock', '库存')
            ->setRenderer(function($value) {
                $stock = (int)$value;

                if ($stock <= 0) {
                    return ['type' => 'Tag', 'props' => ['color' => 'red', 'children' => '缺货']];
                } elseif ($stock < 10) {
                    return ['type' => 'Tag', 'props' => ['color' => 'orange', 'children' => '库存紧张']];
                } elseif ($stock < 50) {
                    return ['type' => 'Tag', 'props' => ['color' => 'blue', 'children' => '充足']];
                } else {
                    return ['type' => 'Tag', 'props' => ['color' => 'green', 'children' => '库存丰富']];
                }
            });

        // Custom: Status with badge
        $container->custom('status', '状态')
            ->setRenderer(function($value) {
                $statusMap = [
                    0 => ['text' => '下架', 'badge' => 'default'],
                    1 => ['text' => '在售', 'badge' => 'success'],
                    2 => ['text' => '售罄', 'badge' => 'error'],
                    3 => ['text' => '预售', 'badge' => 'processing']
                ];

                $status = $statusMap[$value] ?? ['text' => '未知', 'badge' => 'default'];

                return [
                    'type' => 'Badge',
                    'props' => [
                        'status' => $status['badge'],
                        'text' => $status['text']
                    ]
                ];
            });

        // Custom: Category with link
        $container->custom('category_id', '分类')
            ->setRenderer(function($value, $row) {
                $categoryName = $row['category_name'] ?? '未知';

                return [
                    'type' => 'Link',
                    'props' => [
                        'href' => "/admin/product/index?category_id={$value}",
                        'children' => $categoryName
                    ]
                ];
            });

        // Custom: Images preview
        $container->custom('images', '图片')
            ->setRenderer(function($value) {
                if (empty($value)) return '-';

                $images = is_array($value) ? $value : json_decode($value, true);
                if (empty($images)) return '-';

                $imageComponents = array_slice(array_map(function($img) {
                    return [
                        'type' => 'Image',
                        'props' => [
                            'src' => $img,
                            'width' => 40,
                            'height' => 40,
                            'style' => ['marginRight' => '4px', 'borderRadius' => '4px']
                        ]
                    ];
                }, $images), 0, 3);

                if (count($images) > 3) {
                    $imageComponents[] = [
                        'type' => 'Text',
                        'props' => ['children' => '...' . (count($images) - 3)]
                    ];
                }

                return [
                    'type' => 'Space',
                    'props' => ['children' => $imageComponents]
                ];
            });

        // Custom: Sales statistics
        $container->custom('sales_stats', '销量统计')
            ->setRenderer(function($value, $row) {
                $sales = (int)($row['sales'] ?? 0);
                $views = (int)($row['views'] ?? 0);

                if ($views > 0) {
                    $conversion = round($sales / $views * 100, 2);
                } else {
                    $conversion = 0;
                }

                return [
                    'type' => 'Space',
                    'props' => [
                        'direction' => 'vertical',
                        'size' => 0,
                        'children' => [
                            ['type' => 'Text', 'props' => ['children' => "销量: {$sales}"]],
                            ['type' => 'Text', 'props' => ['type' => 'secondary', 'children' => "浏览: {$views}"]],
                            ['type' => 'Text', 'props' => ['type' => $conversion > 5 ? 'success' : 'default', 'children' => "转化率: {$conversion}%"]]
                        ]
                    ]
                ];
            });

        // Action column
        $container->action('', '操作')
            ->setParams(['id' => 'id'])
            ->actions(function($actions) {
                $actions->edit();
                $actions->delete();
            });
    }

    protected function formContainer(\Gy_Library\Components\FormContainer $container): void
    {
        // Form configuration...
    }
}
```

---

## See Also

- [Table Columns v14](crud-table-columns-v14.md) - Built-in column types
- [Form Validation](crud-form-validation.md) - Form field validation
- [Admin Controllers](../../references/admin-controllers.md) - Complete controller patterns
- [Ant Design Documentation](https://ant.design/components/overview/) - React component reference

---

## Iron Law

```
CUSTOM RENDERERS MUST RETURN VALID REACT COMPONENT DEFINITIONS
```
