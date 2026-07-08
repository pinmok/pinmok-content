#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
content.admin module

Description:
  Admin configuration for Content module.
Author:
  惠达浪 <crazys@126.com>
Created:
  2026/03/21
"""
from django.conf import settings
from django.contrib import messages, admin
from django.core.exceptions import PermissionDenied
from django.db.models import Case, When, IntegerField
from django.db.models.fields import BooleanField
from django.urls import reverse_lazy
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _

from pinmok import padmin
from pinmok.content.apps import ContentConfig
from pinmok.content.enums import ArticleStatus, ArticleType, ArticleSubmitAction, TemplateAction
from pinmok.content.models import Article, ArticleResource, ArticleTranslation, Page, Category, CategoryTranslation
from pinmok.content.service.article import ArticleService
from pinmok.content.service.category import CategoryService
from pinmok.padmin.fields import IndentedModelChoiceField
from pinmok.padmin.options import PinmokModelAdmin, PinmokStackedInline, PinmokTabularInline
from pinmok.padmin.service.theme import ThemeService
from pinmok.padmin.widgets import PinmokSelect, PinmokSwitch


class CategoryTranslationInline(PinmokStackedInline):
    model = CategoryTranslation
    extra = 0
    min_num = 1
    max_num = len(settings.LANGUAGES)
    fieldsets = [(None, {'fields': [('name', 'language'), 'description']})]


@padmin.register(Category)
class CategoryAdmin(PinmokModelAdmin):
    menu_sort_order = 3000
    inlines = [CategoryTranslationInline]
    list_display = ['sort_order', 'get_name', 'get_cover', 'parent', 'is_active']
    list_editable = ['is_active', 'sort_order']
    list_display_links = ['get_name', 'get_cover', ]
    search_fields = ['translations__name']
    image_crop_fields = ['cover']

    fieldsets = [
        (None, {'fields': [
            'parent',
            ('cover', 'template', 'sort_order', 'is_active'),
        ]}),
    ]

    @admin.display(description=_('name'))
    def get_name(self, obj):
        return str(obj)

    @admin.display(description=_('cover'))
    def get_cover(self, obj):
        if obj.cover:
            return format_html('<img src="{}" class="avatar">', obj.cover.url)
        return '-'

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'parent':
            obj_id = request.resolver_match.kwargs.get('object_id') if request.resolver_match else None
            exclude_id = int(obj_id) if obj_id else None  # type: ignore[arg-type]
            items = CategoryService.get_items(exclude_id=exclude_id)
            return IndentedModelChoiceField(
                pairs=items,
                queryset=Category.objects.exclude(pk=exclude_id) if exclude_id else Category.objects.all(),
                widget=PinmokSelect(),
                label=Category._meta.get_field('parent').verbose_name,  # type: ignore[union-attr]
                required=False,
                empty_label=_('Top Level'),
            )
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def formfield_for_dbfield(self, db_field, request, **kwargs):
        if db_field.name == 'template':
            kwargs['widget'] = PinmokSelect(choices=ThemeService.get_template_choices(ContentConfig.label, TemplateAction.LIST))
        return super().formfield_for_dbfield(db_field, request, **kwargs)

    def get_queryset(self, request):
        return Category.with_translations(super().get_queryset(request))


class ArticleResourceInline(PinmokTabularInline):
    model = ArticleResource
    extra = 0
    template = 'content/edit_inline/tabular_no_original.html'
    fields = ['resource', 'usage', 'alt', 'sort_order']


class ArticleTranslationInline(PinmokStackedInline):
    model = ArticleTranslation
    extra = 0
    template = 'content/edit_inline/translation_tabs.html'
    fields = ['language', 'title', 'subtitle', 'summary', 'content']
    rich_text_fields = ['content']

    def get_max_num(self, request, obj=None, **kwargs):
        """Hook for customizing the max number of extra inline forms."""
        return len(settings.LANGUAGES) if settings.USE_I18N else 1

    def get_queryset(self, request):
        """
        Override queryset to ensure the default language translation always appears first.

        Annotates each row with `is_default` (0 for default language, 1 for others),
        then orders by it so the default language tab is always rendered first in the UI.
        """
        qs = super().get_queryset(request)
        return qs.annotate(
            is_default=Case(
                When(language=settings.LANGUAGE_CODE, then=0),
                default=1,
                output_field=IntegerField()
            )
        ).order_by('is_default')

    def get_fields(self, request, obj=None):
        fields = list(super().get_fields(request, obj))
        if not settings.USE_I18N:
            fields = [f for f in fields if f != 'language']
        return fields


@padmin.register(Article)
class ArticleAdmin(PinmokModelAdmin):
    back_url = reverse_lazy('admin:content_article_changelist')
    change_form_template = 'content/articles.html'
    menu_sort_order = 1000
    image_crop_fields = [{'cover': {'aspectRatio': '4:3'}}]

    formfield_overrides = {
        **PinmokModelAdmin.formfield_overrides,
        BooleanField: {'widget': PinmokSwitch}
    }
    actions = ['retract_articles']
    fields = ['categories', 'cover', 'template', 'sort_order', 'extra', 'is_top', 'is_recommended']
    list_display = [
        'sort_order', 'get_title', 'categories_display', 'status_display',
        'published_at', 'is_top', 'is_recommended'
    ]
    list_display_links = ['get_title']
    list_filter = ['status']
    list_editable = ['is_top', 'is_recommended']
    search_fields = ['translations__title', 'translations__subtitle']
    date_hierarchy = 'published_at'
    autocomplete_fields = ['categories']

    inlines = [ArticleTranslationInline, ArticleResourceInline]

    @admin.display(description=_('title'), ordering='translations__title')
    def get_title(self, obj):
        return str(obj)

    @admin.display(description=_('status'))
    def status_display(self, obj):
        status = ArticleStatus(obj.status)
        return mark_safe(
            f'<span class="badge bg-{status.color} text-{status.color}-fg">{status.label}</span>'
        )

    @admin.display(description=_('categories'))
    def categories_display(self, obj):
        cats = obj.categories.all()
        if not cats:
            return '-'
        return ', '.join(str(c) for c in cats)

    @admin.action(description=_('Retract selected articles'))
    def retract_articles(self, request, queryset):
        # Only users with publish permission can retract articles
        if not request.user.has_perm(Article.PERM_PUBLISH):
            self.message_user(request, _('Permission denied'), level=messages.ERROR)

        # Only published articles are affected; other statuses are silently ignored
        count = queryset.filter(status=ArticleStatus.PUBLISHED).update(status=ArticleStatus.RETRACTED)
        self.message_user(request, _('%d articles retracted.') % count)

    def has_add_permission(self, request):
        return super().has_add_permission(request) and request.user.has_perm(Article.PERM_WRITE)

    def has_change_permission(self, request, obj: Article | None = None):
        if not super().has_change_permission(request, obj):
            return False
        return request.user.has_perm(Article.PERM_WRITE)

    def get_queryset(self, request):
        qs = Article.with_translations(
            super().get_queryset(request)
            .filter(type=ArticleType.ARTICLE)
            .prefetch_related('categories')
        )
        if request.GET.get('status__exact') != ArticleStatus.DELETED:
            qs = qs.exclude(status=ArticleStatus.DELETED)
        return qs

    def changeform_view(
            self,
            request,
            object_id=None,
            form_url='',
            extra_context=None
    ):
        extra_context = extra_context or {}

        if object_id:
            obj = self.get_object(request, object_id)
            current_status = obj.status if obj else ArticleStatus.DRAFT
        else:
            current_status = ArticleStatus.DRAFT

        has_publish = request.user.has_perm(Article.PERM_PUBLISH)
        extra_context['transition_buttons'] = ArticleService.get_transition_buttons(
            current_status, has_publish
        )
        extra_context['has_publish_perm'] = has_publish
        extra_context['show_save'] = ArticleService.show_save_button(current_status)

        return super().changeform_view(request, object_id, form_url, extra_context)

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if 'categories' in form.base_fields:
            form.base_fields['categories'].required = True
        return form

    def save_model(self, request, obj, form, change):
        has_publish = request.user.has_perm(Article.PERM_PUBLISH)

        action = next(
            (ArticleSubmitAction(key) for key in request.POST if key in ArticleSubmitAction.values),
            None,
        )
        target_status = action.target_status if action else None

        if target_status is not None:
            current_status = (
                Article.objects.filter(pk=obj.pk).values_list('status', flat=True).first()
                if change else ArticleStatus.DRAFT
            )
            try:
                ArticleService.validate_transition(current_status, target_status, has_publish)
                ArticleService.apply_transition(obj, target_status)
            except ValueError as exc:
                self.message_user(request, str(exc), level=messages.ERROR)
                obj.status = current_status
            except PermissionDenied:
                self.message_user(
                    request,
                    _('You do not have permission to publish articles.'),
                    level=messages.ERROR
                )
                obj.status = current_status

        super().save_model(request, obj, form, change)

    def formfield_for_dbfield(self, db_field, request, **kwargs):
        if db_field.name == 'template':
            kwargs['widget'] = PinmokSelect(choices=ThemeService.get_template_choices(ContentConfig.label, TemplateAction.ARTICLE))
        return super().formfield_for_dbfield(db_field, request, **kwargs)


@padmin.register(Page)
class PageAdmin(ArticleAdmin):
    """
    Admin for Page type articles.
    No categories; slug required for URL routing.
    """
    menu_sort_order = 2000
    fields = ['cover', 'template', 'sort_order', 'extra']
    list_display = ['get_title', 'status_display', 'published_at']
    list_editable = []

    def get_queryset(self, request):
        qs = (
            super(ArticleAdmin, self).get_queryset(request)
            .filter(type=ArticleType.PAGE)
            .prefetch_related('translations')
        )
        if request.GET.get('status__exact') != ArticleStatus.DELETED:
            qs = qs.exclude(status=ArticleStatus.DELETED)
        return qs
