from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .project import EpisodeProject
from .self_review import ReviewReport, SelfReview


@dataclass
class ReviewGateResult:
    report: ReviewReport
    ready_for_director: bool


class ReviewGate:
    """Mandatory preview QA gate before a project can be marked review-ready."""

    def __init__(self, reviewer: SelfReview | None = None):
        self.reviewer = reviewer or SelfReview()

    def inspect_preview(
        self,
        project: EpisodeProject,
        preview_path: str | Path,
        sample_every: int = 1,
    ) -> ReviewGateResult:
        report = self.reviewer.review_video(preview_path, sample_every=sample_every)
        if report.passed:
            project.mark_review()
            return ReviewGateResult(report=report, ready_for_director=True)

        project.mark_draft()
        return ReviewGateResult(report=report, ready_for_director=False)
