# Content Management API Reference

This chapter introduces the read-only JSON APIs provided by the Pinmok Content Management System. These interfaces are
primarily used for frontend template rendering, mini-program integration, or third-party system integration.

??? abstract "Quick Start"

    All interfaces in this chapter are mounted under the `api/` path (the full path depends on the project's root route configuration, e.g., `/content/api/...`), support only `GET` requests, and return only published articles and enabled categories.

    | Interface | Endpoint | Parameters |
    | --- | --- | --- |
    | Article List | `api/list/` | URL params: `category`, `page`, `page_size`, `order`, `top`, `recommended` |
    | Article Detail | `api/article/<uuid>/` | Path param: `uuid` |
    | Page Detail | `api/page/<uuid>/` | Path param: `uuid` |
    | Category List | `api/categories/` | None |
    | Category Detail | `api/category/<uuid>/` | Path param: `uuid` |

    Detailed parameter descriptions and response examples for each interface are provided below.

## API Usage Guide

### Response Format

All interfaces return a standard JSON format containing three fields: `code`, `message`, and `data`.

**Success Response Example**

```json
{
  "code": 0,
  "message": "Success",
  "data": {
    ...
  }
}
```

**Error Response Example**

```json
{
  "code": 40001,
  "message": "Invalid category UUID.",
  "data": {}
}
```

### Business Status Codes (code)

| Status Code | Meaning     | HTTP Status Code |
|-------------|-------------|------------------|
| 0           | Success     | 200 OK           |
| 40001       | Bad Request | 400              |
| 40404       | Not Found   | 404              |

!!! tip "Tip"

    When calling interfaces, the frontend should prioritize checking whether `code` is `0` rather than relying solely on
    HTTP status codes. This provides more precise business error information (e.g., distinguishing between UUID format
    errors and resource not found).

## Get Category List

Retrieves all enabled categories, sorted by `sort_order` in ascending order.

**Endpoint:** `GET` `api/categories/`

**Parameters:** None

**Response Example**

```json
{
  "code": 0,
  "message": "Success",
  "data": {
    "items": [
      {
        "uuid": "e20cb724-8320-4c25-9a83-8f34e2ff4465",
        "name": "Company News",
        "description": "",
        "cover": "",
        "parent": null,
        "sort_order": 10000
      },
      {
        "uuid": "1440868d-67a5-4538-9593-3a9c50c1e762",
        "name": "Product List",
        "description": "",
        "cover": "",
        "parent": null,
        "sort_order": 10000
      }
    ]
  }
}
```

## Get Category Detail

Retrieves detailed information for a single category by UUID.

**Endpoint:** `GET api/category/<uuid:uuid>/`

**Parameters:**

| Parameter | Location | Required | Description                |
|-----------|----------|----------|----------------------------|
| uuid      | Path     | Yes      | Category unique identifier |

**Response Example**

```json
{
  "code": 0,
  "message": "Success",
  "data": {
    "uuid": "e20cb724-8320-4c25-9a83-8f34e2ff4465",
    "name": "Company News",
    "description": "",
    "cover": "",
    "parent": null,
    "sort_order": 10000
  }
}
```

**Error Example (40404):** `{"code": 40404, "message": "Category not found.", "data": {}}`

## Get Article List

Retrieves a list of published articles, supporting pagination, category filtering, sorting, and filtering by special
flags.

**Endpoint:** `GET api/list/`

**Parameters (Query):**

| Parameter   | Type   | Required | Default       | Description                                                                                                                                          |
|-------------|--------|----------|---------------|------------------------------------------------------------------------------------------------------------------------------------------------------|
| category    | string | No       | -             | Category UUID. Supports comma-separated multiple values (e.g., `uuid1,uuid2`). Format errors return `40001`                                          |
| page        | int    | No       | 1             | Page number, starting from 1. Non-integer values return `40001`                                                                                      |
| page_size   | int    | No       | 10            | Items per page, range 1-100. Non-integer values return `40001`                                                                                       |
| order       | string | No       | -published_at | Sort field. Allowed values: `published_at`, `-published_at`, `created_at`, `-created_at`, `sort_order`, `-sort_order`. Invalid values return `40001` |
| top         | string | No       | -             | Set to `"1"` to return only pinned articles                                                                                                          |
| recommended | string | No       | -             | Set to `"1"` to return only recommended articles                                                                                                     |

**Response Example**

```json
{
  "code": 0,
  "message": "Success",
  "data": {
    "items": [
      {
        "uuid": "2e1859cc-137c-480f-9a23-4b7bb041fe5a",
        "title": "Pinmok Officially Released",
        "summary": "Pinmok, a Django-based rapid development platform, has officially released version 1.0. The platform is fully compatible with Django development practices and has a very low learning curve.",
        "cover": "/media/2026/09/59467dae22e24770aec8a55aeab1998a.jpg",
        "is_top": false,
        "is_recommended": true,
        "published_at": "2026-07-04T09:14:52.863591+00:00",
        "categories": [
          "1440868d-67a5-4538-9593-3a9c50c1e762"
        ]
      }
    ],
    "page": 1,
    "page_size": 10,
    "total_pages": 1,
    "total_count": 1
  }
}
```

## Get Article Detail

Retrieves the complete content of a single article by UUID, including the rich text body and associated media resources.

**Endpoint:** `GET api/article/<uuid:uuid>/`

**Parameters:**

| Parameter | Location | Required | Description               |
|-----------|----------|----------|---------------------------|
| uuid      | Path     | Yes      | Article unique identifier |

**Response Example**

```json
{
  "code": 0,
  "message": "Success",
  "data": {
    "uuid": "2e1859cc-137c-480f-9a23-4b7bb041fe5a",
    "title": "Pinmok Officially Released",
    "summary": "Pinmok, a Django-based rapid development platform, has officially released version 1.0. The platform is fully compatible with Django development practices and has a very low learning curve.",
    "cover": "/media/2026/09/59467dae22e24770aec8a55aeab1998a.jpg",
    "is_top": false,
    "is_recommended": true,
    "published_at": "2026-07-04T09:14:52.863591+00:00",
    "categories": [
      "1440868d-67a5-4538-9593-3a9c50c1e762"
    ],
    "content": "<p>Article body content, supports HTML format.</p>",
    "gallery": [
      {
        "url": "/media/2026/08/689aa4f3bb9c42189f28db3855938fbb.png",
        "original_name": "artboard_1.png",
        "alt": ""
      }
    ],
    "attachments": [
      {
        "url": "/media/2026/09/a0bc55eb209249e486a7f1ee307b0cad.docx",
        "original_name": "V1.0_Issue_Tracking_Record_(Case_Studies).docx",
        "alt": "Download File"
      }
    ],
    "videos": [],
    "audios": []
  }
}
```

**Error Example (40404):** `{"code": 40404, "message": "Article not found.", "data": {}}`

## Get Page Detail

Pages share the same underlying data model as articles (`ArticleType.PAGE`), but do not belong to any category. They are
typically used for standalone pages such as "About Us" or "Contact."

Retrieves the complete content of a page by UUID.

**Endpoint:** `GET api/page/<uuid:uuid>/`

**Parameters:**

| Parameter | Location | Required | Description            |
|-----------|----------|----------|------------------------|
| uuid      | Path     | Yes      | Page unique identifier |

**Response Example**

```json
{
  "code": 0,
  "message": "Success",
  "data": {
    "uuid": "3de7501f-83d7-48d2-bff1-a83b55de3bd4",
    "title": "Page Article",
    "summary": "Page article summary",
    "cover": "",
    "is_top": false,
    "is_recommended": false,
    "published_at": "2026-07-04T09:16:34.021043+00:00",
    "categories": [],
    "content": "<p>Page article content</p>",
    "gallery": [
      {
        "url": "/media/2026/07/72e844a9cd06425c9f80989f97631900.png",
        "original_name": "page_image.png",
        "alt": ""
      }
    ],
    "attachments": [],
    "videos": [],
    "audios": []
  }
}
```

**Error Example (40404):** `{"code": 40404, "message": "Page not found.", "data": {}}`