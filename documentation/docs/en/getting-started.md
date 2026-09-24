# Getting Started

## Introduction

`pinmok-content` is a content management app built on Pinmok, designed for websites, mobile apps, and other scenarios that require content
presentation. It provides backend management for articles, pages, categories, and tags. On the frontend, you can either render pages through
theme templates or fetch data via the built-in read-only REST API, making it flexible enough to work with any frontend technology stack.

Before proceeding, make sure Pinmok is installed and running correctly. `pinmok-content` does not introduce any additional environment
requirements.

## Installation

Activate your Django project's virtual environment and run:

```bash
pip install pinmok-content
```

## Configuration

### settings.py

Add `pinmok.content` to `INSTALLED_APPS`, anywhere after `pinmok.padmin`:

```python title="settings.py"
INSTALLED_APPS = [
    'pinmok.padmin',
    'pinmok.content',
    # ...
]
```

### urls.py

Add the following route to your project's `urls.py`:

```python title="urls.py"
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('pinmok.content.urls')),  # add this line
    # ...
]
```

> **Note:** If you use a non-empty prefix, such as `path('content/', include('pinmok.content.urls'))`, all URLs including the REST API will
> be placed under that prefix. For example, the API endpoint would become `/content/api/articles/`.

## Migration

Run the database migration:

```bash
python manage.py migrate
```

## Sync Menus

Start the server, log in to the Pinmok admin, and click the sync button (☰) at the top of the left sidebar. Once synced, the content
management menu will appear with the correct name and icon.

---

Installation complete. You're ready to use pinmok-content.