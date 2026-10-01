from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable
import cv2
import numpy as np


@dataclass(frozen=True)
class ReviewFinding:
    code: str
    severity: str
    message: str
    frame: int | None = None


@dataclass
class ReviewReport:
    findings: list[ReviewFinding] = field(default_factory=list)

    @property
    def blocking(self) -> list[ReviewFinding]:
        return [f for f in self.findings if f.severity == "block"]

    @property
    def passed(self) -> bool:
        return not self.blocking


class SelfReview:
    """Deterministic first-pass QA for rendered previews.

    This is intentionally separate from any visual-AI reviewer. These checks
    catch objective failures cheaply before a more expensive style/continuity
    pass is considered.
    """

    def __init__(
        self,
        min_luma: float = 8.0,
        max_luma: float = 247.0,
        frozen_run: int = 18,
        edge_margin_px: int = 4,
    ):
        self.min_luma = min_luma
        self.max_luma = max_luma
        self.frozen_run = frozen_run
        self.edge_margin_px = edge_margin_px

    def review_frames(self, frames: Iterable[np.ndarray]) -> ReviewReport:
        report = ReviewReport()
        previous = None
        frozen = 0

        for index, frame in enumerate(frames):
            if frame is None or frame.size == 0:
                report.findings.append(
                    ReviewFinding("missing_frame", "block", "Rendered frame is missing.", index)
                )
                continue

            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            mean_luma = float(gray.mean())
            if mean_luma <= self.min_luma:
                report.findings.append(
                    ReviewFinding("near_black", "block", "Frame is unexpectedly near-black.", index)
                )
            elif mean_luma >= self.max_luma:
                report.findings.append(
                    ReviewFinding("near_white", "block", "Frame is unexpectedly blown out.", index)
                )

            if previous is not None:
                delta = cv2.absdiff(frame, previous)
                if float(delta.mean()) < 0.05:
                    frozen += 1
                    if frozen == self.frozen_run:
                        report.findings.append(
                            ReviewFinding(
                                "frozen_video",
                                "block",
                                f"Video appears frozen for at least {self.frozen_run} frames.",
                                index,
                            )
                        )
                else:
                    frozen = 0

            previous = frame

        return report

    def review_video(self, path: str | Path, sample_every: int = 1) -> ReviewReport:
        cap = cv2.VideoCapture(str(path))
        if not cap.isOpened():
            return ReviewReport([
                ReviewFinding("video_open_failed", "block", f"Could not open preview: {path}")
            ])

        frames = []
        i = 0
        while True:
            ok, frame = cap.read()
            if not ok:
                break
            if i % max(sample_every, 1) == 0:
                frames.append(frame)
            i += 1
        cap.release()

        if not frames:
            return ReviewReport([
                ReviewFinding("no_frames", "block", "Preview contains no readable frames.")
            ])
        return self.review_frames(frames)
