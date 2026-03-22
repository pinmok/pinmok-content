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
from django.utils.translation import gettext_lazy as _

from djangocmf import cmfadmin
from djangocmf.cmfadmin.fields import IndentedModelChoiceField
from djangocmf.cmfadmin.options import CMFTabularInline, CMFModelAdmin, CMFStackedInline
from djangocmf.cmfadmin.widgets import CMFSelect
from djangocmf.content.models import TagTranslation, Tag, CategoryTranslation, Category
from djangocmf.content.service.category import CategoryService
from djangocmf.core.utils.helper import get_translated_name


class TagTranslationInline(CMFTabularInline):
    model = TagTranslation
    fields = ['language', 'name']

    def get_extra(self, request, obj=None, **kwargs):
        # No extra rows when editing existing object
        return 0 if obj else 1

    def get_max_num(self, request, obj=None, **kwargs):
        return len(settings.LANGUAGES)

    def formfield_for_dbfield(self, db_field, request, **kwargs):
        """
        Set the default language selection to the project's default language code.
        """
        field = super().formfield_for_dbfield(db_field, request, **kwargs)
        if db_field.name == 'language':
            field.initial = settings.LANGUAGE_CODE
            field.choices = [c for c in field.choices if c[0] != '']
        return field

    class Media:
        js = ['content/js/translation_inline.js']


@cmfadmin.register(Tag)
class TagAdmin(CMFModelAdmin):
    list_display = ['sort_order', 'get_default_name', 'is_active']
    list_display_links = ['get_default_name']
    list_editable = ['is_active', 'sort_order']
    search_fields = ['translations__name']
    inlines = [TagTranslationInline]
    fieldsets = [(None, {'fields': [('sort_order', 'is_active')]})]

    def get_default_name(self, obj):
        """
        Display tag name in default language, fallback to first available translation.
        """
        return get_translated_name(obj)

    get_default_name.short_description = _('name')


class CategoryTranslationInline(CMFStackedInline):
    model = CategoryTranslation
    fieldsets = [
        (None, {'fields': [('name', 'language'), 'description']}),
        ('SEO', {'fields': [('meta_title', 'meta_keywords'), 'meta_description'], 'classes': ['collapse']}),
    ]

    def get_extra(self, request, obj=None, **kwargs):
        return 0 if obj else 1

    def get_max_num(self, request, obj=None, **kwargs):
        return len(settings.LANGUAGES)

    def formfield_for_dbfield(self, db_field, request, **kwargs):
        field = super().formfield_for_dbfield(db_field, request, **kwargs)
        if db_field.name == 'language':
            field.initial = settings.LANGUAGE_CODE
            field.choices = [c for c in field.choices if c[0] != '']
        return field

    class Media:
        js = ['content/js/translation_inline.js']


@cmfadmin.register(Category)
class CategoryAdmin(CMFModelAdmin):
    list_display = ['sort_order', 'get_default_name', 'parent', 'is_active']
    list_display_links = ['get_default_name']
    list_editable = ['is_active', 'sort_order']
    search_fields = ['translations__name']
    inlines = [CategoryTranslationInline]
    fieldsets = [
        (None, {'fields': ['parent', ('sort_order', 'template', 'is_active')]}),
    ]

    def get_default_name(self, obj):
        """Display category name in default language, fallback to first available translation."""
        return get_translated_name(obj)

    get_default_name.short_description = _('name')

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'parent':
            items = CategoryService.get_items()
            kwargs['empty_label'] = _('Top Level')
            kwargs['queryset'] = Category.objects.all()
            return IndentedModelChoiceField(
                pairs=items,
                widget=CMFSelect,
                label=Category._meta.get_field('parent').verbose_name,
                required=False,
                **kwargs,
            )
        return super().formfield_for_foreignkey(db_field, request, **kwargs)
