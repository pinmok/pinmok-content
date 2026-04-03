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
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.db.models import Case, When, IntegerField
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _

from djangocmf import cmfadmin
from djangocmf.cmfadmin.admin import CMFModelAdmin
from djangocmf.cmfadmin.options import CMFStackedInline, CMFTabularInline
from djangocmf.cmfadmin.widgets import HugeRTEWidget
from djangocmf.content.enums import ArticleStatus, ArticleType
from djangocmf.content.models import Article, ArticleResource, ArticleTranslation, Page, Category
from djangocmf.content.service.article import ArticleService


@cmfadmin.register(Category)
class CategoryAdmin(CMFModelAdmin):
    menu_order = 3000
    list_display = ['sort_order', 'name', 'parent', 'is_active']
    list_display_links = ['name']
    list_editable = ['is_active', 'sort_order']
    search_fields = ['name']  # 这行之前被我删掉了
    fieldsets = [
        (None, {'fields': ['parent', ('sort_order', 'template', 'is_active')]}),
        (_('Content'), {'fields': ['name', 'description']}),
        (_('SEO'), {'fields': ['meta_title', 'meta_keywords', 'meta_description'], 'classes': ['collapse']}),
    ]


class ArticleResourceInline(CMFTabularInline):
    model = ArticleResource
    extra = 0
    template = 'content/edit_inline/tabular_no_original.html'
    fields = ['resource', 'usage', 'alt', 'sort_order']


class ArticleTranslationInline(CMFStackedInline):
    model = ArticleTranslation
    extra = 1
    max_num = len(settings.LANGUAGES)
    template = 'content/edit_inline/translation_tabs.html'
    fields = ['language_code', 'title', 'subtitle', 'summary', 'content',
              'meta_title', 'meta_description', 'meta_keywords']

    def formfield_for_dbfield(self, db_field, request, **kwargs):
        if db_field.name == 'content':
            kwargs['widget'] = HugeRTEWidget()
        return super().formfield_for_dbfield(db_field, request, **kwargs)

    def get_queryset(self, request):
        """
        Override queryset to ensure the default language translation always appears first.

        Annotates each row with `is_default` (0 for default language, 1 for others),
        then orders by it so the default language tab is always rendered first in the UI.
        """
        qs = super().get_queryset(request)
        return qs.annotate(
            is_default=Case(
                When(language_code=settings.LANGUAGE_CODE, then=0),
                default=1,
                output_field=IntegerField()
            )
        ).order_by('is_default')


@cmfadmin.register(Article)
class ArticleAdmin(CMFModelAdmin):
    back_url = reverse_lazy('admin:content_article_changelist')
    change_form_template = 'content/articles.html'
    menu_order = 1000

    fields = ['categories', 'cover', 'template', 'sort_order', 'extra']
    list_display = ['get_title', 'status_display', 'sort_order', 'published_at']
    list_display_links = ['get_title']
    list_filter = ['status']
    search_fields = ['translations__title', 'translations__subtitle']
    date_hierarchy = 'published_at'
    autocomplete_fields = ['categories']

    inlines = [ArticleTranslationInline, ArticleResourceInline]

    image_crop_fields = {'cover': {'aspectRatio': '16:9'}}

    _SUBMIT_ACTIONS = {
        '_submit_pending': ArticleStatus.PENDING,
        '_submit_publish': ArticleStatus.PUBLISHED,
        '_submit_reject': ArticleStatus.RETURNED,
        '_submit_delete': ArticleStatus.DELETED,
    }

    def get_title(self, obj):
        translation = obj.get_translation()
        return translation.title if translation else f'({obj.article_uuid})'

    get_title.short_description = _('title')
    get_title.admin_order_field = 'translations__title'

    def status_display(self, obj):
        return obj.get_status_display()

    status_display.short_description = _('status')
    status_display.admin_order_field = 'status'

    def has_add_permission(self, request):
        return super().has_add_permission(request) and request.user.has_perm('content.write_article')

    def has_change_permission(self, request, obj=None):
        return super().has_change_permission(request, obj) and request.user.has_perm('content.write_article')

    def get_queryset(self, request):
        qs = (
            super().get_queryset(request)
            .filter(type=ArticleType.ARTICLE)
            .prefetch_related('translations')
        )
        if request.GET.get('status__exact') != ArticleStatus.DELETED:
            qs = qs.exclude(status=ArticleStatus.DELETED)
        return qs

    def changeform_view(self, request, object_id=None, form_url='', extra_context=None):
        extra_context = extra_context or {}

        if object_id:
            obj = self.get_object(request, object_id)
            current_status = obj.status if obj else ArticleStatus.DRAFT
        else:
            current_status = ArticleStatus.DRAFT

        has_publish = request.user.has_perm('content.publish_article')
        extra_context['transition_buttons'] = ArticleService.get_transition_buttons(
            current_status, has_publish
        )
        extra_context['has_publish_perm'] = has_publish
        extra_context['show_save'] = ArticleService.show_save_button(current_status, has_publish)

        return super().changeform_view(request, object_id, form_url, extra_context)

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        form.base_fields['categories'].required = True
        return form

    def save_model(self, request, obj, form, change):
        has_publish = request.user.has_perm('content.publish_article')

        target_status = next(
            (status for key, status in self._SUBMIT_ACTIONS.items() if key in request.POST),
            None
        )

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


@cmfadmin.register(Page)
class PageAdmin(ArticleAdmin):
    """
    Admin for Page type articles.
    No categories; slug required for URL routing.
    """
    menu_order = 2000
    fields = ['slug', 'cover', 'template', 'sort_order', 'extra']

    def get_queryset(self, request):
        qs = (
            super(ArticleAdmin, self).get_queryset(request)
            .filter(type=ArticleType.PAGE)
            .prefetch_related('translations')
        )
        if request.GET.get('status__exact') != ArticleStatus.DELETED:
            qs = qs.exclude(status=ArticleStatus.DELETED)
        return qs
