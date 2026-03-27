"""
Risk service interfaces.
"""

from abc import ABC, abstractmethod
from typing import Any
from uuid import UUID

from myproj.core.contracts import (
    ActionEnvelope,
    RiskLevel,
    RiskPosture,
)
from myproj.core.risk.types import RiskEvaluation


class RiskSynthesizer(ABC):
    """Risk synthesizer interface."""

    @abstractmethod
    def evaluate_action(
        self,
        envelope: ActionEnvelope,
    ) -> RiskEvaluation:
        """
        Evaluate the risk of an action.

        Args:
            envelope: The action envelope to evaluate

        Returns:
            RiskEvaluation with overall risk and contributing reasons
        """
        pass

    @abstractmethod
    def evaluate_content_risk(
        self,
        content: str,
        content_type: str = "text/plain",
    ) -> RiskEvaluation:
        """
        Evaluate risk from content alone.

        Args:
            content: The content to evaluate
            content_type: MIME type of the content

        Returns:
            RiskEvaluation for the content
        """
        pass

    @abstractmethod
    def evaluate_relationship_risk(
        self,
        relationship_classes: list[str],
        is_sensitive: bool = False,
    ) -> RiskEvaluation:
        """
        Evaluate risk from relationship context.

        Args:
            relationship_classes: List of relationship classes
            is_sensitive: Whether the relationship is sensitive

        Returns:
            RiskEvaluation for the relationship
        """
        pass

    @abstractmethod
    def evaluate_action_type_risk(
        self,
        action_type: str,
        channel: str | None = None,
        is_external: bool = False,
    ) -> RiskEvaluation:
        """
        Evaluate risk from action type and channel.

        Args:
            action_type: Type of action being performed
            channel: Optional communication channel
            is_external: Whether this is external communication

        Returns:
            RiskEvaluation for the action type
        """
        pass

    @abstractmethod
    def synthesize_risk_posture(
        self,
        evaluation: RiskEvaluation,
    ) -> RiskPosture:
        """
        Synthesize a RiskPosture from a RiskEvaluation.

        Args:
            evaluation: The complete risk evaluation

        Returns:
            RiskPosture suitable for use in contracts
        """
        pass
