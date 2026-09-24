# 内容管理 API 参考

本章介绍 Pinmok 内容管理系统对外提供的只读 JSON API。这些接口主要用于前端模板渲染、小程序或第三方系统调用。

??? abstract "快速开始"

    本章所有接口均挂载在 `api/` 路径下（完整路径取决于项目根路由配置，例如 `/content/api/...`），仅支持 `GET`
    请求，仅返回已发布的文章和已启用的分类。
    
    | 接口 | 地址 | 参数 |
    | --- | --- | --- |
    | 文章列表 | `api/list/` | URL 参数: `category`, `page`, `page_size`, `order`, `top`, `recommended` |
    | 文章详情 | `api/article/<uuid>/` | 路径参数: `uuid` |
    | 单页详情 | `api/page/<uuid>/` | 路径参数: `uuid` |
    | 分类列表 | `api/categories/` | 无 |
    | 分类详情 | `api/category/<uuid>/` | 路径参数: `uuid` |
    
        各接口的详细参数说明与返回示例见下文。

## API 使用说明

### 响应格式

所有接口均返回标准的 JSON 格式，包含 `code`、`message` 和 `data` 三个字段。

**成功响应示例**

```json
{
  "code": 0,
  "message": "Success",
  "data": {
    ...
  }
}
```

**错误响应示例**

```json
{
  "code": 40001,
  "message": "Invalid category UUID.",
  "data": {}
}
```

### 业务状态码 (code)

| 状态码 | 含义                       | HTTP 状态码 |
|--------|----------------------------|-------------|
| 0      | 成功                       | 200 OK      |
| 40001  | 请求参数错误 (Bad Request) | 400         |
| 40404  | 资源未找到 (Not Found)     | 404         |

!!! tip "提示"

    前端在调用接口时，建议优先判断 `code` 是否为 `0`，而不是仅依赖 HTTP 状态码，以便获取更精确的业务错误信息（如区分是
    UUID 格式错误还是资源不存在）。

## 获取分类列表

获取所有已启用的分类，按 `sort_order` 升序排列。

**接口地址**：`GET api/categories/`

**调用参数**：无

**返回示例**

```json
{
  "code": 0,
  "message": "Success",
  "data": {
    "items": [
      {
        "uuid": "e20cb724-8320-4c25-9a83-8f34e2ff4465",
        "name": "企业新闻",
        "description": "",
        "cover": "",
        "parent": null,
        "sort_order": 10000
      },
      {
        "uuid": "1440868d-67a5-4538-9593-3a9c50c1e762",
        "name": "产品列表",
        "description": "",
        "cover": "",
        "parent": null,
        "sort_order": 10000
      }
    ]
  }
}
```

## 获取分类详情

根据 UUID 获取单个分类的详细信息。

**接口地址**：`GET` `api/category/<uuid:uuid>/`

**调用参数**：

| 参数名 | 位置 | 必填 | 说明             |
|--------|------|------|------------------|
| uuid   | Path | 是   | 分类的唯一标识符 |

**返回示例**

```json
{
  "code": 0,
  "message": "Success",
  "data": {
    "uuid": "e20cb724-8320-4c25-9a83-8f34e2ff4465",
    "name": "企业新闻",
    "description": "",
    "cover": "",
    "parent": null,
    "sort_order": 10000
  }
}
```

**错误示例 (40404)**：`{"code": 40404, "message": "Category not found.", "data": {}}`

## 获取文章列表

获取已发布的文章列表，支持分页、分类筛选、排序及特殊标记过滤。

**接口地址**：`GET api/list/`

**调用参数 (Query)**：

| 参数名      | 类型   | 必填 | 默认值        | 说明                                                                                                                            |
|-------------|--------|------|---------------|---------------------------------------------------------------------------------------------------------------------------------|
| category    | string | 否   | -             | 分类 UUID。支持逗号分隔传入多个（如 `uuid1,uuid2`）。格式错误返回 `40001`                                                       |
| page        | int    | 否   | 1             | 页码，从 1 开始。非整数返回 `40001`                                                                                             |
| page_size   | int    | 否   | 10            | 每页条数，范围 1-100。非整数返回 `40001`                                                                                        |
| order       | string | 否   | -published_at | 排序字段。允许值：`published_at`, `-published_at`, `created_at`, `-created_at`, `sort_order`, `-sort_order`。非法值返回 `40001` |
| top         | string | 否   | -             | 传 `"1"` 时仅返回置顶文章                                                                                                       |
| recommended | string | 否   | -             | 传 `"1"` 时仅返回推荐文章                                                                                                       |

**返回示例**

```json
{
  "code": 0,
  "message": "Success",
  "data": {
    "items": [
      {
        "uuid": "2e1859cc-137c-480f-9a23-4b7bb041fe5a",
        "title": "Pinmok 正式发布了",
        "summary": "基于 Django 快速开发平台 Pinmok 正式发布 1.0 版本，该平台全兼容 Django 开发习惯，学习成本极低。",
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

## 获取文章详情

根据 UUID 获取单篇文章的完整内容，包含富文本正文及关联的媒体资源。

**接口地址**：`GET api/article/<uuid:uuid>/`

**调用参数**：

| 参数名 | 位置 | 必填 | 说明             |
|--------|------|------|------------------|
| uuid   | Path | 是   | 文章的唯一标识符 |

**返回示例**

```json
{
  "code": 0,
  "message": "Success",
  "data": {
    "uuid": "2e1859cc-137c-480f-9a23-4b7bb041fe5a",
    "title": "Pinmok 正式发布了",
    "summary": "基于 Django 快速开发平台 Pinmok 正式发布 1.0 版本，该平台全兼容 Django 开发习惯，学习成本极低。",
    "cover": "/media/2026/09/59467dae22e24770aec8a55aeab1998a.jpg",
    "is_top": false,
    "is_recommended": true,
    "published_at": "2026-07-04T09:14:52.863591+00:00",
    "categories": [
      "1440868d-67a5-4538-9593-3a9c50c1e762"
    ],
    "content": "<p>文章正式内容，支持html格式。</p>",
    "gallery": [
      {
        "url": "/media/2026/08/689aa4f3bb9c42189f28db3855938fbb.png",
        "original_name": "画板 1.png",
        "alt": ""
      }
    ],
    "attachments": [
      {
        "url": "/media/2026/09/a0bc55eb209249e486a7f1ee307b0cad.docx",
        "original_name": "V1.0版本遗留问题迭代记录（成品案例）.docx",
        "alt": "下载文件"
      }
    ],
    "videos": [],
    "audios": []
  }
}
```

**错误示例 (40404)**：`{"code": 40404, "message": "Article not found.", "data": {}}`

## 获取单页详情

单页（Page）在底层与文章共用数据模型（`ArticleType.PAGE`），但不归属任何分类，通常用于“关于我们”、“联系方式”等独立页面。

根据 UUID 获取单页的完整内容。

**接口地址**：`GET api/page/<uuid:uuid>/`

**调用参数**：

| 参数名 | 位置 | 必填 | 说明             |
|--------|------|------|------------------|
| uuid   | Path | 是   | 单页的唯一标识符 |

**返回示例**

```json
{
  "code": 0,
  "message": "Success",
  "data": {
    "uuid": "3de7501f-83d7-48d2-bff1-a83b55de3bd4",
    "title": "单页文章",
    "summary": "单页文章摘要",
    "cover": "",
    "is_top": false,
    "is_recommended": false,
    "published_at": "2026-07-04T09:16:34.021043+00:00",
    "categories": [],
    "content": "<p>单页文章内容</p>",
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

**错误示例 (40404)**：`{"code": 40404, "message": "Page not found.", "data": {}}`