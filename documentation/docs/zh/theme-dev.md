# 主题开发

如果你已经熟悉 Pinmok 主题系统，可以展开 **快速开始**查看 content 应用主题的速查资料。

??? abstract "快速开始"

    本章节面向已了解 Pinmok 主题机制（目录结构、`theme.json`、安装激活）的开发者，提供 content 应用主题的速查信息。

    **最小目录结构**

    一套 content 主题至少包含以下文件。单页模板 `page.html` 是可选的，最小化主题可暂不提供。

    ```text title="目录结构"
    templates/
    └── themes/
        └── mytheme/
            ├── theme.json
            ├── index.html
            ├── index.json
            ├── list.html
            ├── list.json
            ├── article.html
            ├── article.json
            └── page.html          # 可选
    ```


    !!! warning "注意"

        `theme.json` 配置中的 `app_label` 属性，其值必须为字符串 `content`，与应用名对应，Pinmok 才能正确识别为 Content 模板。

    **Action 名称对照**

    模板配置文件中的 `action` 须与对应视图的 URL name 一致。

    | 页面 | Action | URL 地址 |
    |---|---|---|
    | 首页 | `index` | {BASE_URL}/ |
    | 文章分类列表 | `list` | {BASE_URL}/list/<uuid> |
    | 文章详情 | `article` | {BASE_URL}/article/<uuid> |
    | 单页详情 | `page` | {BASE_URL}/page/<uuid> |

    **加载标签库**

    content 主题通常需要同时加载两个标签库：

    ```django
    {% load content_tags pinmok_tags %}
    ```

    `content_tags` 提供文章、分类、分页、状态角标等 content 应用专用功能；`pinmok_tags` 提供站点信息、导航、媒体文件解析、轮播图、友情链接等通用功能。后者在 Pinmok 主题文档中有详细说明，本章直接使用。

    **配置文件格式示例**

    ```json title="theme.json"
    {
      "name": "My Content Theme",
      "app_label": "content",
      "version": "1.0.0",
      "vars": {
        "site_name": {
          "title": "站点名称",
          "type": "text",
          "default": "我的网站"
        }
      }
    }
    ```

    !!! tip "提示"

        定义在 `theme.json` 中的变量为全局变量，所有模板都可以使用。定义在其它模板配置文件中的变量，仅对应模板可用。

    ```json title="index.json"
    {
      "name": "首页",
      "action": "index",
      "vars": {
        "hero_title": {
          "title": "主标题",
          "type": "text",
          "default": "欢迎来到首页"
        }
      },
      "fieldsets": {
        "featured": {
          "title": "精选栏目",
          "vars": {
            "category": {
              "title": "分类",
              "type": "datasource",
              "source": "category"
            },
            "count": {
              "title": "显示数量",
              "type": "number",
              "default": 4
            }
          }
        }
      }
    }
    ```

    ```json title="list.json"
    {
      "name": "文章列表",
      "action": "list",
      "vars": {
        "page_size": {
          "title": "每页数量",
          "type": "number",
          "default": 10
        }
      }
    }
    ```

    ```json title="article.json"
    {
      "name": "文章详情",
      "action": "article"
    }
    ```

    ```json title="page.json"
    {
      "name": "单页详情",
      "action": "page"
    }
    ```

    **content 模板标签速查**

    - 获取某分类的多个文章

        `{% articles category=uuid|list[uuid] limit=N page_num=N page_size=N order='-published_at' top=True recommended=True as var %}`

    - 获取指定文章详细内容

        `{% article uuid=xxx as var %}`

    - 获取单页详细内容

        `{% page uuid=xxx as var %}`

    - 获取单个分类

        `{% category uuid=xxx as var %}`

    - 分页显示

        `{% pagination page_obj wing=4 ul_class='pagination' item_class='page-item' link_class='page-link' active_class='active' disabled_class='disabled' prev_label='«' next_label='»' ellipsis_text='...' %}`

    **content 内置数据源速查**

    在配置文件中声明 `type: "datasource"` 时使用。

    | source | 说明 | 模板中配合使用的标签 |
    |---|---|---|
    | `category` | 所有激活分类的树形数据 | `{% articles category=var ... %}` |
    | `page` | 所有已发布单页的数据 | `{% page uuid=var ... %}` |

    **上下文变量速查**

    以下视图会自动注入业务对象，该对象可以在模板中直接使用 `{{ 变量名.字段 }}` 访问，而不必通过标签获取。

    - **category 对象**（文章分类列表页）例如：`{{ category.translation.name }}`

        | 字段 | 说明 |
        |---|---|
        | `uuid` | 分类唯一标识 |
        | `cover` | 封面图路径，配合 `{% media_url %}` 使用 |
        | `template` | 模板标识，默认 `list` |
        | `is_active` | 是否激活 |
        | `sort_order` | 排序权重 |
        | `parent` | 父分类对象或 `None` |
        | `children` | 子分类关联管理器 |
        | `translation.name` | 分类名称（当前语言） |
        | `translation.description` | 分类描述（当前语言） |

    - **article 对象**（文章详情页）例如：`{{ article.translation.title }}`

        | 字段 | 说明 |
        |---|---|
        | `uuid` | 唯一标识 |
        | `type` | 类型：`article` 或 `page` |
        | `template` | 模板标识，默认 `article` |
        | `cover` | 封面图路径 |
        | `status` | 状态字符串 |
        | `sort_order` | 排序权重 |
        | `extra` | 扩展 JSON 数据 |
        | `is_top` | 是否置顶 |
        | `is_recommended` | 是否推荐 |
        | `published_at` | 发布时间 |
        | `created_at` | 创建时间 |
        | `updated_at` | 更新时间 |
        | `categories` | 所属分类（ManyToMany） |
        | `translation.title` | 标题 |
        | `translation.subtitle` | 副标题 |
        | `translation.summary` | 摘要 |
        | `translation.content` | 正文内容 |
        | `gallery` | 图集资源列表 |
        | `attachments` | 附件资源列表 |
        | `videos` | 视频资源列表 |
        | `audios` | 音频资源列表 |

    - **page 对象**（单页详情页）例如：`{{ page.translation.title }}`

        字段与 `article` 完全一致，将 `article` 替换为 `page` 即可。单页通常不使用置顶、推荐等业务属性，但字段结构与文章完全一致。

    **最小可用主题完整示例**

    ```html title="index.html"
    {% load content_tags pinmok_tags %}
    <!DOCTYPE html>
    <html>
    <head><title>{{ site_name }}</title></head>
    <body>
      <h1>{{ hero_title }}</h1>

      {% if featured.category %}
        {% category uuid=featured.category as feat_cat %}
        {% if feat_cat %}
          <h2>{{ feat_cat.translation.name }}</h2>
          {% articles category=feat_cat.uuid limit=featured.count as feat_articles %}
          {% if feat_articles %}
            <ul>
              {% for art in feat_articles %}
              <li>
                <a href="{% url 'article' art.uuid %}">
                  {{ art.translation.title }}
                </a>
              </li>
              {% endfor %}
            </ul>
          {% endif %}
        {% endif %}
      {% endif %}
    </body>
    </html>
    ```

    ```html title="list.html"
    {% load content_tags pinmok_tags %}
    <h1>{{ category.translation.name }}</h1>
    {% if category.translation.description %}
      <p>{{ category.translation.description }}</p>
    {% endif %}

    {% articles category=category.uuid page_num=request.GET.page|default:1 page_size=page_size as paged %}
    {% if paged %}
      {% for art in paged %}
      <article>
        <h2><a href="{% url 'article' art.uuid %}">{{ art.translation.title }}</a></h2>
        {% if art.translation.summary %}<p>{{ art.translation.summary }}</p>{% endif %}
      </article>
      {% endfor %}
      {% pagination paged %}
    {% endif %}
    ```

    ```html title="article.html"
    {% load content_tags pinmok_tags %}
    <article>
      {% if article.cover %}
        {% media_url article.cover as cover_url %}
        <img src="{{ cover_url }}" alt="{{ article.translation.title }}">
      {% endif %}

      <h1>{{ article.translation.title }}</h1>
      {% if article.translation.subtitle %}<p>{{ article.translation.subtitle }}</p>{% endif %}

      <time>{{ article.published_at|date:"Y-m-d" }}</time>

      {% if article.translation.content %}
        <div>{{ article.translation.content|safe }}</div>
      {% endif %}

      {% if article.gallery %}
      <div class="gallery">
        {% for res in article.gallery %}
          {% media_url res.resource.url as img_url %}
          <img src="{{ img_url }}" alt="{{ res.alt }}">
        {% endfor %}
      </div>
      {% endif %}
    </article>
    ```

    ```html title="page.html"
    {% load content_tags pinmok_tags %}
    <article>
      <h1>{{ page.translation.title }}</h1>
      {% if page.translation.content %}
        <div>{{ page.translation.content|safe }}</div>
      {% endif %}
    </article>
    ```

## 1. 概述

本章面向前端开发人员——你需要掌握 HTML/CSS 和 Django 模板语法（`{% %}` 与 `{{ }}`），不需要编写 Python 代码。

content 应用的主题开发遵循 Pinmok 通用主题机制：主题是一个包含 `theme.json`、HTML 模板及 JSON 配置文件的目录，放在 Django
模板搜索路径下的 `themes/` 文件夹中即可被识别。关于主题目录结构、`theme.json` 编写规范、安装激活流程、 变量注入原理、多语言配置规则等内容，参见
Pinmok 主题文档。本章只讲解 content 应用特有的约定，包括模板标签、 视图注入的上下文变量以及内置数据源。

content 应用提供四种前端页面：

| 页面         | 说明                           |
|--------------|--------------------------------|
| 首页         | 站点入口，通常聚合多个内容模块 |
| 文章分类列表 | 展示某个分类下的文章，带分页   |
| 文章详情     | 展示一篇完整的文章             |
| 单页详情     | 展示"关于我们"等独立页面       |

模板开发人员可先编写静态 HTML，再改造为动态模板。

在模板中通常需要同时加载两个标签库：

```django
{% load content_tags pinmok_tags %}
```

`content_tags` 是本章的核心，提供文章查询、分类查询、分页、状态角标等 content 专用功能。`pinmok_tags`
提供站点信息、导航、媒体文件解析、轮播图、友情链接等框架级通用功能，本章在示例中直接使用，不做展开。

!!! note "Django 模板标准语法完全适用"

    模板继承（`{% extends %}`）、包含（`{% include %}`）、条件判断、循环等均为标准 Django 模板语法，Pinmok
    未做任何限制或修改，只要 Django 支持的，这里都支持。

### 1.1 模板配置文件

每套主题必须包含一个核心描述文件 theme.json，其余配置文件视实际需求可选配。具体配置规则如下：

- **基础规则**：若模板无需定义自定义变量，可省略其对应的配置文件。
- **多模板规则**：若单个 Action 关联多个模板，除默认模板外，其余扩展模板均必须提供独立的配置文件。
- **配置示例**：假设“文章详情页”的默认模板为 `article.html`，若需新增自定义模板 `article_special.html`，则必须创建
  article_special.json，并在其中显式声明 `"action": "article"` 以建立路由映射。

### 1.2 模板标签

Content 模块内置了以下核心模板标签（Template Tags），用于在视图中获取并渲染数据：

- **`{% articles %}`**：查询指定分类下的文章列表，支持通过传入参数进行条件过滤与配置。
- **`{% pagination %}`**：通用分页导航渲染标签，用于将上下文中的分页对象（page_obj）渲染为 HTML 分页控件。
- **`{% article %}`**：获取并渲染指定文章的完整详情数据。
- **`{% page %}`**：获取并渲染指定单页（Page）的完整详情数据。
- **`{% category %}`**：获取并渲染指定分类的详细信息。

### 1.3 URL 定义

本节定义了系统的 URL 路由规范。理解这些路由对于在模板中生成正确的超链接（例如 `<a href="...">`）至关重要。

| 页面         | Action    | URL 路径                    |
|--------------|-----------|-----------------------------|
| 首页         | `index`   | `{BASE_URL}/`               |
| 文章分类列表 | `list`    | `{BASE_URL}/list/<uuid>`    |
| 文章详情     | `article` | `{BASE_URL}/article/<uuid>` |
| 单页详情     | `page`    | `{BASE_URL}/page/<uuid>`    |

- **`{BASE_URL}`**：代表网站的根域名（例如：`https://www.pinmok.com`）。
- **动态参数（`<uuid>`）**：在实际模板中，`<uuid>` 是一个占位符，必须被替换为具体对象的真实 UUID 或 ID。

!!! warning "开发避坑：主题初始化时的链接报错问题"

    URL 路径中的动态参数（如 `<uuid>`） **绝不能为空**。

    当主题刚安装且后台数据库尚无数据时，从数据源获取的变量将为空或 `None`。尝试使用空参数生成 URL 会导致路由失败，
    进而引发 **500 内部服务器错误**。

    **解决方案**：在模板中务必采用防御性编程。在生成链接的逻辑外层包裹 `{% if %}` 判断，确保数据及其参数存在后再进行渲染。

    **示例：**

    ```html
    <!-- ❌ 错误示范：'news.category' 是配置文件中定义的数据源变量，默认值为 None，可能会导致 500 错误 -->
    <a href="{% url 'list' news.category %}">阅读更多</a>
    
    <!-- ✅ 最佳实践：先检查数据是否存在 -->
    {% if news.category %}
      <a href="{% url 'list' news.category %}">阅读更多</a>
    {% endif %}
    ```

## 2. 首页模板开发

首页是 content 主题中工作量最大的页面。与其他页面不同，首页视图 **不注入任何上下文**，页面上的所有内容都需要通过模板标签主动获取。

### 2.1 首页的特殊性

轮播图、导航、站点信息、友情链接等通用模块由 `pinmok_tags` 提供，参见 Pinmok 文档，本章示例中直接使用。文章列表、置顶内容、
推荐内容、指定分类内容等由 `content_tags` 的 `{% articles %}` 标签获取。首页的配置文件除了定义普通变量外，通常会使用
**数据源**来让后台管理员选择具体的业务数据来源。

### 2.2 编写配置文件：index.json

#### 普通变量

```json title="index.json"
{
  "name": "首页",
  "action": "index",
  "vars": {
    "hero_title": {
      "title": "主标题",
      "type": "text",
      "default": "欢迎来到首页"
    }
  }
}
```

示例中定义了一个变量 `hero_title`，文本类型，默认值为 `欢迎来到首页`。用户可以在后台输入其它内容来覆盖默认值。该变量在模板中
可以通过 `{{ hero_title }}` 调用。

#### 数据源变量

数据源类型的变量用于在后台配置界面中提供下拉选择，让管理员指定一个具体的分类或单页，而不是让前端写死 UUID。

```json title="index.json（含数据源）"
{
  "name": "首页",
  "action": "index",
  "vars": {
    "hero_title": {
      "title": "主标题",
      "type": "text",
      "default": "欢迎来到首页"
    }
  },
  "fieldsets": {
    "featured": {
      "title": "精选栏目",
      "vars": {
        "news": {
          "title": "新闻",
          "type": "datasource",
          "source": "category",
          "multiple": true
        },
        "count": {
          "title": "显示数量",
          "type": "number",
          "default": 4
        }
      }
    },
    "about": {
      "title": "关于我们",
      "vars": {
        "about_us": {
          "title": "选择单页",
          "type": "datasource",
          "source": "page"
        }
      }
    }
  }
}
```

该示例中定义了两个数据源类型变量：

- `news`：数据源为 `category`，并设置 `multiple: true` 允许多选。后台配置模板时，该变量会显示所有分类下拉列表，用户可选择多个分类。使用时通过标签调用，例：
  `{% articles category=featured.news ... %}`，模板执行时会从变量 `news` 中获取用户配置的分类 UUID 列表，取出这些分类下的文章。
- `about_us`：数据源为 `page`。后台配置模板时，下拉列表中会显示所有单页文章标题，供用户指定。使用时通过标签调用，例：
  `{% page uuid=about.about_us ... %}`，模板执行时会从变量 `about_us` 中获取单页文章的 UUID，取出对应的单页文章内容。

### 2.3 编写模板：index.html

首页通常是最复杂的，因此将设计稿拆分为若干动态区块，每个区块匹配对应的模板标签。示例中假设已经配置了文章分类数据源变量。

#### 最新文章列表

使用 `{% articles %}` 标签获取已发布文章，赋值给变量 `latest`。设置 `limit` 参数时，返回普通列表，不启用分页。

```django
{% articles category=featured.news limit=6 order="-published_at" as latest %}
{% if latest %}
<ul>
  {% for art in latest %}
  <li>
    <a href="{% url 'article' art.uuid %}">
      {{ art.translation.title }}
    </a>
  </li>
  {% endfor %}
</ul>
{% endif %}
```

`{% articles %}` 的完整参数如下：

| 参数          | 类型        | 默认值          | 说明                                                       |
|---------------|-------------|-----------------|------------------------------------------------------------|
| `category`    | UUID / list | 必填            | 按分类 UUID 过滤，支持单值或列表                           |
| `limit`       | int         | `None`          | 限制返回数量；设置后禁用分页，返回普通列表                 |
| `page_num`    | int         | `1`             | 页码（从 1 开始）；与 `limit` 互斥                         |
| `page_size`   | int         | `10`            | 每页数量；与 `limit` 互斥                                  |
| `order`       | str         | `-published_at` | 排序字段，可选：`published_at`、`created_at`、`sort_order` |
| `top`         | bool        | `False`         | 仅返回置顶文章                                             |
| `recommended` | bool        | `False`         | 仅返回推荐文章                                             |

#### 置顶文章与推荐文章

```django
{% articles category=featured.news top=True limit=3 as top_articles %}
{% if top_articles %}
<section class="top-news">
  {% for art in top_articles %}
    <h3>{{ art.translation.title }}</h3>
  {% endfor %}
</section>
{% endif %}

{% articles category=featured.news recommended=True limit=4 as rec_articles %}
{% if rec_articles %}
<section class="recommended">
  {% for art in rec_articles %}
    <p>{{ art.translation.title }}</p>
  {% endfor %}
</section>
{% endif %}
```

#### 配合数据源：链接到指定单页

```django
{% if about.about_us %}
  {% page uuid=about.about_us as about_page %}
  {% if about_page %}
    <a href="{% url 'page' about_page.uuid %}">
      {{ about_page.translation.title }}
    </a>
  {% endif %}
{% endif %}
```

### 2.4 完整示例

以下是一份可直接运行的 `index.json` 与 `index.html`。

```json title="index.json"
{
  "name": "首页",
  "action": "index",
  "vars": {
    "hero_title": {
      "title": "主标题",
      "type": "text",
      "default": "欢迎来到首页"
    }
  },
  "fieldsets": {
    "featured": {
      "title": "精选栏目",
      "vars": {
        "news": {
          "title": "选择分类",
          "type": "datasource",
          "source": "category",
          "multiple": true
        },
        "count": {
          "title": "显示数量",
          "type": "number",
          "default": 4
        }
      }
    }
  }
}
```

```django title="index.html"
{% load i18n content_tags pinmok_tags %}
{% site_info as site %}
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <title>{{ site.site_name }}</title>
</head>
<body>

<header>
    <h1>{{ hero_title }}</h1>
</header>

{% if featured.news %}
<section class="latest">
    <h2>{% translate 'Latest Articles' %}</h2>
    {% articles category=featured.news limit=6 order="-published_at" as latest %}
    {% if latest %}
    <ul>
        {% for art in latest %}
        <li>
            <a href="{% url 'article' art.uuid %}">
                {{ art.translation.title }}
            </a>
        </li>
        {% endfor %}
    </ul>
    {% endif %}
</section>
{% endif %}


<footer>
    <p>{{ site.site_name }}</p>
</footer>

</body>
</html>
```

---

## 3. 文章列表页模板开发

文章列表页是指定分类下所有文章的列表，它与首页共用 `{% articles %}` 标签，但会使用分页模式。此外，列表页视图会注入当前分类的
`category` 对象。

### 3.1 category 对象

列表页视图自动将 `category` 对象注入模板上下文，可直接使用：

| 字段                      | 说明                                      |
|---------------------------|-------------------------------------------|
| `uuid`                    | 分类唯一标识                              |
| `cover`                   | 封面图路径，需配合 `{% media_url %}` 使用 |
| `template`                | 模板标识，默认 `list`                     |
| `is_active`               | 是否激活                                  |
| `sort_order`              | 排序权重                                  |
| `parent`                  | 父分类对象或 `None`                       |
| `children`                | 子分类关联管理器                          |
| `translation.name`        | 分类名称（当前语言）                      |
| `translation.description` | 分类描述（当前语言）                      |

```django
<h1>{{ category.translation.name }}</h1>
{% if category.translation.description %}
  <p>{{ category.translation.description }}</p>
{% endif %}
```

### 3.2 分页文章列表

列表页视图只注入 `category` 对象，文章列表由模板通过 `{% articles %}` 标签自行获取。分页参数（如每页数量）来自主题配置文件，
或在模板中硬性指定，视图无法预知这些变量名或数值，因此将查询条件交给模板层组装是最直接的做法。

```django
{% articles category=category.uuid page_num=request.GET.page|default:1 page_size=page_size as paged %}
```

!!! warning "page_num 从 1 开始"

    `page_num` 从 1 开始计数。避免将未过滤的 `request.GET.page` 直接传入，务必通过 `|default:1` 提供默认值，
    防止空字符串或非法值导致异常。

`paged` 为 Django `Page` 对象，常用属性如下：

| 属性                           | 说明           |
|--------------------------------|----------------|
| `paged.object_list`            | 当前页文章列表 |
| `paged.number`                 | 当前页码       |
| `paged.paginator.num_pages`    | 总页数         |
| `paged.has_previous()`         | 是否有上一页   |
| `paged.has_next()`             | 是否有下一页   |
| `paged.previous_page_number()` | 上一页页码     |
| `paged.next_page_number()`     | 下一页页码     |

### 3.3 分页组件

列表页拿到 `Page` 对象后，需要用 `{% pagination %}` 标签渲染分页导航。该标签接收 `Page` 对象，输出分页按钮 HTML。

```django
{% pagination paged %}
```

如果默认样式不满足需求，可以通过参数调整 CSS 类：

```django
{% pagination paged wing=2 ul_class="pagination justify-content-center" %}
```

| 参数             | 类型 | 默认值       | 说明                       |
|------------------|------|--------------|----------------------------|
| `page_obj`       | Page | 必填         | Django 分页对象            |
| `wing`           | int  | `4`          | 当前页两侧各显示的页码数量 |
| `ul_class`       | str  | `pagination` | `<ul>` 元素的 CSS 类       |
| `item_class`     | str  | `page-item`  | `<li>` 元素的 CSS 类       |
| `link_class`     | str  | `page-link`  | `<a>` 元素的 CSS 类        |
| `active_class`   | str  | `active`     | 当前页附加类               |
| `disabled_class` | str  | `disabled`   | 禁用状态附加类             |
| `prev_label`     | str  | `«`          | 上一页按钮文字             |
| `next_label`     | str  | `»`          | 下一页按钮文字             |
| `ellipsis_text`  | str  | `...`        | 省略号文字                 |

### 3.4 完整示例

```json title="list.json"
{
  "name": "文章列表",
  "action": "list",
  "vars": {
    "page_size": {
      "title": "每页数量",
      "type": "number",
      "default": 10
    }
  }
}
```

```html title="list.html"
{% load content_tags pinmok_tags %}

<h1>{{ category.translation.name }}</h1>
{% if category.translation.description %}
<p>{{ category.translation.description }}</p>
{% endif %}

{% articles category=category.uuid page_num=request.GET.page|default:1 page_size=page_size as paged %}
{% if paged %}
<div class="article-list">
    {% for art in paged %}
    <article>
        {% if art.cover %}
        {% media_url art.cover as cover_url %}
        <img src="{{ cover_url }}" alt="{{ art.translation.title }}">
        {% endif %}
        <h2>
            <a href="{% url 'article' art.uuid %}">
                {{ art.translation.title }}
            </a>
        </h2>
        {% if art.translation.summary %}
        <p>{{ art.translation.summary }}</p>
        {% endif %}
    </article>
    {% endfor %}
</div>

{% pagination paged %}

{% else %}
<p>该分类下暂无文章。</p>
{% endif %}
```

---

## 4. 文章详情页模板开发

文章详情页用于展示一篇完整的文章内容。与列表页不同，详情页视图会自动注入 `article` 对象，模板中直接使用即可，不需要写标签去获取。

### 4.1 article 对象可用字段

视图注入的 `article` 对象包含文章主表字段、当前语言翻译内容，以及服务层附加的资源分组字段。模板中可按以下字段访问：

| 字段                   | 说明                       |
|------------------------|----------------------------|
| `uuid`                 | 唯一标识                   |
| `type`                 | 类型：`article` 或 `page`  |
| `template`             | 模板标识，默认 `article`   |
| `cover`                | 封面图路径（ImageField）   |
| `status`               | 状态字符串                 |
| `sort_order`           | 排序权重                   |
| `extra`                | 扩展 JSON 数据             |
| `is_top`               | 是否置顶                   |
| `is_recommended`       | 是否推荐                   |
| `published_at`         | 发布时间                   |
| `created_at`           | 创建时间                   |
| `updated_at`           | 更新时间                   |
| `categories`           | 所属分类（ManyToMany）     |
| `translation.title`    | 标题                       |
| `translation.subtitle` | 副标题                     |
| `translation.summary`  | 摘要                       |
| `translation.content`  | 正文内容                   |
| `gallery`              | 图集资源列表（服务层附加） |
| `attachments`          | 附件资源列表               |
| `videos`               | 视频资源列表               |
| `audios`               | 音频资源列表               |

### 4.2 内容与元数据输出

文章详情页通常需要展示标题、发布时间、正文等基本信息：

```django
<article>
  <h1>{{ article.translation.title }}</h1>

  {% if article.translation.subtitle %}
    <p class="subtitle">{{ article.translation.subtitle }}</p>
  {% endif %}

  <time>{{ article.published_at|date:"Y-m-d H:i" }}</time>

  {% if article.translation.content %}
    <div class="content">
      {{ article.translation.content|safe }}
    </div>
  {% endif %}
</article>
```

!!! warning "正文输出过滤"

    content 应用的后台编辑器为富文本编辑器，article.translation.content 中存储的是包含 HTML 标签的原始内容。
    模板中输出时必须使用 |safe 过滤器，否则 HTML 标签会被转义为文本显示在页面上。

### 4.3 封面图

如果文章上传了封面图，通常在标题上方或侧栏展示：

```django
{% if article.cover %}
  {% media_url article.cover as cover_url %}
  <img src="{{ cover_url }}" alt="{{ article.translation.title }}">
{% endif %}
```

### 4.4 资源处理

content 应用将文章资源（图集、附件、视频、音频）独立存储在资源关联表中，不混入正文。这样设计的目的是支持多语言：
切换语言时正文内容变化，但资源文件无需重复上传，所有语言版本共享同一套资源。

服务层在获取文章详情时，会按用途将资源预取并归类为四个列表：

| 属性                  | 说明                             |
|-----------------------|----------------------------------|
| `article.gallery`     | 图集资源（`usage="gallery"`）    |
| `article.attachments` | 附件资源（`usage="attachment"`） |
| `article.videos`      | 视频资源（`usage="video"`）      |
| `article.audios`      | 音频资源（`usage="audio"`）      |

模板中根据资源类型分别渲染即可。

#### 图集渲染

图集通常以图片网格或轮播形式展示在正文下方：

```django
{% if article.gallery %}
<div class="gallery">
  {% for res in article.gallery %}
    {% media_url res.resource.url as img_url %}
    <img src="{{ img_url }}" alt="{{ res.alt }}">
  {% endfor %}
</div>
{% endif %}
```

#### 附件列表

附件通常以可下载链接形式展示：

```django
{% if article.attachments %}
<ul class="attachments">
  {% for res in article.attachments %}
    <li>
      <a href="{% media_url res.resource.url %}" download>
        {{ res.resource.title|default:res.alt }}
      </a>
    </li>
  {% endfor %}
</ul>
{% endif %}
```

#### 视频

```django
{% if article.videos %}
  {% for res in article.videos %}
    {% media_url res.resource.url as video_url %}
    <video src="{{ video_url }}" controls></video>
  {% endfor %}
{% endif %}
```

#### 音频

```django
{% if article.audios %}
  {% for res in article.audios %}
    {% media_url res.resource.url as audio_url %}
    <audio src="{{ audio_url }}" controls></audio>
  {% endfor %}
{% endif %}
```

!!! note "资源字段说明"

    `res.alt` 为文章资源表字段，用于资源加载失败时的替代文本，信息由后台录入。

    `res.resource` 为 Pinmok Resource 模型实例，常见可用字段有：

    |字段|类型|含义|
    |---|---|---|
    |url|字符串|资源的存储相对地址，需要转换成实际地址|
    |original_name|字符串|资源上传时的原始文件名|
    |size|整数|文件大小|
    |file_type|字符串|文件类型，取值为：image、video、audio、document、archive|
    |created_at|时间|上传时间，格式为：2026-08-17 01:12:48.487793|

### 4.5 分类归属

文章可能属于多个分类，在详情页底部展示分类入口是常见做法：

```django
{% if article.categories.exists %}
  <div class="categories">
    {% for cat in article.categories.all %}
      <a href="{% url 'list' cat.uuid %}">
        {{ cat.translation.name }}
      </a>
    {% endfor %}
  </div>
{% endif %}
```

### 4.6 完整示例

```json title="article.json"
{
  "name": "文章详情",
  "action": "article"
}
```

```html title="article.html"
{% load content_tags pinmok_tags %}

<article class="article-detail">

    {% if article.cover %}
    <figure class="cover">
        <img src="{% media_url article.cover %}" alt="{{ article.translation.title }}">
    </figure>
    {% endif %}

    <header>
        <h1>{{ article.translation.title }}</h1>

        {% if article.translation.subtitle %}
        <p class="subtitle">{{ article.translation.subtitle }}</p>
        {% endif %}

        <div class="meta">
            <time>{{ article.published_at|date:"Y-m-d" }}</time>
        </div>
    </header>

    {% if article.translation.content %}
    <div class="content">
        {{ article.translation.content|safe }}
    </div>
    {% endif %}

    {% if article.gallery %}
    <div class="gallery">
        <h3>图集</h3>
        {% for res in article.gallery %}
        {% media_url res.resource.url as img_url %}
        <img src="{{ img_url }}" alt="{{ res.alt }}">
        {% endfor %}
    </div>
    {% endif %}

    {% if article.attachments %}
    <div class="attachments">
        <h3>附件</h3>
        <ul>
            {% for res in article.attachments %}
            <li>
                <a href="{% media_url res.resource.url %}" download>
                    {{ res.resource.title|default:res.alt }}
                </a>
                <span>{{ res.resource.size }} bytes</span>
            </li>
            {% endfor %}
        </ul>
    </div>
    {% endif %}

    {% if article.categories.exists %}
    <div class="categories">
        {% for cat in article.categories.all %}
        <a href="{% url 'list' cat.uuid %}">
            {{ cat.translation.name }}
        </a>
        {% endfor %}
    </div>
    {% endif %}

</article>
```

---

## 5. 单页详情页

单页详情页与文章详情页高度相似。因为单页在数据层面与文章共用同一模型，视图注入的 `page` 对象字段和 `article`
完全一致。模板写法上只需注意以下几点：

- 视图注入的变量名为 `page`，而非 `article`
- 单页通常没有分类归属（`page.categories` 为空）
- 单页没有置顶、推荐等属性

因此模板中只需将 `article` 替换为 `page` 即可。

```html title="page.html"
{% load content_tags pinmok_tags %}

<article class="page-detail">
    <h1>{{ page.translation.title }}</h1>

    {% if page.translation.content %}
    <div class="content">
        {{ page.translation.content|safe }}
    </div>
    {% endif %}
</article>
```

!!! tip "单页模板命名"

    单页模板默认文件名为 `page.html`，对应配置文件 `page.json`，action 为 `page`。如果项目中单页数量较多且样式差异大，
    可通过后台为不同单页指定不同的模板标识（需在模型中设置），主题中提供对应的模板文件即可。
