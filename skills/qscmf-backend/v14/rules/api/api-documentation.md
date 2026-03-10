---
title: API Documentation (v14)
impact: MEDIUM
impactDescription: OpenAPI/Apifox documentation generation
tags: api, documentation, openapi, apifox, v14
---

## API Documentation (v14)

OpenAPI/Apifox documentation generation for QSCMF v14 API endpoints.

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
      "url": "/"
    }
  ],
  "tags": [
    {
      "name": "ModuleName",
      "description": "模块描述"
    }
  ],
  "paths": {
    "/api/ModuleName/action": {
      "post": {
        "tags": ["ModuleName"],
        "summary": "操作描述",
        "requestBody": {
          "required": true,
          "content": {
            "application/json": {
              "schema": {
                "$ref": "#/components/schemas/RequestModel"
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
                  "$ref": "#/components/schemas/ResponseModel"
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
      // Define reusable schemas here
    }
  }
}
```

---

## QSCMF Response Format

All QSCMF APIs use standard response format:

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
  }
}
```

---

## API Path Convention

QSCMF RestController uses RESTful routing:

```
/Api/{ResourceName}
```

HTTP Method → Controller Method mapping:
| HTTP Method | URI | Controller Method |
|-------------|-----|-------------------|
| GET | `/Api/OaQrcode` | `gets()` |
| POST | `/Api/OaQrcode` | `create()` |
| PUT | `/Api/OaQrcode/{id}` | `update()` |
| DELETE | `/Api/OaQrcode/{id}` | `delete()` |

**Note:** Don't include method name in URI. The framework routes based on HTTP verb.

---

## Example: Complete API Documentation

```json
{
  "openapi": "3.0.0",
  "info": {
    "title": "用户中心 - 公众号二维码 API",
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
