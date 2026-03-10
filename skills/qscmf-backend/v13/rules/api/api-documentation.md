---
title: API Documentation (v13)
impact: MEDIUM
impactDescription: OpenAPI/Apifox documentation generation
tags: api, documentation, openapi, apifox, v13
---

## API Documentation (v13)

OpenAPI/Apifox documentation generation for QSCMF v13 API endpoints.

### When to Use This Rule

- Creating new API endpoints that need documentation
- Generating Apifox-compatible API specs
- Documenting cross-system APIs (QscmfCrossApi)

---

## Documentation Approach

**Decision:** Hand-written OpenAPI JSON files, not swagger-php.

**Rationale:**
- Only a few APIs → swagger-php is overkill
- Simple and direct, easy to maintain
- Documentation separated from code, doesn't pollute business logic
- Easy to import into Apifox

---

## File Location

```
docs/openapi.json
```

---

## OpenAPI 3.0 Structure

### Basic Template

```json
{
  "openapi": "3.0.0",
  "info": {
    "title": "模块名 - API",
    "description": "API 描述",
    "version": "1.0.0"
  },
  "servers": [
    {
      "url": "/",
      "description": "API 服务"
    }
  ],
  "tags": [
    {
      "name": "ControllerName",
      "description": "控制器描述"
    }
  ],
  "paths": {
    "/api/ControllerName/method": {
      "post": {
        "tags": ["ControllerName"],
        "summary": "接口摘要",
        "requestBody": {
          "required": true,
          "content": {
            "application/json": {
              "schema": {
                "$ref": "#/components/schemas/RequestSchema"
              }
            }
          }
        },
        "responses": {
          "200": {
            "description": "成功",
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/ResponseSchema"
                }
              }
            }
          }
        }
      }
    }
  },
  "components": {
    "schemas": {
      "RequestSchema": {
        "type": "object",
        "required": ["field1"],
        "properties": {
          "field1": {
            "type": "string",
            "description": "字段描述"
          }
        }
      },
      "ResponseSchema": {
        "type": "object",
        "properties": {
          "status": {
            "type": "integer",
            "description": "状态码，1 成功，0 失败"
          },
          "info": {
            "type": "string",
            "description": "提示信息"
          },
          "data": {
            "type": "object"
          }
        }
      }
    }
  }
}
```

---

## Key Principles

### 1. Use `$ref` for Data Models

**Good:** Define reusable schemas in `components/schemas`
```json
{
  "schema": {
    "$ref": "#/components/schemas/UserData"
  }
}
```

**Bad:** Inline schema definitions
```json
{
  "schema": {
    "type": "object",
    "properties": { ... }
  }
}
```

### 2. Standard Response Format

All QSCMF API responses follow this format:

```json
{
  "status": 1,      // 1 = success, 0 = failure
  "info": "提示信息",
  "data": {}        // Response data (nullable)
}
```

Define response schemas:

```json
{
  "SuccessResponse": {
    "type": "object",
    "properties": {
      "status": { "type": "integer", "enum": [1] },
      "info": { "type": "string" },
      "data": { "$ref": "#/components/schemas/DataModel" }
    }
  },
  "ErrorResponse": {
    "type": "object",
    "properties": {
      "status": { "type": "integer", "enum": [0] },
      "info": { "type": "string" }
    }
  }
}
```

### 3. API Path Format (RESTful)

QSCMF RestController uses RESTful routing. HTTP method determines the action:

```
/Api/{ResourceName}
```

| HTTP Method | URI | Controller Method |
|-------------|-----|-------------------|
| GET | `/Api/OaQrcode` | `gets()` |
| POST | `/Api/OaQrcode` | `create()` |
| PUT | `/Api/OaQrcode/{id}` | `update()` |
| DELETE | `/Api/OaQrcode/{id}` | `delete()` |

**Note:** Don't include method name in URI. The framework routes based on HTTP verb.

### 4. Callback Payload Documentation

For APIs that trigger callbacks, document the callback payload:

```json
{
  "CallbackPayload": {
    "type": "object",
    "description": "回调通知的数据结构",
    "properties": {
      "field1": { "type": "string", "description": "描述" },
      "field2": { "type": "string", "description": "描述" }
    }
  }
}
```

---

## Workflow

When creating a new API:

1. **Implement API** - Create controller and model
2. **Create OpenAPI file** - `docs/openapi.json`
3. **Define schemas** - Use `$ref` for reusable models
4. **Add examples** - Include request/response examples
5. **Import to Apifox** - Upload OpenAPI file

---

## Example: Complete API Documentation

```json
{
  "openapi": "3.0.0",
  "info": {
    "title": "用户中心 - 二维码 API",
    "version": "1.0.0"
  },
  "servers": [{ "url": "/" }],
  "paths": {
    "/api/Qrcode/create": {
      "post": {
        "tags": ["Qrcode"],
        "summary": "创建二维码",
        "requestBody": {
          "required": true,
          "content": {
            "application/json": {
              "schema": {
                "$ref": "#/components/schemas/QrcodeCreateRequest"
              }
            }
          }
        },
        "responses": {
          "200": {
            "description": "成功",
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/QrcodeCreateResponse"
                }
              }
            }
          }
        }
      }
    }
  },
  "components": {
    "schemas": {
      "QrcodeCreateRequest": {
        "type": "object",
        "required": ["scene_str"],
        "properties": {
          "scene_str": {
            "type": "string",
            "description": "场景值",
            "maxLength": 64
          }
        }
      },
      "QrcodeCreateData": {
        "type": "object",
        "properties": {
          "qrcode_url": { "type": "string", "format": "uri" },
          "expire_at": { "type": "string", "format": "date-time" }
        }
      },
      "QrcodeCreateResponse": {
        "type": "object",
        "properties": {
          "status": { "type": "integer", "enum": [1] },
          "info": { "type": "string" },
          "data": { "$ref": "#/components/schemas/QrcodeCreateData" }
        }
      }
    }
  }
}
```

---

## Related Rules

- [Response Format](api-response-format.md) - Standard JSON response format
- [API Controllers Reference](../../references/api-controllers.md) - RESTful API development
