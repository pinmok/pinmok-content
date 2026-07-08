# <img src="https://www.pinmok.com/assets/img/pinmok.bg.svg" height="60" alt="Pinmok"> Pinmok Content

[![Python](https://img.shields.io/badge/Python-3.12+-blue)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-lightgrey)](LICENSE)

[English](#english) | [简体中文](#简体中文)

---

## English

pinmok-content is the official content module for [Pinmok](https://www.pinmok.com), providing article, category, and page management, along
with matching frontend display support.

### Installation

```bash
pip install pinmok-content
```

### Quick Start

**1. Add to `INSTALLED_APPS`**

Add `pinmok.content` after `pinmok.padmin`.

```python
INSTALLED_APPS = [
    ...
    'pinmok.padmin',
    'pinmok.content',  # must come after pinmok.padmin
]
```

**2. Configure URLs**

```python
from django.urls import path, include

urlpatterns = [
    ...
    path('', include('pinmok.content.urls')),
]
```

**3. Run migrations**

```bash
python manage.py migrate
```

**4. Sync menus**

After completing the steps above, a **Pinmok Content** menu item will automatically appear in the admin, with entries for articles,
categories, and more underneath. At this point, the menu is auto-generated from the Django app name and has no icons. After running a menu
sync, the menu will read from the configuration and correctly display localized names and icons.

### Features

#### Content Management

Full admin management for Articles, Pages, and Categories, with support for multi-language translation, status workflow (draft, in review,
published, withdrawn), featured/pinned flags, and multimedia assets (images, attachments, video, audio).

Pages share the same data structure as Articles and are suited for standalone static content that doesn't need to belong to a category.

#### Theme & Templates

pinmok-content is fully integrated with the Pinmok theme system — the frontend is driven by theme templates. Built-in template tags cover
common use cases like article lists, featured content, and category navigation, so theme developers can pull content straight into a
template with a single tag — no backend code or Python required. Switching themes changes the entire site's appearance, while template tags
keep the frontend fully decoupled from the backend. See the theme development docs for template tag usage and theme development.

#### REST API

pinmok-content ships with a built-in read-only REST API, suited for decoupled frontends, mini-programs, and similar scenarios. The API is
mounted under the `/api/` prefix and provides endpoints for article list/detail, category list/detail, with support for common parameters
like pagination, ordering, and category filtering, returning standard JSON.

Authentication and rate limiting are left to be configured at the project level.

### Requirements

| Dependency | Version |
|------------|---------|
| Python     | >= 3.12 |
| Pinmok     | >= 1.0  |

The required Django version follows whatever Pinmok requires, so it isn't pinned separately here.

### Contributing

Issues and pull requests are welcome. If you find this project useful, a star on the repository goes a long way for an independently
developed open-source project.

- GitHub: [github.com/pinmok/pinmok-content](https://github.com/pinmok/pinmok-content)
- Gitee: [gitee.com/pinmok/pinmok-content](https://gitee.com/pinmok/pinmok-content)

---

## 简体中文

pinmok-content 是 [Pinmok](https://www.pinmok.com) 的官方内容模块，提供文章、分类、页面等内容管理功能，以及配套的前端展示支持。

### 安装

```bash
pip install pinmok-content
```

### 快速开始

**1. 添加到 INSTALLED_APPS**

将 `pinmok.content` 添加在 `padmin` 之后。

```python
INSTALLED_APPS = [
    ...
    'pinmok.padmin',
    'pinmok.content',  # 必须在 pinmok.padmin 之后
]
```

**2. 配置 URL**

```python
from django.urls import path, include

urlpatterns = [
    ...
    path('', include('pinmok.content.urls')),
]
```

**3. 执行数据库迁移**

```bash
python manage.py migrate
```

**4. 同步菜单**

完成以上步骤后，后台管理界面会自动出现 **Pinmok Content** 菜单项，文章、分类等管理入口在其下方。但此时菜单由 Django
应用名自动生成，尚未包含图标。执行一次菜单同步后，菜单将从配置中读取，正确显示多语言名称及图标。

### 功能概览

#### 内容管理

提供文章（Article）、页面（Page）、分类（Category）的完整后台管理，支持多语言翻译、状态流转（草稿、审核、发布、撤回）、文章置顶与推荐标记，
以及图片、附件、视频、音频等多媒体资源管理。

页面（Page）与文章共享相同的数据结构，适用于无需挂载分类的独立静态内容页面。

#### 主题与模板

pinmok-content 完全集成 Pinmok 主题系统，前端页面由主题模板驱动。内置的模板标签覆盖文章列表、推荐内容、分类导航等常见场景，
主题开发者只需在模板中调用标签即可获取内容——无需编写任何后端代码，也无需懂 Python。更换主题即可改变整站风格，而模板标签则让前端与后端彻底解耦。
模板标签的使用方式及主题开发方法，请参考主题开发文档。

#### REST API

pinmok-content 内置只读 REST API，适用于前后端分离、小程序等场景。API 挂载在 `/api/` 前缀下，提供文章列表、文章详情、分类列表、
分类详情等接口，支持分页、排序、分类筛选等常用参数，返回标准 JSON 格式。

接口鉴权与访问频率限制由项目层自行配置即可。

### 依赖

| 依赖     | 版本      |
|--------|---------|
| Python | >= 3.12 |
| pinmok | >= 1.0  |

Django 版本要求随 pinmok 而定，无需单独指定。

### 参与贡献

欢迎提交 Issue 或 Pull Request。如果觉得有用，去仓库点个 Star 也是实实在在的支持。

- GitHub：[github.com/pinmok/pinmok-content](https://github.com/pinmok/pinmok-content)
- Gitee：[gitee.com/pinmok/pinmok-content](https://gitee.com/pinmok/pinmok-content)