#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
content.models module

Description:
  Models for Content of DjangoCMF
Author:
  惠达浪 <crazys@126.com>
Created:
  2026-01-16
"""

from django.db import models
from django.utils.translation import gettext_lazy as _


class Category(models.Model):
    name = models.CharField(max_length=100, verbose_name=_("Category Name"))
    slug = models.SlugField(max_length=120, unique=True, verbose_name=_("Slug"))

    parent = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        related_name="children",
        on_delete=models.CASCADE,
        verbose_name=_("Parent Category")
    )

    sort_order = models.IntegerField(default=0, verbose_name=_("Sort Order"))
    status = models.BooleanField(default=True, verbose_name=_("Status"))

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("Category")
        verbose_name_plural = _("Categories")
        ordering = ["sort_order", "id"]

    def __str__(self):
        return self.name
