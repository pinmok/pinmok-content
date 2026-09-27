<p align="center">
  <img src="https://www.pinmok.com/assets/img/pinmok.bg.svg" height="60" alt="Pinmok">
</p>

# Pinmok Content

[![Python 3.12+](https://img.shields.io/badge/Python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-lightgrey.svg)](https://opensource.org/licenses/MIT)
[![Pinmok 1.0+](https://img.shields.io/badge/Pinmok-1.0+-green.svg)](https://www.pinmok.com)

[English](#english) | [简体中文](#简体中文)

---

<a id="english"></a>

## English

**Pinmok Content** is the official content management module for the [Pinmok](https://www.pinmok.com) framework. It provides article,
category, and page management, along with frontend display support tailored for corporate websites, blogs, and small-to-medium content
sites.

### Features

- **Content Management**: Full admin support for Articles, Pages, and Categories, including multi-language translation, status workflows,
  and multimedia assets.
- **Theme-Driven Frontend**: Deeply integrated with the Pinmok theme system. Built-in template tags and a Data Source mechanism allow
  frontend developers to build content-driven pages without writing backend Python code in most common scenarios.
- **Independent Multimedia Resources**: Galleries, attachments, videos, and audios are stored independently from the main content, allowing
  multiple language versions to share the same resource files.
- **REST API**: Provides a built-in read-only REST API for content retrieval, supporting pagination, ordering, and filtering, suitable for
  decoupled frontends or mini-programs.

### Installation

> **Prerequisite**: You must have the core `pinmok` framework installed first.

**1. Install the package**

```bash
pip install pinmok-content
```

**2. Add to `INSTALLED_APPS`**
Add `pinmok.content` **after** `pinmok.padmin` in your `settings.py`:

```python
INSTALLED_APPS = [
    'pinmok.padmin',
    'pinmok.content',  # Must come after pinmok.padmin
    ...
]
```

**3. Configure URLs**
Include the content URLs in your project's `urls.py`:

```python
from django.urls import path, include

urlpatterns = [
    ...,
    path('', include('pinmok.content.urls')),
]
```

**4. Run Migrations & Sync Menus**

```bash
python manage.py migrate
```

After running migrations, a "Pinmok Content" menu will appear in the admin panel. Run a menu sync (via admin dashboard or management
command) to correctly display localized names and icons.

### Quick Usage

Once installed, you can fetch and display content directly in your Django templates using declarative tags:

```django
{% load content_tags %}

<!-- Fetch the latest 5 articles from a specific category -->
{% articles category=category.uuid limit=5 as latest %}

{% for article in latest %}
    <h2>{{ article.translation.title }}</h2>
{% endfor %}
```

### Documentation

For detailed information on theme development, template tags, data sources, and REST API usage, please refer to
the [Pinmok Official Documentation](https://www.pinmok.com).

### Contributing

Issues and pull requests are welcome. If you find this project useful, feel free to give it a star.

- **GitHub**: [github.com/pinmok/pinmok-content](https://github.com/pinmok/pinmok-content)
- **Gitee**: [gitee.com/pinmok/pinmok-content](https://gitee.com/pinmok/pinmok-content)

---

<a id="简体中文"></a>

## 简体中文

**Pinmok Content** 是 [Pinmok](https://www.pinmok.com) 框架的官方内容管理模块。提供文章、分类、页面管理功能，以及配套的前端展示支持，适用于企业官网、博客及中小型内容站点。

### 核心特性

- **内容管理**：提供文章、页面、分类的完整后台管理，支持多语言翻译、状态流转以及多媒体资源管理。
- **主题驱动的前端**：深度集成 Pinmok 主题系统。内置的模板标签与数据源机制，使得前端开发者在大多数常见场景下，无需编写后端 Python 代码即可构建内容展示页面。
- **独立的多媒体资源**：图集、附件、视频、音频独立于正文存储，支持多语言版本共享同一套资源文件，节省存储空间。
- **REST API**：提供内置的只读 REST API 接口，支持分页、排序和筛选，适用于前后端分离或小程序场景。

### 安装

> **前置条件**：必须先安装 `pinmok` 核心框架。

**1. 安装扩展包**

```bash
pip install pinmok-content
```

**2. 注册应用**
在 `settings.py` 的 `INSTALLED_APPS` 中，将 `pinmok.content` 添加在 `pinmok.padmin` **之后**：

```python
INSTALLED_APPS = [
    'pinmok.padmin',
    'pinmok.content',  # 必须在 pinmok.padmin 之后
    ...
]
```

**3. 配置路由**
在项目的 `urls.py` 中引入内容模块路由：

```python
from django.urls import path, include

urlpatterns = [
    ...,
    path('', include('pinmok.content.urls')),
]
```

**4. 执行迁移与同步菜单**

```bash
python manage.py migrate
```

完成迁移后，后台管理界面会出现 Pinmok Content 菜单。请执行一次菜单同步操作，以正确显示多语言名称及图标。

### 快速使用

安装完成后，您可以直接在 Django 模板中使用声明式标签获取并展示内容：

```django
{% load content_tags %}

<!-- 获取指定分类下最新的 5 篇文章 -->
{% articles category=category.uuid limit=5 as latest %}

{% for article in latest %}
    <h2>{{ article.translation.title }}</h2>
{% endfor %}
```

### 文档

有关主题开发、模板标签、数据源和 REST API 的详细说明，请参阅 [Pinmok 官方文档](https://www.pinmok.com)。

### 参与贡献

欢迎提交 Issue 或 Pull Request。如果觉得这个项目有用，欢迎给仓库点个 Star。

- **GitHub**：[github.com/pinmok/pinmok-content](https://github.com/pinmok/pinmok-content)
- **Gitee**：[gitee.com/pinmok/pinmok-content](https://gitee.com/pinmok/pinmok-content)
