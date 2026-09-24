# Theme Development

If you're already familiar with the Pinmok theme system, expand **Quick Start** for a cheat sheet on Content app themes.

??? abstract "Quick Start"

    This section is for developers who already understand the Pinmok theme mechanism (directory structure, `theme.json`,
    installation and activation) and need a quick reference for Content app themes.

    **Minimum Directory Structure**

    A Content theme must include at least the following files. The page template `page.html` is optional and can be omitted for a minimal theme.

    ```text title="Directory Structure"
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
            └── page.html          # Optional
    ```

    !!! warning "Note"
        The `app_label` property in `theme.json` must be set to the string `content` to match the app name,
        so Pinmok can correctly identify it as a Content template.

    **Action Name Mapping**

    The `action` in template configuration files must match the URL name of the corresponding view.

    | Page | Action | Full URL |
    |---|---|---|
    | Homepage | `index` | {BASE_URL}/ |
    | Category Article List | `list` | {BASE_URL}/list/<uuid> |
    | Article Detail | `article` | {BASE_URL}/article/<uuid> |
    | Page Detail | `page` | {BASE_URL}/page/<uuid> |

    **Loading Tag Libraries**

    Content themes typically need to load two tag libraries:

    ```django
    {% load content_tags pinmok_tags %}
    ```

    `content_tags` provides Content app-specific features such as articles, categories, pagination, and status badges. 
    `pinmok_tags` provides general features like site information, navigation, media file resolution, carousels, and
    friend links. The latter is detailed in the Pinmok theme documentation and will be used directly in this chapter.

    **Configuration File Format Examples**

    ```json title="theme.json"
    {
      "name": "My Content Theme",
      "app_label": "content",
      "version": "1.0.0",
      "vars": {
        "site_name": {
          "title": "Site Name",
          "type": "text",
          "default": "My Website"
        }
      }
    }
    ```

    !!! tip "Tip"

        Variables defined in `theme.json` are global and available to all templates. Variables defined in other template configuration files are only available to their corresponding templates.

    ```json title="index.json"
    {
      "name": "Homepage",
      "action": "index",
      "vars": {
        "hero_title": {
          "title": "Hero Title",
          "type": "text",
          "default": "Welcome to the Homepage"
        }
      },
      "fieldsets": {
        "featured": {
          "title": "Featured Section",
          "vars": {
            "category": {
              "title": "Category",
              "type": "datasource",
              "source": "category"
            },
            "count": {
              "title": "Display Count",
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
      "name": "Article List",
      "action": "list",
      "vars": {
        "page_size": {
          "title": "Items Per Page",
          "type": "number",
          "default": 10
        }
      }
    }
    ```

    ```json title="article.json"
    {
      "name": "Article Detail",
      "action": "article"
    }
    ```

    ```json title="page.json"
    {
      "name": "Page Detail",
      "action": "page"
    }
    ```

    **Content Template Tags Cheat Sheet**

    - Get multiple articles from a category
        `{% articles category=uuid|list[uuid] limit=N page_num=N page_size=N order='-published_at' top=True recommended=True as var %}`
    - Get a specific article's full content
        `{% article uuid=xxx as var %}`
    - Get a page's full content
        `{% page uuid=xxx as var %}`
    - Get a single category
        `{% category uuid=xxx as var %}`
    - Pagination display
        `{% pagination page_obj wing=4 ul_class='pagination' item_class='page-item' link_class='page-link' active_class='active' disabled_class='disabled' prev_label='«' next_label='»' ellipsis_text='...' %}`

    **Content Built-in Data Sources Cheat Sheet**

    Used when declaring `type: "datasource"` in configuration files.

    | source | Description | Corresponding Template Tag |
    |---|---|---|
    | `category` | Tree data of all active categories | `{% articles category=var ... %}` |
    | `page` | Data of all published pages | `{% page uuid=var ... %}` |

    **Context Variables Cheat Sheet**

    The following views automatically inject business objects, which can be accessed directly in templates using `{{ variable.field }}` without needing to fetch them via tags.

    - **category object** (Article category list page) Example: `{{ category.translation.name }}`

        | Field | Description |
        |---|---|
        | `uuid` | Category unique identifier |
        | `cover` | Cover image path, used with `{% media_url %}` |
        | `template` | Template identifier, defaults to `list` |
        | `is_active` | Whether active |
        | `sort_order` | Sort weight |
        | `parent` | Parent category object or `None` |
        | `children` | Child category relation manager |
        | `translation.name` | Category name (current language) |
        | `translation.description` | Category description (current language) |

    - **article object** (Article detail page) Example: `{{ article.translation.title }}`

        | Field | Description |
        |---|---|
        | `uuid` | Unique identifier |
        | `type` | Type: `article` or `page` |
        | `template` | Template identifier, defaults to `article` |
        | `cover` | Cover image path |
        | `status` | Status string |
        | `sort_order` | Sort weight |
        | `extra` | Extended JSON data |
        | `is_top` | Whether pinned to top |
        | `is_recommended` | Whether recommended |
        | `published_at` | Publication time |
        | `created_at` | Creation time |
        | `updated_at` | Update time |
        | `categories` | Associated categories (ManyToMany) |
        | `translation.title` | Title |
        | `translation.subtitle` | Subtitle |
        | `translation.summary` | Summary |
        | `translation.content` | Body content |
        | `gallery` | Gallery resource list |
        | `attachments` | Attachment resource list |
        | `videos` | Video resource list |
        | `audios` | Audio resource list |

    - **page object** (Page detail page) Example: `{{ page.translation.title }}`

        Fields are identical to `article`. Simply replace `article` with `page`. Pages typically don't use business
        attributes like pinning or recommendations, but the field structure is identical to articles.

    **Complete Minimal Theme Example**

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

## 1. Overview

This chapter is aimed at frontend developers — you need to be familiar with HTML/CSS and Django template syntax (`{% %}`
and `{{ }}`), but no Python coding is required.

Content app theme development follows the Pinmok universal theme mechanism: a theme is a directory containing
`theme.json`, HTML templates, and JSON configuration files, placed in the `themes/` folder under Django's template
search path to be recognized. For details on theme directory structure, `theme.json` specifications, installation and
activation procedures, variable injection principles, and multilingual configuration rules, refer to the Pinmok Theme
Documentation. This chapter only covers Content app-specific conventions, including template tags, view-injected context
variables, and built-in data sources.

The Content app provides four types of frontend pages:

| Page                  | Description                                                      |
|-----------------------|------------------------------------------------------------------|
| Homepage              | Site entry point, typically aggregating multiple content modules |
| Category Article List | Displays articles under a specific category with pagination      |
| Article Detail        | Shows a complete article                                         |
| Page Detail           | Displays standalone pages like "About Us"                        |

Template developers can start by writing static HTML, then transform it into dynamic templates.

In templates, you typically need to load two tag libraries simultaneously:

```django
{% load content_tags pinmok_tags %}
```

`content_tags` is the core of this chapter, providing Content-specific features like article queries, category queries,
pagination, and status badges. `pinmok_tags` provides framework-level general features like site information,
navigation, media file resolution, carousels, and friend links. It will be used directly in examples without further
explanation.

!!! note "Standard Django Template Syntax Fully Applies"

    Template inheritance (`{% extends %}`), inclusion (`{% include %}`), conditional statements, loops, etc., are all
    standard Django template syntax. Pinmok does not impose any restrictions or modifications — anything Django supports is
    supported here.

### 1.1 Template Configuration Files

Every theme must contain a core descriptor file, `theme.json`. Additional configuration files are optional and can be
configured as needed. The specific rules are as follows:

- **Basic Rule**: If a template does not require custom variables, its corresponding configuration file can be omitted.
- **Multiple Templates Rule**: If a single Action is associated with multiple templates, all extended templates
  (excluding the default one) must have their own independent configuration files.
- **Configuration Example**: Suppose the default template for the "Article Detail Page" is `article.html`. If you need
  to add a custom template named `article_special.html`, you must create an `article_special.json` file and explicitly
  declare `"action": "article"` inside it to establish the route mapping.

### 1.2 Template Tags

The Content module provides the following built-in core template tags used to fetch and render data in views:

- **`{% articles %}`**: Fetches a list of articles under a specified category. It supports conditional filtering and
  configuration via parameters.
- **`{% pagination %}`**: A generic pagination navigation rendering tag used to render the pagination object
  (`page_obj`) from the context into an HTML pagination control.
- **`{% article %}`**: Fetches and renders the complete details of a specified article.
- **`{% page %}`**: Fetches and renders the complete details of a specified standalone page.
- **`{% category %}`**: Fetches and renders the details of a specified category.

### 1.3 URL Definitions

This section defines the URL routing for the application. Understanding these routes is essential for generating correct
hyperlinks (e.g., `<a href="...">`) in your templates.

| Page                   | Action    | URL Path                    |
|------------------------|-----------|-----------------------------|
| Home                   | `index`   | `{BASE_URL}/`               |
| Article Category List  | `list`    | `{BASE_URL}/list/<uuid>`    |
| Article Detail         | `article` | `{BASE_URL}/article/<uuid>` |
| Standalone Page Detail | `page`    | `{BASE_URL}/page/<uuid>`    |

- **`{BASE_URL}`**: Represents the root domain of your website (e.g., `https://www.pinmok.com`).
- **Dynamic Parameters (`<uuid>`)**: In actual templates, `<uuid>` is a placeholder and must be replaced with the real
  UUID or ID of the specific object.

!!! warning "Crucial Note for Theme Developers (Handling Empty Data)"

    Dynamic parameters in URL paths (e.g., `<uuid>`) **must not be empty**.
    
    When a theme is freshly installed and the backend database contains no data, the variables fetched from the data source
    will be empty or `None`. Attempting to generate URLs with empty parameters will cause routing failures and result in
    **500 Internal Server Errors**.
    
    **Solution**: Always use defensive programming in your templates. Wrap your link generation logic in `{% if %}` blocks
    to ensure the data and its parameters exist before rendering the URL.
    
    **Example:**
    
    ```html
    <!-- ❌ Bad Practice: 'news.category' is a data source variable defined in the configuration file with a default value of None, which may cause a 500 error. -->
    <a href="{% url 'list' news.category %}">Read More</a>
    
    <!-- ✅ Best Practice: Check for data existence first -->
    {% if news.category %}
      <a href="{% url 'list' news.category %}">Read More</a>
    {% endif %}
    ```

## 2. Homepage Template Development

The homepage is the most labor-intensive page in a Content theme. Unlike other pages, the homepage view injects no
context — all content on the page must be actively retrieved via template tags.

### 2.1 Homepage Specifics

General modules like carousels, navigation, site information, and friend links are provided by `pinmok_tags` (see Pinmok
documentation; used directly in this chapter's examples). Article lists, pinned content, recommended content, and
category-specific content are retrieved via the `{% articles %}` tag from `content_tags`. Besides defining regular
variables, homepage configuration files typically use data sources to allow backend administrators to select specific
business data sources.

### 2.2 Writing Configuration: index.json

**Regular Variables**

```json
{
  "name": "Homepage",
  "action": "index",
  "vars": {
    "hero_title": {
      "title": "Hero Title",
      "type": "text",
      "default": "Welcome to the Homepage"
    }
  }
}
```

The example defines a variable `hero_title` of text type with a default value of `Welcome to the Homepage`. Users can
input other content in the backend to override the default. This variable can be called in templates via
`{{ hero_title }}`.

**Data Source Variables**

Data source type variables provide dropdown selections in the backend configuration interface, allowing administrators
to specify a particular category or page instead of hardcoding UUIDs in the frontend.

```json
{
  "name": "Homepage",
  "action": "index",
  "vars": {
    "hero_title": {
      "title": "Hero Title",
      "type": "text",
      "default": "Welcome to the Homepage"
    }
  },
  "fieldsets": {
    "featured": {
      "title": "Featured Section",
      "vars": {
        "news": {
          "title": "News",
          "type": "datasource",
          "source": "category",
          "multiple": true
        },
        "count": {
          "title": "Display Count",
          "type": "number",
          "default": 4
        }
      }
    },
    "about": {
      "title": "About Us",
      "vars": {
        "about_us": {
          "title": "Select Page",
          "type": "datasource",
          "source": "page"
        }
      }
    }
  }
}
```

This example defines two data source type variables:

`news`: Data source is `category`, with `multiple: true` set to allow multiple selections. When configuring the template
in the backend, this variable displays a dropdown of all categories, allowing users to select multiple categories. It's
used via tags, e.g., `{% articles category=featured.news ... %}`. During template execution, it retrieves the list of
category UUIDs configured by the user from the `news` variable and fetches articles from those categories.

`about_us`: Data source is `page`. When configuring the template in the backend, the dropdown displays the titles of all
page articles for selection. It is used with template tags, for example,
`{% page uuid=about.about_us ... %}`. During template execution, it retrieves the page article UUID from the `about_us`
variable and fetches the corresponding page content.

### 2.3 Writing Template: index.html

The homepage is usually the most complex, so the design is split into several dynamic blocks, each matching a
corresponding template tag. The examples assume an article category data source variable has been configured.

**Latest Articles List**

Use the `{% articles %}` tag to fetch published articles and assign them to the variable `latest`. When the `limit`
parameter is set, it returns a plain list without pagination.

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

Complete parameters for `{% articles %}`:

| Parameter   | Type        | Default       | Description                                                                |
|-------------|-------------|---------------|----------------------------------------------------------------------------|
| category    | UUID / list | Required      | Filter by category UUID, supports single value or list                     |
| limit       | int         | None          | Limit return count; when set, disables pagination and returns a plain list |
| page_num    | int         | 1             | Page number (starting from 1); mutually exclusive with `limit`             |
| page_size   | int         | 10            | Items per page; mutually exclusive with `limit`                            |
| order       | str         | -published_at | Sort field, options: `published_at`, `created_at`, `sort_order`            |
| top         | bool        | False         | Return only pinned articles                                                |
| recommended | bool        | False         | Return only recommended articles                                           |

**Pinned and Recommended Articles**

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

**Working with Data Sources: Linking to a Specific Page**

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

### 2.4 Complete Example

Below is a ready-to-run `index.json` and `index.html`.

```json title='index.json'
{
  "name": "Homepage",
  "action": "index",
  "vars": {
    "hero_title": {
      "title": "Hero Title",
      "type": "text",
      "default": "Welcome to the Homepage"
    }
  },
  "fieldsets": {
    "featured": {
      "title": "Featured Section",
      "vars": {
        "news": {
          "title": "Select Category",
          "type": "datasource",
          "source": "category",
          "multiple": true
        },
        "count": {
          "title": "Display Count",
          "type": "number",
          "default": 4
        }
      }
    }
  }
}
```

```django title='index.html'
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

## 3. Article List Page Template Development

The article list page displays all articles under a specified category. It shares the `{% articles %}` tag with the
homepage but uses pagination mode. Additionally, the list page view injects the current category's `category` object.

### 3.1 category Object

The list page view automatically injects the `category` object into the template context for direct use:

| Field                   | Description                                           |
|-------------------------|-------------------------------------------------------|
| uuid                    | Category unique identifier                            |
| cover                   | Cover image path, must be used with `{% media_url %}` |
| template                | Template identifier, defaults to `list`               |
| is_active               | Whether active                                        |
| sort_order              | Sort weight                                           |
| parent                  | Parent category object or `None`                      |
| children                | Child category relation manager                       |
| translation.name        | Category name (current language)                      |
| translation.description | Category description (current language)               |

```django
<h1>{{ category.translation.name }}</h1>
{% if category.translation.description %}
  <p>{{ category.translation.description }}</p>
{% endif %}
```

### 3.2 Paginated Article List

The list page view only injects the `category` object; the article list must be fetched by the template itself via the
`{% articles %}` tag. Pagination parameters (like items per page) come from the theme configuration file or are
hardcoded in the template. Since the view cannot predict these variable names or values, delegating query condition
assembly to the template layer is the most straightforward approach.

```django
{% articles category=category.uuid page_num=request.GET.page|default:1 page_size=page_size as paged %}
```

!!! warning "page_num Starts from 1"

    `page_num` is 1-based. Avoid passing an empty or invalid request.GET.page value directly. Use |default:1 to provide
    a fallback when the value is empty or missing.

`paged` is a Django `Page` object with commonly used attributes:

| Attribute                    | Description                     |
|------------------------------|---------------------------------|
| paged.object_list            | Current page article list       |
| paged.number                 | Current page number             |
| paged.paginator.num_pages    | Total pages                     |
| paged.has_previous()         | Whether there's a previous page |
| paged.has_next()             | Whether there's a next page     |
| paged.previous_page_number() | Previous page number            |
| paged.next_page_number()     | Next page number                |

### 3.3 Pagination Component

After obtaining the `Page` object on the list page, use the `{% pagination %}` tag to render the pagination navigation.
This tag accepts a `Page` object and outputs pagination button HTML.

```django
{% pagination paged %}
```

If the default styling doesn't meet your needs, you can adjust CSS classes via parameters:

```django
{% pagination paged wing=2 ul_class="pagination justify-content-center" %}
```

| Parameter      | Type | Default    | Description                                                        |
|----------------|------|------------|--------------------------------------------------------------------|
| page_obj       | Page | Required   | Django pagination object                                           |
| wing           | int  | 4          | Number of page numbers to display on each side of the current page |
| ul_class       | str  | pagination | CSS class for the `<ul>` element                                   |
| item_class     | str  | page-item  | CSS class for `<li>` elements                                      |
| link_class     | str  | page-link  | CSS class for `<a>` elements                                       |
| active_class   | str  | active     | Additional class for the current page                              |
| disabled_class | str  | disabled   | Additional class for disabled state                                |
| prev_label     | str  | «          | Previous page button text                                          |
| next_label     | str  | »          | Next page button text                                              |
| ellipsis_text  | str  | ...        | Ellipsis text                                                      |

### 3.4 Complete Example

```json title='list.json'
{
  "name": "Article List",
  "action": "list",
  "vars": {
    "page_size": {
      "title": "Items Per Page",
      "type": "number",
      "default": 10
    }
  }
}
```

```django title='list.html'
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
<p>No articles in this category yet.</p>
{% endif %}
```

## 4. Article Detail Page Template Development

The article detail page displays a complete article. Unlike the list page, the detail view automatically injects the
`article` object, which can be used directly in the template without needing to fetch it via tags.

### 4.1 Available Fields in the article Object

The view-injected `article` object contains the article master table fields, current language translation content, and
service-layer-attached resource grouping fields. Access them in templates as follows:

| Field                | Description                                    |
|----------------------|------------------------------------------------|
| uuid                 | Unique identifier                              |
| type                 | Type: `article` or `page`                      |
| template             | Template identifier, defaults to `article`     |
| cover                | Cover image path (ImageField)                  |
| status               | Status string                                  |
| sort_order           | Sort weight                                    |
| extra                | Extended JSON data                             |
| is_top               | Whether pinned to top                          |
| is_recommended       | Whether recommended                            |
| published_at         | Publication time                               |
| created_at           | Creation time                                  |
| updated_at           | Update time                                    |
| categories           | Associated categories (ManyToMany)             |
| translation.title    | Title                                          |
| translation.subtitle | Subtitle                                       |
| translation.summary  | Summary                                        |
| translation.content  | Body content                                   |
| gallery              | Gallery resource list (service-layer attached) |
| attachments          | Attachment resource list                       |
| videos               | Video resource list                            |
| audios               | Audio resource list                            |

### 4.2 Content and Metadata Output

Article detail pages typically need to display basic information like title, publication time, and body content:

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

!!! warning "Body Output Filtering"

    The Content app's backend editor is a rich text editor, and `article.translation.content` stores raw content with HTML
    tags. When outputting in templates, you must use the `|safe` filter; otherwise, HTML tags will be escaped and displayed
    as text on the page.

### 4.3 Cover Image

If an article has an uploaded cover image, it's typically displayed above the title or in a sidebar:

```django
{% if article.cover %}
  {% media_url article.cover as cover_url %}
  <img src="{{ cover_url }}" alt="{{ article.translation.title }}">
{% endif %}
```

### 4.4 Resource Handling

The Content app stores article resources (gallery, attachments, videos, audios) separately in a resource association
table, not mixed into the body content. This design supports multilingual content: when switching languages, the body
content changes, but resource files don't need to be re-uploaded — all language versions share the same set of
resources.

When fetching article details, the service layer prefetches and categorizes resources by usage into four lists:

| Attribute           | Description                                 |
|---------------------|---------------------------------------------|
| article.gallery     | Gallery resources (`usage="gallery"`)       |
| article.attachments | Attachment resources (`usage="attachment"`) |
| article.videos      | Video resources (`usage="video"`)           |
| article.audios      | Audio resources (`usage="audio"`)           |

Render each resource type separately in the template.

**Gallery Rendering**

Galleries are typically displayed as image grids or carousels below the body content:

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

**Attachment List**

Attachments are typically displayed as downloadable links:

```django
{% if article.attachments %}
<ul class="attachments">
  {% for res in article.attachments %}
    <li>
      <a href="{% media_url res.resource.url %}" download>
        {{ res.resource.original_name|default:res.alt }}
      </a>
    </li>
  {% endfor %}
</ul>
{% endif %}
```

**Videos**

```django
{% if article.videos %}
  {% for res in article.videos %}
    {% media_url res.resource.url as video_url %}
    <video src="{{ video_url }}" controls></video>
  {% endfor %}
{% endif %}
```

**Audios**

```django
{% if article.audios %}
  {% for res in article.audios %}
    {% media_url res.resource.url as audio_url %}
    <audio src="{{ audio_url }}" controls></audio>
  {% endfor %}
{% endif %}
```

!!! note "Resource Field Description"

    `res.alt` is a field in the article resource table, used as alternative text when resources fail to load. The
    information is entered in the backend.

    `res.resource` is a Pinmok Resource model instance. Commonly available fields include:

    | Field | Type | Meaning |
    |---|---|---|
    | url | String | Relative storage path of the resource, needs to be converted to an actual address |
    | original_name | String | Original filename when the resource was uploaded |
    | size | Integer | File size |
    | file_type | String | File type, values: image, video, audio, document, archive |
    | created_at | DateTime | Upload time, format: 2026-08-17 01:12:48.487793 |

### 4.5 Category Affiliation

Articles may belong to multiple categories. Displaying category entry points at the bottom of the detail page is a
common practice:

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

### 4.6 Complete Example

```json title='article.json'
{
  "name": "Article Detail",
  "action": "article"
}
```

```django title='article.html'
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
        <h3>Gallery</h3>
        {% for res in article.gallery %}
        {% media_url res.resource.url as img_url %}
        <img src="{{ img_url }}" alt="{{ res.alt }}">
        {% endfor %}
    </div>
    {% endif %}
    
    {% if article.attachments %}
    <div class="attachments">
        <h3>Attachments</h3>
        <ul>
            {% for res in article.attachments %}
            <li>
                <a href="{% media_url res.resource.url %}" download>
                    {{ res.resource.original_name|default:res.alt }}
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

## 5. Page Detail

The page detail is highly similar to the article detail page. Since pages share the same data model as articles at the
data level, the view-injected `page` object has fields identical to `article`. When writing templates, just note the
following:

- The view-injected variable name is `page`, not `article`
- Pages typically have no category affiliation (`page.categories` is empty)
- Pages don't have attributes like pinning or recommendations

Therefore, simply replace `article` with `page` in the template.

```django
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

!!! tip "Page Template Naming"

    The default page template filename is `page.html`, with corresponding configuration file `page.json` and action `page`.
    If your project has many pages with significant style differences, you can specify different template identifiers for
    different pages in the backend (requires model configuration), and provide the corresponding template files in the
    theme.
