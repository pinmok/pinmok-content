"""
pinmok-content API 测试

放置位置：pinmok/content/tests.py

运行方式：
    python manage.py test pinmok.content
或在 PyCharm 里右键文件/类/方法 -> Run 'Test ...'
"""

from django.core.cache import cache
from django.test import TestCase

from pinmok.content.enums import ArticleStatus
from pinmok.content.models import Article, Category, CategoryTranslation, ArticleTranslation, Page


# ---------------------------------------------------------------------------
# 基类：每个测试方法结束后自动清空缓存，避免测试间缓存污染
# ---------------------------------------------------------------------------

class ContentTestCase(TestCase):
    def tearDown(self):
        cache.clear()


# ---------------------------------------------------------------------------
# 测试数据工厂函数
# ---------------------------------------------------------------------------

def _create_category(name="测试分类", parent=None):
    """
    建一个分类 + 对应的中文翻译记录。
    name/description 在 CategoryTranslation 里，不在 Category 本身。
    """
    category = Category.objects.create(parent=parent)
    CategoryTranslation.objects.create(
        category=category,
        language='zh-hans',
        name=name,
    )
    return category


def _create_article(title="测试文章", status=ArticleStatus.PUBLISHED,
                    categories=None, **extra):
    """
    建一篇文章 + 对应的中文翻译记录。
    title/summary/content 在 ArticleTranslation 里，不在 Article 本身。
    status/type/is_top 等字段直接在 Article 上，可以通过 extra 传入。
    """
    article = Article.objects.create(status=status, **extra)
    ArticleTranslation.objects.create(
        article=article,
        language='zh-hans',
        title=title,
    )
    if categories:
        # noinspection PyUnresolvedReferences
        article.categories.set(categories)
    return article


def _create_page(title="测试页面"):
    """
    建一个页面。Page 是 Article 的代理模型，save() 里自动把 type 设成 PAGE。
    """
    page = Page.objects.create(status=ArticleStatus.PUBLISHED)
    ArticleTranslation.objects.create(
        article=page,
        language='zh-hans',
        title=title,
    )
    return page


def _data(response):
    """从 success()/error() 的信封里取出 data 部分。"""
    return response.json()["data"]


# ---------------------------------------------------------------------------
# 测试类
# ---------------------------------------------------------------------------

class ArticleAPIBasicTest(ContentTestCase):
    """最基础的一组：接口能不能正常返回、分页对不对。"""

    def setUp(self):
        self.category = _create_category()
        self.article = _create_article(categories=[self.category])

    def test_article_list_returns_200(self):
        response = self.client.get("/api/list/")
        self.assertEqual(response.status_code, 200)

    def test_article_list_contains_created_article(self):
        response = self.client.get("/api/list/")
        uuids = [item["uuid"] for item in _data(response)["items"]]
        self.assertIn(str(self.article.uuid), uuids)

    def test_article_detail_returns_200(self):
        response = self.client.get(f"/api/article/{self.article.uuid}/")
        self.assertEqual(response.status_code, 200)

    def test_pagination_second_page_no_overlap(self):
        for i in range(30):
            _create_article(title=f"批量文章 {i}", categories=[self.category])

        page1 = _data(self.client.get("/api/list/?page=1"))
        page2 = _data(self.client.get("/api/list/?page=2"))

        uuids_page1 = {item["uuid"] for item in page1["items"]}
        uuids_page2 = {item["uuid"] for item in page2["items"]}
        self.assertEqual(uuids_page1 & uuids_page2, set())


class ArticleAPICategoryFilterTest(ContentTestCase):
    """测代码审查里修过的分类筛选相关 bug。"""

    def setUp(self):
        self.category_a = _create_category("分类A")
        self.category_b = _create_category("分类B")
        self.empty_category = _create_category("没有文章的分类")
        self.article_a = _create_article("属于分类A", categories=[self.category_a])
        self.article_b = _create_article("属于分类B", categories=[self.category_b])

    def test_filter_by_nonexistent_category_returns_empty_list(self):
        fake_uuid = "00000000-0000-0000-0000-000000000000"
        response = self.client.get(f"/api/list/?category={fake_uuid}")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(_data(response)["items"], [])

    def test_filter_by_real_empty_category_returns_empty_list(self):
        response = self.client.get(f"/api/list/?category={self.empty_category.uuid}")
        self.assertEqual(_data(response)["items"], [])

    def test_filter_by_multiple_categories_uses_or_logic(self):
        url = f"/api/list/?category={self.category_a.uuid},{self.category_b.uuid}"
        response = self.client.get(url)
        uuids = {item["uuid"] for item in _data(response)["items"]}
        self.assertIn(str(self.article_a.uuid), uuids)
        self.assertIn(str(self.article_b.uuid), uuids)

    def test_invalid_category_uuid_returns_400(self):
        response = self.client.get("/api/list/?category=not-a-uuid")
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["code"], 40001)


class ArticleAPIOrderingTest(ContentTestCase):
    """测排序参数的白名单校验。"""

    def setUp(self):
        self.category = _create_category()
        _create_article("A", categories=[self.category])
        _create_article("B", categories=[self.category])

    def test_order_by_whitelisted_fields_work(self):
        for field in ["published_at", "-published_at", "created_at",
                      "-created_at", "sort_order", "-sort_order"]:
            response = self.client.get(f"/api/list/?order={field}")
            self.assertEqual(response.status_code, 200, f"order={field} 应该被允许")

    def test_order_by_non_whitelisted_field_returns_400(self):
        response = self.client.get("/api/list/?order=__class__")
        self.assertEqual(response.status_code, 400)


class ArticleAPITopRecommendedTest(ContentTestCase):
    """测 top/recommended 筛选参数。"""

    def setUp(self):
        self.category = _create_category()
        self.top_article = _create_article(
            "置顶文章", categories=[self.category], is_top=True
        )
        self.normal_article = _create_article(
            "普通文章", categories=[self.category], is_top=False
        )

    def test_top_only_filter(self):
        response = self.client.get("/api/list/?top=1")
        uuids = {item["uuid"] for item in _data(response)["items"]}
        self.assertIn(str(self.top_article.uuid), uuids)
        self.assertNotIn(str(self.normal_article.uuid), uuids)


class ArticleAPISafeUrlTest(ContentTestCase):
    """测 _safe_url()：没有封面图时详情接口不应该报错，cover 字段应返回空字符串。"""

    def setUp(self):
        self.category = _create_category()
        self.article = _create_article(categories=[self.category])
        # cover 字段默认是 null/blank，不需要额外设置

    def test_detail_without_cover_returns_empty_string(self):
        response = self.client.get(f"/api/article/{self.article.uuid}/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(_data(response)["cover"], "")


class ArticleAPIVisibilityTest(ContentTestCase):
    """草稿/待审核/撤回状态的文章，不应该能通过公开只读 API 查到。"""

    def setUp(self):
        self.category = _create_category()
        self.draft = _create_article(
            "草稿", status=ArticleStatus.DRAFT, categories=[self.category]
        )
        self.pending = _create_article(
            "待审核", status=ArticleStatus.PENDING, categories=[self.category]
        )
        self.retracted = _create_article(
            "已撤回", status=ArticleStatus.RETRACTED, categories=[self.category]
        )
        self.published = _create_article(
            "已发布", status=ArticleStatus.PUBLISHED, categories=[self.category]
        )

    def test_draft_not_accessible_via_detail(self):
        response = self.client.get(f"/api/article/{self.draft.uuid}/")
        self.assertEqual(response.status_code, 404)

    def test_pending_not_accessible_via_detail(self):
        response = self.client.get(f"/api/article/{self.pending.uuid}/")
        self.assertEqual(response.status_code, 404)

    def test_retracted_not_accessible_via_detail(self):
        response = self.client.get(f"/api/article/{self.retracted.uuid}/")
        self.assertEqual(response.status_code, 404)

    def test_only_published_appears_in_list(self):
        response = self.client.get("/api/list/")
        uuids = {item["uuid"] for item in _data(response)["items"]}
        self.assertIn(str(self.published.uuid), uuids)
        self.assertNotIn(str(self.draft.uuid), uuids)
        self.assertNotIn(str(self.pending.uuid), uuids)
        self.assertNotIn(str(self.retracted.uuid), uuids)


class PageVsArticleTypeTest(ContentTestCase):
    """
    验证 article/page 两个接口是否真的按 type 区分。
    Page 是 Article 的代理模型，save() 自动把 type 设成 PAGE。
    """

    def setUp(self):
        self.category = _create_category()
        self.article = _create_article("普通文章", categories=[self.category])
        self.page = _create_page("普通页面")

    def test_article_uuid_not_accessible_via_page_endpoint(self):
        """用文章的 uuid 请求 /api/pages/，期望 404。"""
        response = self.client.get(f"/api/pages/{self.article.uuid}/")
        self.assertEqual(response.status_code, 404)

    def test_page_uuid_not_accessible_via_article_endpoint(self):
        """用页面的 uuid 请求 /api/article/，期望 404。"""
        response = self.client.get(f"/api/article/{self.page.uuid}/")
        self.assertEqual(response.status_code, 404)

    def test_page_accessible_via_page_endpoint(self):
        """用页面的 uuid 请求 /api/pages/，期望 200。"""
        response = self.client.get(f"/api/pages/{self.page.uuid}/")
        self.assertEqual(response.status_code, 200)


class CategoryAPITest(ContentTestCase):
    """分类列表和详情接口。"""

    def setUp(self):
        self.category = _create_category()

    def test_category_list_returns_200(self):
        response = self.client.get("/api/categories/")
        self.assertEqual(response.status_code, 200)

    def test_category_list_uses_items_key(self):
        self.assertIn("items", _data(self.client.get("/api/categories/")))

    def test_category_detail_returns_200(self):
        response = self.client.get(f"/api/categories/{self.category.uuid}/")
        self.assertEqual(response.status_code, 200)

    def test_category_detail_nonexistent_returns_404(self):
        response = self.client.get(
            "/api/categories/00000000-0000-0000-0000-000000000000/"
        )
        self.assertEqual(response.status_code, 404)
