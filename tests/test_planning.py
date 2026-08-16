"""Tests for the Planning Agent without live API requests."""

import unittest
from types import SimpleNamespace

from agents.planning import planning_agent
from models import PlannedBeat, VideoPlan


def make_plan(beat_numbers: list[int] | None = None) -> VideoPlan:
    numbers = beat_numbers or [1, 2, 3, 4, 5, 6, 7, 8]
    return VideoPlan(
        title="Why F1 Killed the V10",
        hook="V10s sounded incredible, so why did F1 get rid of them?",
        angle="Trace the forces behind F1's move away from V10 engines.",
        beats=[
            PlannedBeat(beat=number, purpose=f"Purpose {number}")
            for number in numbers
        ],
    )


class FakeResponses:
    def __init__(self, parsed_plan: VideoPlan | None) -> None:
        self.parsed_plan = parsed_plan
        self.call_arguments: dict[str, object] | None = None

    def parse(self, **kwargs: object) -> SimpleNamespace:
        self.call_arguments = kwargs
        return SimpleNamespace(output_parsed=self.parsed_plan)


class FakeClient:
    def __init__(self, parsed_plan: VideoPlan | None) -> None:
        self.responses = FakeResponses(parsed_plan)


class PlanningAgentTests(unittest.TestCase):
    def test_returns_structured_plan(self) -> None:
        expected_plan = make_plan()
        client = FakeClient(expected_plan)

        result = planning_agent("  Why did F1 stop using V10 engines?  ", client=client)

        self.assertEqual(result, expected_plan)
        self.assertEqual(client.responses.call_arguments["text_format"], VideoPlan)
        messages = client.responses.call_arguments["input"]
        self.assertIn("Why did F1 stop using V10 engines?", messages[1]["content"])

    def test_rejects_empty_topic_without_calling_api(self) -> None:
        client = FakeClient(make_plan())

        with self.assertRaisesRegex(ValueError, "cannot be empty"):
            planning_agent("   ", client=client)

        self.assertIsNone(client.responses.call_arguments)

    def test_rejects_missing_parsed_output(self) -> None:
        with self.assertRaisesRegex(ValueError, "did not return"):
            planning_agent("A valid topic", client=FakeClient(None))

    def test_rejects_fewer_than_six_beats(self) -> None:
        invalid_plan = make_plan([1, 2, 3, 4, 5])

        with self.assertRaisesRegex(ValueError, "between 6 and 10 beats"):
            planning_agent("A valid topic", client=FakeClient(invalid_plan))

    def test_rejects_more_than_ten_beats(self) -> None:
        invalid_plan = make_plan(list(range(1, 12)))

        with self.assertRaisesRegex(ValueError, "between 6 and 10 beats"):
            planning_agent("A valid topic", client=FakeClient(invalid_plan))

    def test_accepts_six_and_ten_beats(self) -> None:
        for count in (6, 10):
            expected_plan = make_plan(list(range(1, count + 1)))

            result = planning_agent(
                "A valid topic",
                client=FakeClient(expected_plan),
            )

            self.assertEqual(result, expected_plan)

    def test_rejects_non_sequential_beat_numbers(self) -> None:
        invalid_plan = make_plan([1, 2, 3, 4, 6, 7])

        with self.assertRaisesRegex(ValueError, "invalid beat numbering"):
            planning_agent("A valid topic", client=FakeClient(invalid_plan))


if __name__ == "__main__":
    unittest.main()
