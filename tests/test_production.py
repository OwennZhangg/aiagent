"""Tests for script generation and the human approval gate."""

import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

from agents.production import (
    load_script_edits,
    production_agent,
    save_script_for_review,
    wait_for_script_approval,
)
from models import PlannedBeat, ProductionBeat, ProductionPlan, VideoPlan


def make_video_plan() -> VideoPlan:
    return VideoPlan(
        title="Why F1 Killed the V10",
        hook="V10s sounded incredible, so why did F1 get rid of them?",
        angle="Explain why efficiency and manufacturer relevance won.",
        beats=[
            PlannedBeat(beat=number, purpose=f"Purpose {number}")
            for number in range(1, 7)
        ],
    )


def make_production_plan() -> ProductionPlan:
    return ProductionPlan(
        title="Why F1 Killed the V10",
        beats=[
            ProductionBeat(
                beat=number,
                purpose=f"Purpose {number}",
                script=f"Script line {number}.",
                visual_needed=number % 2 == 0,
                visual_type="photo overlay" if number % 2 == 0 else None,
                picture_description=(
                    f"Concrete supporting image {number}" if number % 2 == 0 else None
                ),
                search_query=f"specific image query {number}" if number % 2 == 0 else None,
            )
            for number in range(1, 7)
        ],
    )


class FakeResponses:
    def __init__(self, parsed_plan: ProductionPlan | None) -> None:
        self.parsed_plan = parsed_plan
        self.call_arguments: dict[str, object] | None = None

    def parse(self, **kwargs: object) -> SimpleNamespace:
        self.call_arguments = kwargs
        return SimpleNamespace(output_parsed=self.parsed_plan)


class FakeClient:
    def __init__(self, parsed_plan: ProductionPlan | None) -> None:
        self.responses = FakeResponses(parsed_plan)


class ProductionAgentTests(unittest.TestCase):
    def test_returns_structured_production_plan(self) -> None:
        video_plan = make_video_plan()
        expected = make_production_plan()
        client = FakeClient(expected)

        result = production_agent(video_plan, client=client)

        self.assertEqual(result, expected)
        self.assertEqual(
            client.responses.call_arguments["text_format"],
            ProductionPlan,
        )
        messages = client.responses.call_arguments["input"]
        self.assertIn('"beats"', messages[1]["content"])

    def test_rejects_missing_or_reordered_beats(self) -> None:
        production = make_production_plan()
        production.beats = production.beats[:-1]

        with self.assertRaisesRegex(ValueError, "every planned beat in order"):
            production_agent(
                make_video_plan(),
                client=FakeClient(production),
            )

    def test_rejects_incomplete_visual_details(self) -> None:
        production = make_production_plan()
        production.beats[1].search_query = None

        with self.assertRaisesRegex(ValueError, "complete supporting-visual"):
            production_agent(
                make_video_plan(),
                client=FakeClient(production),
            )

    def test_script_markdown_round_trip_loads_human_edits(self) -> None:
        production = make_production_plan()

        with tempfile.TemporaryDirectory() as temporary_directory:
            script_path = Path(temporary_directory) / "script.md"
            save_script_for_review(production, script_path)
            markdown = script_path.read_text(encoding="utf-8")
            markdown = markdown.replace(
                "Script line 2.",
                "This is the creator's edited second line.",
            )
            script_path.write_text(markdown, encoding="utf-8")

            approved = load_script_edits(production, script_path)

        self.assertEqual(
            approved.beats[1].script,
            "This is the creator's edited second line.",
        )
        self.assertEqual(production.beats[1].script, "Script line 2.")

    def test_approval_waits_for_input_then_loads_saved_edits(self) -> None:
        production = make_production_plan()
        input_was_requested = False

        with tempfile.TemporaryDirectory() as temporary_directory:
            script_path = Path(temporary_directory) / "script.md"
            save_script_for_review(production, script_path)

            def approve_after_edit(prompt: str) -> str:
                nonlocal input_was_requested
                input_was_requested = True
                self.assertIn("press Enter", prompt)
                markdown = script_path.read_text(encoding="utf-8")
                script_path.write_text(
                    markdown.replace("Script line 1.", "Approved opening line."),
                    encoding="utf-8",
                )
                return ""

            approved = wait_for_script_approval(
                production,
                script_path,
                input_fn=approve_after_edit,
            )

        self.assertTrue(input_was_requested)
        self.assertEqual(approved.beats[0].script, "Approved opening line.")

    def test_rejects_deleted_script_markers(self) -> None:
        production = make_production_plan()

        with tempfile.TemporaryDirectory() as temporary_directory:
            script_path = Path(temporary_directory) / "script.md"
            save_script_for_review(production, script_path)
            markdown = script_path.read_text(encoding="utf-8")
            script_path.write_text(
                markdown.replace("<!-- beat-1-script-start -->", ""),
                encoding="utf-8",
            )

            with self.assertRaisesRegex(ValueError, "Keep its script markers"):
                load_script_edits(production, script_path)


if __name__ == "__main__":
    unittest.main()
