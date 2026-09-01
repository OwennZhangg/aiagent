"""Tests for the Composer Agent without live API calls."""

import unittest
from pathlib import Path
from types import SimpleNamespace
import tempfile

from agents.composer import (
    composer_agent,
    render_production_guide,
    save_production_guide,
)

from models import (
    FinalBeat,
    FinalGuide,
    ProductionBeat,
    ProductionPlan,
)


def make_production_plan() -> ProductionPlan:
    return ProductionPlan(
        title="Why F1 Killed the V10",
        beats=[
            ProductionBeat(
                beat=1,
                purpose="Create immediate curiosity",
                script="F1 V10s sounded incredible.",
                visual_needed=False,
                visual_type=None,
                picture_description=None,
                search_query=None,
            ),
            ProductionBeat(
                beat=2,
                purpose="Show the engine",
                script="These engines could rev past 19,000 RPM.",
                visual_needed=True,
                visual_type="photo overlay",
                picture_description="Close-up of an F1 V10 engine",
                search_query="Formula 1 V10 engine close up",
            ),
        ],
    )


def make_final_guide() -> FinalGuide:
    return FinalGuide(
        title="Why F1 Killed the V10",
        beats=[
            FinalBeat(
                beat=1,
                script="F1 V10s sounded incredible.",
                picture=None,
                on_screen_text="Why kill the V10?",
                editing_note="Start immediately on the creator.",
                estimated_duration=2,
            ),
            FinalBeat(
                beat=2,
                script="These engines could rev past 19,000 RPM.",
                picture="output/test/beats/beat2/selected.jpg",
                on_screen_text="19,000 RPM",
                editing_note="Place the engine image above the creator.",
                estimated_duration=3,
            ),
        ],
    )

class FakeResponses:
    def __init__(
        self,
        parsed_guide: FinalGuide | None,
    ) -> None:
        self.parsed_guide = parsed_guide
        self.call_arguments: dict[str, object] | None = None

    def parse(
        self,
        **kwargs: object,
    ) -> SimpleNamespace:
        self.call_arguments = kwargs

        return SimpleNamespace(
            output_parsed=self.parsed_guide
        )


class FakeClient:
    def __init__(
        self,
        parsed_guide: FinalGuide | None,
    ) -> None:
        self.responses = FakeResponses(
            parsed_guide
        )

class ComposerAgentTests(unittest.TestCase):
    def test_returns_structured_final_guide(self) -> None:
        production_plan = make_production_plan()
        expected_guide = make_final_guide()

        selected_images = {
            1: None,
            2: Path(
                "output/test/beats/beat2/selected.jpg"
            ),
        }

        client = FakeClient(expected_guide)

        result = composer_agent(
            production_plan,
            selected_images,
            client=client,
        )

        self.assertEqual(
            result,
            expected_guide,
        )

        self.assertEqual(
            client.responses.call_arguments["text_format"],
            FinalGuide,
        )

        messages = client.responses.call_arguments["input"]

        self.assertIn(
            "Approved production plan",
            messages[1]["content"],
        )

        self.assertIn(
            "output/test/beats/beat2/selected.jpg",
            messages[1]["content"],
        )

    def test_rejects_changed_approved_script(self) -> None:
        production_plan = make_production_plan()
        invalid_guide = make_final_guide()

        invalid_guide.beats[0].script = (
            "The Composer rewrote this approved line."
        )

        selected_images = {
            1: None,
            2: Path(
                "output/test/beats/beat2/selected.jpg"
            ),
        }

        with self.assertRaisesRegex(
            ValueError,
            "changed the approved script",
        ):
            composer_agent(
                production_plan,
                selected_images,
                client=FakeClient(invalid_guide),
            )

    def test_rejects_invented_picture_path(self) -> None:
        production_plan = make_production_plan()
        invalid_guide = make_final_guide()

        invalid_guide.beats[1].picture = (
            "output/fake/invented-image.jpg"
        )

        selected_images = {
            1: None,
            2: Path(
                "output/test/beats/beat2/selected.jpg"
            ),
        }

        with self.assertRaisesRegex(
            ValueError,
            "wrong picture",
        ):
            composer_agent(
                production_plan,
                selected_images,
                client=FakeClient(invalid_guide),
            )
    def test_renders_production_guide_markdown(self) -> None:
        markdown = render_production_guide(
            make_final_guide()
        )

        self.assertIn(
            "# Why F1 Killed the V10",
            markdown,
        )

        self.assertIn(
            "## Beat 1",
            markdown,
        )

        self.assertIn(
            "F1 V10s sounded incredible.",
            markdown,
        )

        self.assertIn(
            "Creator only — no image.",
            markdown,
        )

        self.assertIn(
            "output/test/beats/beat2/selected.jpg",
            markdown,
        )

        self.assertIn(
            "19,000 RPM",
            markdown,
        )

        self.assertIn(
            "3 seconds",
            markdown,
        )
    def test_saves_production_guide(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            output_path = (
                Path(temporary_directory)
                / "production-guide.md"
            )

            result = save_production_guide(
                make_final_guide(),
                output_path,
            )

            self.assertEqual(
                result,
                output_path,
            )

            self.assertTrue(
                output_path.exists()
            )

            saved_markdown = output_path.read_text(
                encoding="utf-8"
            )

            self.assertIn(
                "# Why F1 Killed the V10",
                saved_markdown,
            )
    def test_rejects_missing_parsed_output(self) -> None:
        production_plan = make_production_plan()

        selected_images = {
            1: None,
            2: Path(
                "output/test/beats/beat2/selected.jpg"
            ),
        }

        with self.assertRaisesRegex(
            ValueError,
            "did not return",
        ):
            composer_agent(
                production_plan,
                selected_images,
                client=FakeClient(None),
            )

if __name__ == "__main__":
    unittest.main()