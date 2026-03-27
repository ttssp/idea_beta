"""Repositories 单元测试 - 验证导入和基本结构"""

import pytest


class TestRepositoryImports:
    """测试 repositories 包的导入"""

    def test_can_import_base_repository(self):
        """可以导入 BaseRepository"""
        from myproj.core.repositories import BaseRepository

        assert BaseRepository is not None

    def test_can_import_thread_repository(self):
        """可以导入 ThreadRepository"""
        from myproj.core.repositories import ThreadRepository

        assert ThreadRepository is not None

    def test_can_import_message_repository(self):
        """可以导入 MessageRepository"""
        from myproj.core.repositories import MessageRepository

        assert MessageRepository is not None

    def test_can_import_principal_repository(self):
        """可以导入 PrincipalRepository"""
        from myproj.core.repositories import PrincipalRepository

        assert PrincipalRepository is not None

    def test_can_import_relationship_repository(self):
        """可以导入 RelationshipRepository"""
        from myproj.core.repositories import RelationshipRepository

        assert RelationshipRepository is not None

    def test_can_import_event_repository(self):
        """可以导入 EventRepository"""
        from myproj.core.repositories import EventRepository

        assert EventRepository is not None

    def test_all_repositories_are_exported(self):
        """所有 repositories 都在 __all__ 中导出"""
        from myproj.core.repositories import __all__

        expected_exports = {
            "BaseRepository",
            "EventRepository",
            "MessageRepository",
            "PrincipalRepository",
            "RelationshipRepository",
            "ThreadRepository",
        }

        assert set(__all__) == expected_exports


class TestRepositoryStructure:
    """测试 Repository 的结构"""

    def test_thread_repository_inherits_base(self):
        """ThreadRepository 继承自 BaseRepository"""
        from myproj.core.repositories import BaseRepository
        from myproj.core.repositories import ThreadRepository

        assert issubclass(ThreadRepository, BaseRepository)

    def test_message_repository_inherits_base(self):
        """MessageRepository 继承自 BaseRepository"""
        from myproj.core.repositories import BaseRepository
        from myproj.core.repositories import MessageRepository

        assert issubclass(MessageRepository, BaseRepository)

    def test_principal_repository_inherits_base(self):
        """PrincipalRepository 继承自 BaseRepository"""
        from myproj.core.repositories import BaseRepository
        from myproj.core.repositories import PrincipalRepository

        assert issubclass(PrincipalRepository, BaseRepository)

    def test_relationship_repository_inherits_base(self):
        """RelationshipRepository 继承自 BaseRepository"""
        from myproj.core.repositories import BaseRepository
        from myproj.core.repositories import RelationshipRepository

        assert issubclass(RelationshipRepository, BaseRepository)

    def test_event_repository_inherits_base(self):
        """EventRepository 继承自 BaseRepository"""
        from myproj.core.repositories import BaseRepository
        from myproj.core.repositories import EventRepository

        assert issubclass(EventRepository, BaseRepository)

    def test_repositories_have_required_methods(self):
        """Repository 有必需的方法"""
        from myproj.core.repositories import (
            EventRepository,
            MessageRepository,
            PrincipalRepository,
            RelationshipRepository,
            ThreadRepository,
        )

        repositories = [
            ThreadRepository,
            MessageRepository,
            PrincipalRepository,
            RelationshipRepository,
            EventRepository,
        ]

        for repo_class in repositories:
            assert hasattr(repo_class, "_model_class")
            assert hasattr(repo_class, "_to_id_value")
            assert hasattr(repo_class, "_get_entity_id")
            assert hasattr(repo_class, "_to_entity")
            assert hasattr(repo_class, "_to_model")
