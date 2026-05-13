#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
article module

Description:
  Article service for the content app.
Author:
  惠达浪 <crazys@126.com>
Created:
  2026/3/24
"""
from django.core.exceptions import PermissionDenied
from django.db.models import F
from django.utils import timezone
from django.utils.translation import gettext_lazy as _, get_language

from pinmok.content.enums import ArticleStatus, ArticleSubmitAction, ArticleType
from pinmok.content.models import Article


class ArticleService:
    # --- status transition rules ---
    TRANSITIONS = {
        ArticleStatus.DRAFT: [ArticleStatus.PENDING, ArticleStatus.PUBLISHED],
        ArticleStatus.PENDING: [ArticleStatus.RETURNED, ArticleStatus.PUBLISHED],
        ArticleStatus.PUBLISHED: [ArticleStatus.RETRACTED],
        ArticleStatus.RETURNED: [ArticleStatus.PENDING, ArticleStatus.PUBLISHED],
        ArticleStatus.RETRACTED: [ArticleStatus.PENDING, ArticleStatus.PUBLISHED],
        ArticleStatus.DELETED: [],
    }
    PUBLISH_REQUIRED = {ArticleStatus.PUBLISHED, ArticleStatus.RETURNED}

    # Save button visibility per status
    # PENDING and PUBLISHED: only publish-perm users can meaningfully save
    SAVE_ALLOWED = {
        ArticleStatus.DRAFT,
        ArticleStatus.RETURNED,
        ArticleStatus.RETRACTED,
    }

    @classmethod
    def get_allowed_transitions(cls, current_status):
        """Return list of allowed next statuses for the given current status."""
        return cls.TRANSITIONS.get(current_status, [])

    @classmethod
    def validate_transition(cls, current_status, target_status, has_publish_perm):
        """
        Validate a status transition.
        Raises ValueError on illegal transition, PermissionDenied on missing permission.
        """
        allowed = cls.get_allowed_transitions(current_status)
        if target_status not in allowed:
            raise ValueError(
                _('Invalid status transition: %(from)s → %(to)s') % {
                    'from': current_status,
                    'to': target_status,
                }
            )
        if target_status in cls.PUBLISH_REQUIRED and not has_publish_perm:
            raise PermissionDenied

    @classmethod
    def apply_transition(cls, obj, target_status):
        """Apply a validated status transition to an Article instance."""
        obj.status = target_status
        if target_status == ArticleStatus.PUBLISHED and not obj.published_at:
            obj.published_at = timezone.now()

    @classmethod
    def get_transition_buttons(cls, current_status, has_publish_perm):
        """
        Return button config list for the changeform submit row.

        Each button dict has:
          name    — POST key, matched in ArticleSubmitAction
          label   — display text
          class   — Bootstrap btn class for styling
        Save button is always rendered separately in the template.
        """

        def btn(action: ArticleSubmitAction, css: str) -> dict:
            return {'name': action.value, 'label': action.label, 'class': css}

        buttons = []
        match current_status:
            case ArticleStatus.DRAFT | ArticleStatus.RETURNED | ArticleStatus.RETRACTED:
                if has_publish_perm:
                    buttons = [btn(ArticleSubmitAction.PUBLISH, 'btn-success')]
                else:
                    buttons = [btn(ArticleSubmitAction.PENDING, 'btn-warning')]

            case ArticleStatus.PENDING if has_publish_perm:
                buttons = [
                    btn(ArticleSubmitAction.PUBLISH, 'btn-success'),
                    btn(ArticleSubmitAction.REJECT, 'btn-danger'),
                ]

            case ArticleStatus.PUBLISHED if has_publish_perm:
                buttons = [btn(ArticleSubmitAction.RETRACT, 'btn-danger')]

            case _:
                pass

        return buttons

    @classmethod
    def show_save_button(cls, current_status):
        """Return whether the plain Save button should be shown."""
        return current_status in cls.SAVE_ALLOWED

    @staticmethod
    def get_pages():
        """
        Return published PAGE articles with title in current language.

        Returns:
            QuerySet[dict]: Each item contains:
                - uuid: article UUID
                - title: article title in current language

        Notes:
            - Assumes one translation per article per language.
            - Uses Django ORM values() query.
        """
        return Article.objects.filter(
            type=ArticleType.PAGE,
            status=ArticleStatus.PUBLISHED,
            translations__language=get_language(),
        ).values('uuid').annotate(title=F('translations__title'))
