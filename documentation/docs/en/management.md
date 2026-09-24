# Content Management

This chapter covers how to manage content from the Pinmok admin panel. If you are already familiar with CMS concepts, expand the **Quick Start** section below for a high-level overview.

??? abstract "Quick Start"

    The content management backend consists of three modules:

    - **Categories**: A way to organize content. Templates use categories to filter and display content—for example, "show the latest 5 articles from the News category."
    - **Articles**: Standard content entries that must belong to a category.
    - **Pages**: Standalone content that does not belong to any category. Pages are retrieved directly by their unique slug.

    Articles and pages share the same data structure and editing interface. The only difference is that pages do not have a category field.

    All three modules support multiple languages. Shared fields (category, status, cover image, etc.) remain consistent across all languages, while translatable fields (title, content, summary) are filled in per-language tabs. If a translation is missing, the system falls back to the default language.

## Categories

A category is an organizational dimension for your content. A "Company News" article belongs to the "News" category; a "Product Manual" belongs to the "Docs" category. Frontend templates use categories to filter and display content—for example, "show the latest 5 articles from the News category."

**A category is not navigation.** Navigation is the menu structure of your site and is managed separately by Pinmok's navigation module. A category is a content attribute that defines *what type of content this is*. A single category can be referenced by multiple navigation items, or by none at all if it is only used for template filtering.

### Creating a Category

Go to **Content > Categories** in the admin panel and click **Add**:

![Adding a category](assets/images/category_add.en.png)

#### Basic Information

| Field | Description |
|-------|-------------|
| **Parent Category** | If hierarchical categories are enabled, select a parent here. Defaults to top-level. |
| **Cover Image** | A display image for the category, which can be referenced in templates. |
| **Template** | The template used to render this category on the frontend. Follows Pinmok template rules: if multiple templates are available, they appear in the dropdown; otherwise only **Default** is shown. |
| **Sort Order** | A numeric weight for ordering categories. Lower values appear first in both the admin list and frontend queries. |
| **Enabled** | Controls whether the category is active. When disabled, articles under this category are hidden on the frontend, but the articles themselves are not deleted. |

#### Translations

In the **Category Translations** section, select a language from the dropdown and enter the corresponding name and description. To add another language, click **Add another Category Translation** and repeat.

!!! tip "Tip"

    You do not need to fill in every translation. When content is retrieved, the system automatically falls back to the default language if a translation is missing. For example, if your system supports four languages with English as the default, and you have only filled in English and Chinese, a French visitor will see the English version.

Once saved, the category becomes available in the article edit form.

## Articles

### Publishing an Article

Go to **Content > Articles** in the admin panel and click **Add**:

![Adding an article](assets/images/article_add.en.png)

#### Translatable Content

| Field | Required | Description |
|-------|----------|-------------|
| **Language** | Yes | Fill in the default language first. Additional languages can be added after saving. |
| **Title** | Yes | The article title. |
| **Subtitle** | No | Usually displayed alongside the title in the article header. |
| **Summary** | No | A short description used in list views. |
| **Content** | No | The article body. Uses a rich-text editor supporting images, tables, and code blocks. |

#### Article Properties

| Field | Required | Description |
|-------|----------|-------------|
| **Category** | Yes | The category this article belongs to. Categories must be created before you can assign them. |
| **Cover Image** | No | Used for list thumbnails and social sharing. Supports cropping. |
| **Template** | No | The template used to render this article on the frontend. Same rules as category templates. |
| **Sort Order** | No | A numeric weight for ordering. Defaults to `10000`. This value is factored into all article list queries regardless of the primary sort field. |
| **Extra Data** | No | JSON-formatted data for custom use by frontend templates or developers. |
| **Pinned** | No | Pins the article so it appears at the top of lists. |
| **Featured** | No | Marks the article as featured, allowing templates to pull it separately. |

Click **Save** or **Save and continue editing** to store the article as a draft.

#### Article Resources

You can attach additional resource files (images, media, documents) to an article. Common use cases include photo galleries, downloadable files, or custom template integrations.

Click **Add another Article Resource** to add a row:

![Adding a resource](assets/images/add_resource.en.png)

- **Magnifying glass icon**: Opens the resource library to select an existing file.
- **Plus icon**: Opens the upload dialog to add a new file to the library.
- After uploading, close the dialog and click the magnifying glass again to select the newly uploaded file.
- Click **Save** to associate the selected resources with the article.

!!! tip "Tip"

    Uploaded resources are stored in the Pinmok resource library. The system deduplicates files based on SHA-256 hashing, so uploading the same image twice stores only one physical copy.

### Status & Workflow

Articles move through the following statuses from creation to publication:

| Status | Description | Frontend Visibility |
|--------|-------------|---------------------|
| **Draft** | Initial state. Content is incomplete or awaiting internal review. | Hidden |
| **Pending Review** | Content is complete and has been submitted for approval. | Hidden |
| **Rejected** | Reviewer returned the article for revision. | Hidden |
| **Published** | Approved and live on the site. | Visible |
| **Withdrawn** | Previously published content has been taken offline. Can be edited and republished. | Hidden |

Status transitions are governed by role-based permissions:

- **Regular editors** can save as **Draft** or submit for review. Once submitted, the article enters **Pending Review** and becomes read-only for the editor.
- **Reviewers** can **Publish** or **Reject** articles in **Pending Review**. Rejected articles return to an editable state.
- **Published** articles can be **Withdrawn** by a reviewer. Withdrawn articles return to an editable state.

!!! note "Note"

    Only articles in **Draft** or **Rejected** status can be edited directly. Articles in **Pending Review** or **Published** status must first be changed (rejected or withdrawn) before they can be modified.

### Article List Operations

From the article list view, you can:

![Article list](assets/images/article_list.en.png)

- **Search**: Find articles by title keyword.
- **Sort**: Click column headers to sort by creation time, publish time, sort order, etc.
- **Filter**: Narrow results by category, status, or pinned/featured flags.
- **Batch actions**: Select multiple articles to change their status or delete them in bulk.

## Pages

### Pages vs. Articles

Pages share the same data structure and editing interface as articles, but differ in two key ways:

- **No category**: Pages do not require or display a category field.
- **Direct retrieval**: Pages are fetched directly by their unique slug, rather than through a category list.

### When to Use Pages

Pages are ideal for standalone content that does not belong to any category, such as:

- About Us
- Contact
- Terms of Service
- Help Center Home

### Creating a Page

Go to **Content > Pages** in the admin panel. The workflow is identical to articles: fill in the title, body, status, and cover image. The only difference is the absence of a **Category** field.

Pages also support multiple languages. Switch language tabs to enter translations.

!!! note "Note"

    Pages and articles share the same underlying data model. The system distinguishes them internally, which is completely transparent to users. Use **Articles** when you need a category; use **Pages** when you do not.
