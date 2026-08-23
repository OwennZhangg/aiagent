"""Tests for the Image Agent without real searches or API calls."""

import unittest
from pathlib import Path

from agents.image import image_agent
from models import ProductionBeat, ProductionPlan


class ImageAgentTests(unittest.TestCase):
    def test_creator_only_beat_skips_all_image_work(self) -> None:
        production_plan = ProductionPlan(
            title="Test Video",
            beats=[
                ProductionBeat(
                    beat=1,
                    purpose="Deliver the hook",
                    script="Here is the hook.",
                    visual_needed=False,
                    visual_type=None,
                    picture_description=None,
                    search_query=None,
                )
            ],
        )

        def fail_if_called(*args, **kwargs):
            self.fail(
                "An image function was called for a creator-only beat."
            )

        result = image_agent(
            production_plan,
            Path("unused"),
            search_fn=fail_if_called,
            download_fn=fail_if_called,
            select_fn=fail_if_called,
            save_fn=fail_if_called,
        )

        self.assertEqual(
            result,
            {1: None},
        )

    def test_visual_beat_runs_complete_image_workflow(self) -> None:
        production_plan = ProductionPlan(
            title="Test Video",
            beats=[
                ProductionBeat(
                    beat=1,
                    purpose="Show a concrete example",
                    script="This is the Ferrari F2004.",
                    visual_needed=True,
                    visual_type="photo overlay",
                    picture_description="Ferrari F2004 racing on track",
                    search_query="Ferrari F2004 racing 2004",
                )
            ],
        )

        calls: list[str] = []

        def fake_search(
            queries: list[str],
        ) -> list[list[str]]:
            calls.append(f"search:{queries[0]}")
            return [
                [
                    "https://example.com/one.jpg",
                    "https://example.com/two.jpg",
                ]
            ]

        def fake_download(
            image_urls: list[str],
            image_directory: Path,
        ) -> list[Path]:
            calls.append(f"download:{image_directory}")
            return [
                image_directory / "candidate1.jpg",
                image_directory / "candidate2.jpg",
            ]

        def fake_select(
            query: str,
            candidate_paths: list[Path],
        ) -> Path:
            calls.append(f"select:{query}")
            return candidate_paths[1]

        def fake_save(
            selected_candidate: Path,
            image_directory: Path,
        ) -> Path:
            calls.append(f"save:{selected_candidate.name}")
            return image_directory / "selected.jpg"

        result = image_agent(
            production_plan,
            Path("output/test-video"),
            search_fn=fake_search,
            download_fn=fake_download,
            select_fn=fake_select,
            save_fn=fake_save,
        )

        self.assertEqual(
            result,
            {
                1: Path(
                    "output/test-video/beats/beat1/selected.jpg"
                )
            },
        )

        self.assertEqual(
            calls,
            [
                "search:Ferrari F2004 racing 2004",
                "download:output/test-video/beats/beat1",
                "select:Ferrari F2004 racing 2004",
                "save:candidate2.jpg",
            ],
        )
    def test_failed_beat_does_not_stop_remaining_beats(self) -> None:
        production_plan = ProductionPlan(
            title="Test Video",
            beats=[
                ProductionBeat(
                    beat=1,
                    purpose="First example",
                    script="This image will fail.",
                    visual_needed=True,
                    visual_type="photo overlay",
                    picture_description="First example",
                    search_query="failing search",
                ),
                ProductionBeat(
                    beat=2,
                    purpose="Second example",
                    script="This image should still work.",
                    visual_needed=True,
                    visual_type="photo overlay",
                    picture_description="Second example",
                    search_query="working search",
                ),
            ],
        )

        searched_queries: list[str] = []

        def fake_search(
            queries: list[str],
        ) -> list[list[str]]:
            searched_queries.extend(queries)
            return [
                [],
                ["https://example.com/image.jpg"],
            ]

        def fake_download(
            image_urls: list[str],
            image_directory: Path,
        ) -> list[Path]:
            return [image_directory / "candidate1.jpg"]

        def fake_select(
            query: str,
            candidate_paths: list[Path],
        ) -> Path:
            return candidate_paths[0]

        def fake_save(
            selected_candidate: Path,
            image_directory: Path,
        ) -> Path:
            return image_directory / "selected.jpg"

        result = image_agent(
            production_plan,
            Path("output/test-video"),
            search_fn=fake_search,
            download_fn=fake_download,
            select_fn=fake_select,
            save_fn=fake_save,
        )

        self.assertEqual(result[1], None)

        self.assertEqual(
            result[2],
            Path(
                "output/test-video/beats/beat2/selected.jpg"
            ),
        )

        self.assertEqual(
            searched_queries,
            [
                "failing search",
                "working search",
            ],
        )
if __name__ == "__main__":
    unittest.main()
