from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from studio.core.project import EpisodeProject
from studio.core.render_policy import RenderPolicy, RenderPolicyError, RenderRequest
from studio.core.storage import ProjectStore


class ProjectStoreTests(unittest.TestCase):
    def test_project_round_trip_and_approval(self):
        with tempfile.TemporaryDirectory() as td:
            store = ProjectStore(td)
            project_id, project = store.create("Episode One")
            self.assertEqual(project_id, "episode-one")
            self.assertEqual(project.status, "draft")
            project.director_notes = "Close-up on the punchline."
            store.save(project_id, project)
            loaded = store.load(project_id)
            self.assertEqual(loaded.director_notes, "Close-up on the punchline.")
            loaded.approve_final_master()
            self.assertTrue(loaded.final_master_approved)

    def test_media_path_cannot_escape_project(self):
        with tempfile.TemporaryDirectory() as td:
            store = ProjectStore(td)
            project_id, _ = store.create("Safe")
            with self.assertRaises(ValueError):
                store.media_path(project_id, "../../escape.txt")


class RenderPolicyTests(unittest.TestCase):
    def test_4k_requires_approval(self):
        with tempfile.TemporaryDirectory() as td:
            config = Path(td) / "profiles.json"
            config.write_text(json.dumps({
                "preview": {"width": 1280, "height": 720, "fps": 30},
                "master": {"width": 3840, "height": 2160, "fps": 60, "requires_approval": True},
            }))
            policy = RenderPolicy(config)
            self.assertEqual(policy.resolve(RenderRequest("preview"))["width"], 1280)
            with self.assertRaises(RenderPolicyError):
                policy.resolve(RenderRequest("master", False))
            self.assertEqual(policy.resolve(RenderRequest("master", True))["width"], 3840)


if __name__ == "__main__":
    unittest.main()
