# Content App Theme Development

If you are already familiar with theme development and just need a quick reference, expand the **Quick Reference** section below.

??? abstract "Quick Reference"

    This section is for developers who already understand the Pinmok theme mechanism. It provides a quick reference for the Content app theme.

    **Minimum Directory Structure**
    ```text title="Directory Structure"
    templates/
    └── themes/
        └── mytheme/
            ├── theme.json       # Required, app_label must be "content"
            ├── index.html       # Homepage
            ├── index.json
            ├── list.html        # Article list
            ├── list.json
            ├── article.html     # Article detail
            ├── article.json
            └── page.html        # Single page detail (Optional)
    ```

    **Action and URL Route Mapping**

    | Page | Action | URL Path |
    |---|---|---|
    | Homepage | `index` | `{BASE_URL}/` |
    | Article Category List | `list` | `{BASE_URL}/list/<uuid>` |
    | Article Detail | `article` | `{BASE_URL}/article/<uuid>` |
    | Single Page Detail | `page` | `{BASE_URL}/page/<uuid>` |

    **Template Tags Quick Reference**

    | Tag | Purpose | Parameters (Required in **bold**) |
    |---|---|---|
    | `{% articles %}` | Fetch article list | **category** (UUID or list), **as** (variable name)<br>limit, page_num, page_size<br>order, top, recommended<br>*(Note: `limit` is mutually exclusive with `page_num/page_size`)* |
    | `{% page %}` | Fetch single page details | **uuid** (Page UUID), **as** (variable name) |
    | `{% category %}` | Fetch single category | **uuid** (Category UUID), **as** (variable name) |
    | `{% pagination %}` | Render pagination component | **page_obj** (Page object)<br>wing, ul_class, item_class, link_class, active_class, disabled_class,<br>prev_label, next_label, ellipsis_text |

    **Built-in Data Sources Quick Reference**

    Used when declaring `"type": "datasource"` in JSON configurations.

    | Source Value | Description | Corresponding Template Tag |
    |---|---|---|
    | `category` | Tree data of all active categories | `{% articles category=var ... %}` |
    | `page` | Data of all published single pages | `{% page uuid=var ... %}` |

---

## Overview

Although front-end and back-end separation has become the mainstream, template development based on server-side rendering still offers
significant efficiency advantages for small websites, internal tools, or rapid prototyping. It eliminates the need for complex API
integration, allowing a single template to quickly deliver a complete business presentation.

This chapter is aimed at frontend developers proficient in HTML/CSS and Django template syntax. The Pinmok framework does not alter Django's
core template syntax (like `{% %}` and `{{ }}`). Instead, it extends it with **Template Tags** and a **Data Source** mechanism, providing
out-of-the-box business components.

The Content app provides the following core support for theme development:

- **Four Standard Pages**: Homepage, Article Category List, Article Detail, and Single Page Detail.
- **Dedicated Template Tags (`content_tags`)**: Provides specialized tags for article queries, category fetching, and pagination rendering.
- **Data Source Mechanism**: Solves the pain point of "unpredictable real data IDs" during template development, decoupling backend
  configuration from frontend code.
- **Automatic Context Injection**: Views automatically inject necessary current business objects (like `article` or `category`) into the
  template context, eliminating the need for extra queries.

!!! note "Division of Labor for Template Tags"

    Content themes typically need to load two tag libraries simultaneously: `{% load content_tags pinmok_tags %}`.

    - `content_tags`: Provides Content app-specific business features (articles, categories, pagination, etc.).
    - `pinmok_tags`: Provides framework-level general features (site info, navigation, media parsing, carousels, etc.). 
      This chapter focuses on `content_tags`; for `pinmok_tags`, please refer to the core Pinmok theme documentation.

---

## Core Concepts: Template Tags and Data Sources

Before diving into specific pages, it is essential to understand the two core design philosophies behind Pinmok theme development.

### Template Tags

In pure Django development, fetching related data usually requires writing complex ORM queries or custom template tags. Pinmok encapsulates
common business queries into standard tags. You don't need to write any Python logic. Simply use declarative syntax in your HTML, like
`{% articles category=xxx limit=5 as list %}`, to extract data into the `list` variable for looping. This significantly lowers the barrier
to entry for frontend developers working on templates.

### Data Sources

**Design Rationale**:
When developing a homepage or an aggregation page, we often need to display "articles under a specific category." However, when writing the
template, **the template developer can never know the real ID of that category in advance** (because the data is entered at runtime in the
backend).

**The Solution**:
Pinmok introduces the **Data Source** mechanism, defining two data sources: `category` and `page`.

1. **Declare in JSON**: You define a variable (e.g., `news_category`), set its type to `datasource`, and specify the source as `category`.
2. **Backend Binding**: When the site admin configures the theme in the backend, they see a dropdown to select the real category. The actual
   UUID is then bound to the `news_category` variable.
3. **Use in Template**: In the template, you simply pass the variable name as a parameter: `{% articles category=news_category %}`.

**Summary**: Data sources allow template developers to focus purely on the "logical structure" (I want to display articles from a category),
while delegating the "specific data" (which exact category) to the backend configuration. This achieves true decoupling of code and data.

---

## Template Tags Reference

### `{% articles %}`

Used to query articles under specified categories. It supports pagination, sorting, and filtering for pinned/recommended articles.

**Parameters**:

| Parameter     | Type        | Default         | Description                                                                         |
|---------------|-------------|-----------------|-------------------------------------------------------------------------------------|
| `category`    | UUID / list | **Required**    | Filter by category UUID. Supports single values or lists (used with data sources).  |
| `limit`       | int         | None            | Limits the number of returned items. Disables pagination, returns a plain QuerySet. |
| `page_num`    | int         | 1               | Page number (1-based). **Mutually exclusive with `limit`**.                         |
| `page_size`   | int         | 10              | Items per page. **Mutually exclusive with `limit`**.                                |
| `order`       | str         | `-published_at` | Sort field. Options: `published_at`, `created_at`, `sort_order`.                    |
| `top`         | bool        | False           | If True, returns only pinned articles.                                              |
| `recommended` | bool        | False           | If True, returns only recommended articles.                                         |

**Usage Examples**:

```django
<!-- Fetch the 5 latest articles in a category -->
{% articles category=featured.news limit=5 order="-published_at" as latest_list %}

<!-- Fetch paginated articles -->
{% articles category=category.uuid page_num=page page_size=10 as paged_articles %}
```

!!! note "A Note on the `page_num` Parameter"

    `page_num` specifies the current page to render. Here is how to handle it in different scenarios:

    1. **In the Article List page (`list`)**:
       The backend already saves the page number in a variable. You can use `page` directly to get the URL parameter (e.g., `?page=2`).
       **Example**: `page_num=page`.
    2. **In other pages (e.g., Homepage `index`)**:
       The view does **not** inject a `page` variable by default. However, **you do not need to write a custom View**. Simply use
       `request.GET.page|default:1` in the template to fetch the URL parameter and handle pagination. **Example**:
       `page_num=request.GET.page|default:1`.
    3. **When to write a custom View**:
       Only when your pagination logic is highly complex (e.g., calculating the page number based on specific business conditions in Python
       rather than just relying on URL parameters) should you write a custom View, process the paginator, and modify the URL routes.
       For 99% of standard pagination needs, using `request.GET.page` at the template level is sufficient.

### `{% page %}`

Used to fetch the full details of a specified single page by its UUID. Typically used to display a specific page (like "About Us") on the
homepage.

**Usage Example**:

```django
<!-- Define the 'page' datasource variable 'about_us' in the config file -->
{% page uuid=about_us as about_page %}
{% if about_page %}
    <h2>{{ about_page.translation.title }}</h2>
{% endif %}
```

### `{% category %}`

Used to fetch a single category object by its UUID, returning category information.

**Usage Example**:

```django
{% category uuid=featured.category as feat_cat %}
{% if feat_cat %}
    <h3>{{ feat_cat.translation.name }}</h3>
{% endif %}
```

### `{% pagination %}`

Renders a Django `Page` object into an HTML pagination navigation component.

**Parameters**:

| Parameter        | Type | Default      | Description                                                                               |
|------------------|------|--------------|-------------------------------------------------------------------------------------------|
| `page_obj`       | Page | **Required** | Django Page object (usually returned by `{% articles %}` in pagination mode).             |
| `wing`           | int  | `4`          | Number of page links to show on each side of the current page.                            |
| `ul_class`       | str  | `pagination` | CSS class for the `<ul>` element.                                                         |
| `item_class`     | str  | `page-item`  | CSS class for each `<li>` element.                                                        |
| `link_class`     | str  | `page-link`  | CSS class for each `<a>` element.                                                         |
| `active_class`   | str  | `active`     | Extra CSS class applied to the current page's `<li>`.                                     |
| `disabled_class` | str  | `disabled`   | Extra CSS class applied to disabled `<li>` elements (e.g., prev/next when at boundaries). |
| `prev_label`     | str  | `«`          | Text or icon for the "Previous" button.                                                   |
| `next_label`     | str  | `»`          | Text or icon for the "Next" button.                                                       |
| `ellipsis_text`  | str  | `...`        | Text displayed for page gaps/ellipsis.                                                    |

**Usage Example**:

```django
{% pagination paged_articles wing=2 ul_class="pagination justify-content-center" %}
```

---

## Practical Theme Development

### Homepage (index)

The homepage view **injects no context variables**. All content must be actively fetched using template tags. The focus here is on
leveraging data sources to configure dynamic modules.

**`index.json` Configuration Example**:

```json
{
  "name": "Homepage",
  "action": "index",
  "fieldsets": {
    "featured": {
      "title": "Featured Section",
      "vars": {
        "news_category": {
          "title": "News Category",
          "type": "datasource",
          "source": "category"
        }
      }
    }
  }
}
```

**`index.html` Template Example**:

```django
{% load content_tags pinmok_tags %}
 <!DOCTYPE html>
 <html>
 <head><title>Homepage</title></head>
 <body>
   <h1>Latest Articles</h1>
   <!-- Use the datasource variable as a parameter -->
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

### Article List Page (list)

The list view automatically injects the current `category` object into the context. The focus here is on pagination handling.

**`list.html` Template Example**:

```django
{% load content_tags pinmok_tags %}
 <!-- Directly use the injected category object -->
 <h1>{{ category.translation.name }}</h1>
 <p>{{ category.translation.description }}</p>
 
 <!-- Fetch paginated data -->
 {% articles category=category.uuid page_num=request.GET.page|default:1 page_size=10 as paged %}
 
 {% if paged %}
   <div class="article-list">
     {% for art in paged %}
       <article>
         <h2><a href="{% url 'article' art.uuid %}">{{ art.translation.title }}</a></h2>
       </article>
     {% endfor %}
   </div>
   <!-- Render pagination -->
   {% pagination paged %}
 {% else %}
   <p>No articles yet.</p>
 {% endif %}
```

### Article Detail Page (article)

The detail view automatically injects the `article` object. The focus here is on safely outputting rich text and handling media resources.

**`article.html` Template Example**:

```django
{% load content_tags pinmok_tags %}
 <article>
   <h1>{{ article.translation.title }}</h1>
   <time>{{ article.published_at|date:"Y-m-d" }}</time>
   
   <!-- Note: Rich text content MUST use the |safe filter -->
   <div class="content">
     {{ article.translation.content|safe }}
   </div>

   <!-- Handle gallery resources -->
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

### Single Page Detail (page)

Single pages share the exact same model and fields as articles. The only difference is that the view injects the object as `page` instead of
`article`.

**`page.html` Template Example**:

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

## Summary: Standard Theme Development Workflow

To maximize efficiency and minimize errors, it is highly recommended to follow this standard workflow when developing themes:

1. **Build Static Pages**: First, complete the static design for all pages using pure HTML/CSS/JS. Ensure styles and interactions are
   perfect.
2. **Split and Plan**: Analyze the static pages. Determine which data is static (hardcoded in HTML) and which is dynamic (needs to be
   fetched from the database).
3. **Configure JSON and Data Sources**: Define dynamic variables in the corresponding `.json` files. For categories or single pages that
   need to be selected in the backend, **always** use the `datasource` type.
4. **Replace with Template Tags**:
    - Replace static dummy data with `{{ variable_name }}`.
    - Replace lists that need looping with data fetched via tags like `{% articles %}`.
    - Replace hardcoded links with `{% url %}` tags.
5. **Defensive Checks**: Wrap all dynamically generated links (especially those using datasource variables) in `{% if %}` checks to prevent
   500 errors caused by empty parameters during initial setup.

!!! warning "Pitfall Guide"

    1. **Empty URL Dynamic Parameters**: When a theme is freshly installed and the backend has no data, datasource variables will be empty.
       `{% url 'list' news.category %}` will throw a 500 error. It **must** be wrapped in `{% if news.category %}`.
    2. **Rich Text Escaping**: `article.translation.content` contains HTML tags. You **must** append the `|safe` filter when outputting it;
       otherwise, the tags will be escaped and displayed as plain text.