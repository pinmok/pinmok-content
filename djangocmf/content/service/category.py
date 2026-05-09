#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
category module

Description:
  Category service for the content app.

  Provides CategoryNode and CategoryService for building and flattening
  category trees with indented labels.
Author:
  惠达浪 <crazys@126.com>
Created:
  2026/3/22
"""
from dataclasses import dataclass

from djangocmf.content.models import Category
from djangocmf.core.constants import DEFAULT_SORT_ORDER
from djangocmf.core.libs.tree import TreeNode


@dataclass(kw_only=True)
class CategoryNode(TreeNode["CategoryNode"]):
    """Tree node representation of a Category."""
    sort_order: int = DEFAULT_SORT_ORDER
    name: str = ""
    uuid: str = ""
    cover: str = ""
    description: str = ""


class CategoryService:
    """
   Service for category data retrieval and tree construction.

   Handles database access, node assembly, and tree flattening for
   Category models. All tree operations delegate to CategoryNode,
   which extends TreeNode.
   """

    @classmethod
    def _load_nodes(cls) -> list[CategoryNode]:
        """
        Fetch all categories with translations prefetched.
        Language fallback is handled by TranslatableModel.get_translation().
        """
        categories = Category.with_translations()

        return [
            CategoryNode(
                id=cat.id,
                parent_id=cat.parent_id,
                uuid=str(cat.uuid),
                sort_order=cat.sort_order,
                name=cat.translation.name if cat.translation else '',
                cover=cat.cover.url if cat.cover else '',
                description=cat.translation.description if cat.translation else '',
            )
            for cat in categories
        ]

    @classmethod
    def get_items(cls, exclude_id: int | str | None = None) -> list[tuple[CategoryNode, str]]:
        """
        Return categories flattened in DFS pre-order with indented labels.

        Returns:
            List of ``(CategoryNode, indented_label)`` pairs.
        """
        return CategoryNode.flatten_with_indent(
            cls._load_nodes(),
            label_func=lambda n: n.name,
            exclude_id=exclude_id,
            sort_key='sort_order',
        )

    @classmethod
    def build_tree(cls) -> list[CategoryNode]:
        """
        Return categories as a tree structure.

        Returns:
            Root nodes of the constructed tree.
        """
        return CategoryNode.build_tree(cls._load_nodes(), sort_key='sort_order')
