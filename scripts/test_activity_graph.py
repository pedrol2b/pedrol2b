import datetime as dt
import tempfile
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path

import activity_graph


class ActivityGraphTests(unittest.TestCase):
    def test_zero_activity_renders_valid_svg_with_31_points(self):
        today = dt.date(2026, 10, 21)
        days = [{"date": (today - dt.timedelta(days=i)).isoformat(),
                 "contributionCount": 0} for i in range(31)]
        svg = activity_graph.render(days, today)
        root = ET.fromstring(svg)
        points = root.findall(".//{http://www.w3.org/2000/svg}circle")
        self.assertEqual(len(points), 31)
        self.assertNotIn("nan", svg.lower())
        self.assertNotIn("inf", svg.lower())
        self.assertIn("0 contributions", svg)

    def test_calendar_filters_window_and_orders_points(self):
        today = dt.date(2026, 10, 21)
        days = [{"date": (today - dt.timedelta(days=i)).isoformat(),
                 "contributionCount": i} for i in range(35)]
        root = ET.fromstring(activity_graph.render(days, today))
        titles = root.findall(".//{http://www.w3.org/2000/svg}circle/{http://www.w3.org/2000/svg}title")
        self.assertEqual(len(titles), 31)
        self.assertEqual(titles[0].text, "2026-09-21: 30 contributions")
        self.assertEqual(titles[-1].text, "2026-10-21: 0 contributions")

    def test_api_error_preserves_existing_graph(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "graph.svg"
            output.write_text("previous graph")
            for payload in ({"errors": [{"message": "rate limited"}]},
                            {"data": {"user": None}}):
                with self.subTest(payload=payload), self.assertRaises(ValueError):
                    activity_graph.generate(payload, output)
                self.assertEqual(output.read_text(), "previous graph")

    def test_incomplete_calendar_is_rejected(self):
        with self.assertRaises(ValueError):
            activity_graph.render([], dt.date(2026, 10, 21))


if __name__ == "__main__":
    unittest.main()
