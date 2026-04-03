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
from django.conf import settings
from django.core.exceptions import PermissionDenied
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from djangocmf.content.enums import ArticleStatus


class ArticleService:
    # --- status transition rules ---
    TRANSITIONS = {
        ArticleStatus.DRAFT: [ArticleStatus.PENDING],
        ArticleStatus.PENDING: [ArticleStatus.PUBLISHED, ArticleStatus.RETURNED],
        ArticleStatus.PUBLISHED: [ArticleStatus.RETURNED],
        ArticleStatus.RETURNED: [ArticleStatus.PENDING],
        ArticleStatus.DELETED: [],
    }
    PUBLISH_REQUIRED = {ArticleStatus.PUBLISHED, ArticleStatus.RETURNED}

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
          name    — POST key, matched in _SUBMIT_ACTIONS
          label   — display text
          class   — CSS class for styling
        A None entry inserts a visual separator.
        Save button is always rendered separately in the template.
        """
        buttons = []

        if current_status == ArticleStatus.DRAFT:
            buttons.append({
                'name': '_submit_pending',
                'label': _('Submit for review'),
                'class': 'btn-warning',
            })

        elif current_status == ArticleStatus.PENDING:
            if has_publish_perm:
                buttons.append({
                    'name': '_submit_publish',
                    'label': _('Publish'),
                    'class': 'btn-success',
                })
                buttons.append({
                    'name': '_submit_reject',
                    'label': _('Return'),
                    'class': 'btn-danger',
                })

        elif current_status == ArticleStatus.PUBLISHED:
            if has_publish_perm:
                buttons.append({
                    'name': '_submit_reject',
                    'label': _('Retract'),
                    'class': 'btn-danger',
                })

        elif current_status == ArticleStatus.RETURNED:
            buttons.append({
                'name': '_submit_pending',
                'label': _('Submit for review'),
                'class': 'btn-warning',
            })

        # DELETED: no buttons

        return buttons

    # Save button visibility per status
    # PENDING and PUBLISHED: only publish-perm users can meaningfully save
    # DELETED: nobody should be editing
    SAVE_ALLOWED = {
        ArticleStatus.DRAFT,
        ArticleStatus.RETURNED,
    }
    SAVE_ALLOWED_WITH_PERM = {
        ArticleStatus.PENDING,
        ArticleStatus.PUBLISHED,
    }

    @classmethod
    def show_save_button(cls, current_status, has_publish_perm):
        """Return whether the plain Save button should be shown."""
        if current_status in cls.SAVE_ALLOWED:
            return True
        if current_status in cls.SAVE_ALLOWED_WITH_PERM and has_publish_perm:
            return True
        return False


def get_translated_name(obj, related_name='translations', language=None, fallback=None):
    """
    Get the translated name for a model instance.
    Works with or without prefetch_related.
    """
    language = language or settings.LANGUAGE_CODE
    fallback = fallback or f'{obj.__class__.__name__}({obj.pk})'
    translations = getattr(obj, related_name).all()
    translation = next((t for t in translations if t.language_code == language), None)
    if not translation:
        translation = next(iter(translations), None)
    return translation.name if translation else fallback
