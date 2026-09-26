# Content 应用主题开发

如果你已经熟知模板制作，只想速查用法，可以点开速查资料。

??? abstract "点击展开：速查资料"

      本章节面向已了解 Pinmok 主题机制的开发者，提供 Content 应用主题的速查信息。

       **最小目录结构**
       ```text title="目录结构"
       templates/
       └── themes/
           └── mytheme/
               ├── theme.json       # 必须，app_label 必须为 "content"
               ├── index.html       # 首页
               ├── index.json
               ├── list.html        # 文章列表
               ├── list.json
               ├── article.html     # 文章详情
               ├── article.json
               └── page.html        # 单页详情 (可选)
       ```
   
       **Action 与 URL 路由映射**

       | 页面 | Action | URL 路径 |
       |---|---|---|
       | 首页 | `index` | `{BASE_URL}/` |
       | 文章分类列表 | `list` | `{BASE_URL}/list/<uuid>` |
       | 文章详情 | `article` | `{BASE_URL}/article/<uuid>` |
       | 单页详情 | `page` | `{BASE_URL}/page/<uuid>` |
   
       **模板标签速查**

       | 标签 | 作用 | 参数说明 (必填项加粗) |
       |---|---|---|
       | `{% articles %}` | 获取文章列表 | **category**(UUID或列表), **as**(变量名)<br>limit(数量), page_num(页码), page_size(每页)<br>order(排序), top(置顶), recommended(推荐)<br>*(注: `limit` 与 `page_num/page_size` 互斥)* |
       | `{% page %}` | 获取单页详情 | **uuid**(单页UUID), **as**(变量名) |
       | `{% category %}` | 获取单个分类 | **uuid**(分类UUID), **as**(变量名) |
       | `{% pagination %}` | 渲染分页组件 | **page_obj**(Page对象) <br>wing(侧边页码数), ul_class, item_class, link_class, active_class, disabled_class, <br>prev_label, next_label, ellipsis_text |
       
       **内置数据源速查**

       在 JSON 配置中声明 `"type": "datasource"` 时使用。

       | source 值 | 说明 | 模板中配合使用的标签 |
       |---|---|---|
       | `category` | 所有激活分类的树形数据 | `{% articles category=var ... %}` |
       | `page` | 所有已发布单页的数据 | `{% page uuid=var ... %}` |

## 概述

虽然前后端分离已成为主流，但在面对小型网站、内部工具或快速验证型需求时，基于服务端渲染的模板开发依然具有极高的效率优势。
无需复杂的前后端联调，一套模板即可快速实现完整的业务展示。

本章面向 **熟悉 HTML/CSS 及 Django 模板语法** 的前端开发人员。Pinmok 框架并未改变 Django 模板的核心语法（如 `{% %}` 和
`{{ }}`），而是通过扩展 **标签库**和 **数据源机制**，为您提供开箱即用的业务组件。

Content 应用为主题开发提供了以下核心支持：

1. **四大标准页面**：首页、文章分类列表、文章详情、单页详情。
2. **专属标签库 (`content_tags`)**：提供文章查询、分类获取、分页渲染等专用标签。
3. **数据源机制 (Datasource)**：解决模板开发时“无法预知真实数据 ID”的痛点，实现后台配置与前端代码的解耦。
4. **上下文自动注入**：视图会自动将必要的当前业务对象（如 `article`、`category`）注入模板，无需额外查询。

!!! note "关于标签库的分工"

    Content 主题通常需要同时加载两个标签库：`{% load content_tags pinmok_tags %}`。

    - `content_tags`：提供 Content 应用专属的业务功能（文章、分类、分页等）。
    - `pinmok_tags`：提供框架级通用功能（站点信息、导航、媒体文件解析、轮播图等）。本章重点讲解 `content_tags`，`pinmok_tags` 请参考 Pinmok 基础主题文档。

## 核心概念：标签库与数据源

在深入具体页面前，必须理解 Pinmok 主题开发的两个核心设计理念。

### 标签库

在纯 Django 开发中，获取关联数据通常需要编写复杂的 ORM 查询或自定义 template tags。Pinmok 将常用的业务查询封装成了标准标签。
你不需要在 Python 代码中写任何逻辑，只需在 HTML 中通过 `{% articles category=xxx limit=5 as list %}` 这样的声明式语法，即可将数据提取到 `list`
变量中进行循环渲染。这极大降低了前端人员参与模板开发的门槛。

### 数据源

**设计初衷**：
在开发首页或聚合页时，我们经常需要展示“某个特定分类下的文章”。但在编写模板时， **模板开发者永远无法预知这个分类的真实 ID 是什么**
（因为数据是后台运行时才录入的）。

**解决方案**：
Pinmok 引入了 **数据源 (Datasource)** 机制，定义了两个数据源：`category` 和 `page`。

1. **在 JSON 配置中声明**：你只需定义一个变量（如 `news_category`），并将其类型设为 `datasource`，数据源指定为 `category`。
2. **后台配置绑定**：网站管理员在后台配置主题时，会看到一个下拉框，从中选择真实的分类。此时，真实的 UUID 被绑定到了 `news_category` 变量上。
3. **模板中使用变量**：在模板中，你只需要把变量名当作参数传入标签：`{% articles category=news_category %}`。

**总结**：数据源让模板开发时只需关注“逻辑结构”（我要展示一个分类的文章），而将“具体数据”（展示哪个分类）交由后台配置完成，实现了真正的代码与数据解耦。

---

## 标签详解

### `{% articles %}`

用于查询指定分类下的文章，支持分页、排序、置顶/推荐过滤。

**参数说明**：

| 参数          | 类型        | 默认值          | 说明                                                       |
|---------------|-------------|-----------------|------------------------------------------------------------|
| `category`    | UUID / list | 必填            | 按分类 UUID 过滤，支持单值或列表（配合数据源使用）         |
| `limit`       | int         | None            | 限制返回数量；设置后禁用分页，返回普通 QuerySet            |
| `page_num`    | int         | 1               | 页码（从 1 开始）；与 `limit` 互斥                         |
| `page_size`   | int         | 10              | 每页数量；与 `limit` 互斥                                  |
| `order`       | str         | `-published_at` | 排序字段，可选：`published_at`, `created_at`, `sort_order` |
| `top`         | bool        | False           | 仅返回置顶文章                                             |
| `recommended` | bool        | False           | 仅返回推荐文章                                             |

**使用示例**：

```django
<!-- 获取某分类下最新的 5 篇文章 -->
{% articles category=featured.news limit=5 order="-published_at" as latest_list %}

<!-- 获取分页文章列表 -->
{% articles category=category.uuid page_num=page page_size=10 as paged_articles %}
```

!!! note "关于分页参数 `page_num` 的说明"

    `page_num` 用于指定当前渲染的页码。关于该参数的获取方式，请注意以下场景：

    1. **在文章列表页 (`list`)**：
       后端已经将页面保存在变量中，您可以直接使用 `page` 获取 URL 上的页码参数（例如 `?page=2`）。
       **示例**：`page_num=page`。

    2. **在其他页面（如首页 `index`）**：
       视图默认 **不会**注入名为 `page` 的分页变量。但您 **无需为此自定义 View**。直接在模板中同样使用
       `request.GET.page|default:1` 即可获取 URL 参数并实现分页。
       **示例**：`page_num=request.GET.page|default:1`

    3. **何时需要自定义 View**
      只有当您的分页逻辑非常复杂（例如需要根据特定的业务条件在 Python 代码中计算页码，而不是单纯依赖 URL 参数），
      才需要自己编写 View 方法、处理分页对象，并修改 URL 路由指向您的自定义 View。对于 99% 的常规分页需求，
      直接在模板层使用 `request.GET.page` 即可。

### `{% page %}`

用于获取指定 UUID 的文章或单页的完整详情。通常用于首页调用特定单页（如“关于我们”）。

**使用示例**：

配置文件中定义 `page` 数据源变量 `about_us`

```django
{% page uuid=about_us as about_page %}
{% if about_page %}
    <h2>{{ about_page.translation.title }}</h2>
{% endif %}
```

### `{% category %}`

用于获取指定 UUID 的分类对象，返回类别信息。

**使用示例**：

```django
{% category uuid=featured.category as feat_cat %}
{% if feat_cat %}
    <h3>{{ feat_cat.translation.name }}</h3>
{% endif %}
```

### `{% pagination %}`

将 Django 的 `Page` 对象渲染为 HTML 分页导航。

**参数说明**：

| 参数             | 类型 | 默认值       | 说明                                                    |
|------------------|------|--------------|---------------------------------------------------------|
| `page_obj`       | Page | **必填**     | Django 分页对象（通常由 `{% articles %}` 分页模式返回） |
| `wing`           | int  | `4`          | 当前页码两侧各显示的页码数量                            |
| `ul_class`       | str  | `pagination` | `<ul>` 元素的 CSS 类                                    |
| `item_class`     | str  | `page-item`  | `<li>` 元素的 CSS 类                                    |
| `link_class`     | str  | `page-link`  | `<a>` 元素的 CSS 类                                     |
| `active_class`   | str  | `active`     | 当前激活页 `<li>` 附加的 CSS 类                         |
| `disabled_class` | str  | `disabled`   | 禁用状态（如首页/末页不可点时）`<li>` 附加的 CSS 类     |
| `prev_label`     | str  | `«`          | “上一页”按钮显示的文字或图标                            |
| `next_label`     | str  | `»`          | “下一页”按钮显示的文字或图标                            |
| `ellipsis_text`  | str  | `...`        | 页码省略号显示的文字                                    |

**使用示例**：

```django
{% pagination paged_articles wing=2 ul_class="pagination justify-content-center" %}
```

---

## 模板开发实战

### 首页 (index)

首页视图 **不注入任何上下文**，所有内容均需通过标签主动获取。重点在于利用数据源配置动态模块。

**`index.json` 配置示例**：

```json
{
  "name": "首页",
  "action": "index",
  "fieldsets": {
    "featured": {
      "title": "精选栏目",
      "vars": {
        "news_category": {
          "title": "新闻分类",
          "type": "datasource",
          "source": "category"
        }
      }
    }
  }
}
```

**`index.html` 模板示例**：

```django
{% load content_tags pinmok_tags %}
<!DOCTYPE html>
<html>
<head><title>首页</title></head>
<body>
  <h1>最新文章</h1>
  
  <!-- 使用数据源变量作为参数 -->
  {% if featured.news_category %}
    {% articles category=featured.news_category limit=5 as latest %}
    <ul>
      {% for art in latest %}
        <li>
          <a href="{% url 'article' art.uuid %}">{{ art.translation.title }}</a>
        </li>
      {% endfor %}
    </ul>
  {% endif %}
</body>
</html>
```

### 文章列表页 (list)

列表页视图会自动注入当前分类的 `category` 对象。重点在于分页处理。

**`list.html` 模板示例**：

```django
{% load content_tags pinmok_tags %}

<!-- 直接使用注入的 category 对象 -->
<h1>{{ category.translation.name }}</h1>
<p>{{ category.translation.description }}</p>

<!-- 获取分页数据 -->
{% articles category=category.uuid page_num=request.GET.page|default:1 page_size=10 as paged %}

{% if paged %}
  <div class="article-list">
    {% for art in paged %}
      <article>
        <h2><a href="{% url 'article' art.uuid %}">{{ art.translation.title }}</a></h2>
      </article>
    {% endfor %}
  </div>
  
  <!-- 渲染分页 -->
  {% pagination paged %}
{% else %}
  <p>暂无文章。</p>
{% endif %}
```

### 文章详情页 (article)

详情页视图会自动注入 `article` 对象。重点在于富文本的安全输出和资源处理。

**`article.html` 模板示例**：

```django
{% load content_tags pinmok_tags %}

<article>
  <h1>{{ article.translation.title }}</h1>
  <time>{{ article.published_at|date:"Y-m-d" }}</time>
  
  <!-- 注意：正文必须使用 |safe 过滤器 -->
  <div class="content">
    {{ article.translation.content|safe }}
  </div>

  <!-- 处理图集资源 -->
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

### 单页详情页 (page)

单页与文章共用模型，字段完全一致，只是注入的变量名为 `page`。

**`page.html` 模板示例**：

```django
{% load content_tags pinmok_tags %}

<article>
  <h1>{{ page.translation.title }}</h1>
  <div class="content">
    {{ page.translation.content|safe }}
  </div>
</article>
```

---

## 总结：模板制作标准流程

为了提高效率并减少错误，建议遵循以下标准流程进行主题开发：

1. **编写静态页面**：首先使用纯 HTML/CSS/JS 完成所有页面的静态设计，确保样式和交互完美。
2. **拆分与规划**：分析静态页面，确定哪些数据是固定的（写死在 HTML 中），哪些是动态的（需要从数据库获取）。
3. **配置 JSON 与数据源**：在对应的 `.json` 文件中定义动态变量。对于需要后台选择的分类或单页，务必使用 `datasource` 类型。
4. **替换为模板标签**：

    - 将静态的假数据替换为 `{{ 变量名 }}`。
    - 将需要循环的列表替换为 `{% articles %}` 等标签获取的数据。
    - 使用 `{% url %}` 替换硬编码的链接。

5. **防御性检查**：对所有动态生成的链接（特别是使用数据源变量的链接）使用 `{% if %}` 进行判空保护，防止初始化时因参数为空导致 500 错误。

!!! warning "避坑指南"

    1. **URL 动态参数为空**：主题刚安装且后台无数据时，数据源变量为空。`{% url 'list' news.category %}` 会引发 500 错误。必须包裹在
       `{% if news.category %}` 中。
    2. **富文本转义**：`article.translation.content` 包含 HTML 标签，输出时 **必须**添加 `|safe` 过滤器，否则标签会被转义为纯文本显示。