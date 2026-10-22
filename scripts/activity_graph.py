"""Render the public GitHub contribution calendar as a standalone SVG."""

import datetime as dt
import json
import math
import sys
from pathlib import Path


def render(days, today):
    start = today - dt.timedelta(days=30)
    window = sorted(
        (day for day in days if start.isoformat() <= day["date"] <= today.isoformat()),
        key=lambda day: day["date"],
    )
    expected = [(start + dt.timedelta(days=i)).isoformat() for i in range(31)]
    if [day["date"] for day in window] != expected:
        raise ValueError("Expected a complete calendar for the last 31 UTC days")
    counts = [day["contributionCount"] for day in window]
    if any(type(count) is not int or count < 0 for count in counts):
        raise ValueError("Contribution counts must be nonnegative integers")
    ceiling = max(4, math.ceil(max(counts) / 4) * 4)
    points = [(60 + i * 30, 250 - count / ceiling * 160)
              for i, count in enumerate(counts)]
    parts = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="1000" height="320" '
        'viewBox="0 0 1000 320" role="img" aria-labelledby="title description">',
        '<title id="title">Pedro Bueno\'s GitHub Activity Graph</title>',
        f'<desc id="description">{sum(counts)} contributions from {start} to {today} (UTC).</desc>',
        '<rect width="1000" height="320" fill="#131313"/>',
        '<g fill="#f7f1ff" font-family="Verdana,Arial,sans-serif">',
        '<text x="500" y="36" text-anchor="middle" font-size="20">Pedro Bueno\'s GitHub Activity Graph</text>',
        f'<text x="500" y="60" text-anchor="middle" font-size="12">{sum(counts)} contributions in the last 31 days</text>',
    ]
    for i in range(5):
        y = 250 - i * 40
        parts.extend([
            f'<path d="M60 {y}H960" stroke="#f7f1ff" stroke-opacity="0.12"/>',
            f'<text x="48" y="{y + 4}" text-anchor="end" font-size="11">{ceiling * i // 4}</text>',
        ])
    coordinates = " ".join(f"{x:.1f},{y:.1f}" for x, y in points)
    parts.append(f'<polyline points="{coordinates}" fill="none" stroke="#fce566" stroke-width="2"/>')
    for day, (x, y) in zip(window, points):
        parts.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="3" fill="#fce566"><title>{day["date"]}: {day["contributionCount"]} contributions</title></circle>')
    for i in range(0, 31, 5):
        date = dt.date.fromisoformat(window[i]["date"])
        parts.append(f'<text x="{points[i][0]}" y="275" text-anchor="middle" font-size="11">{date:%b %d}</text>')
    parts.append(f'<text x="960" y="305" text-anchor="end" font-size="10">Updated {today} UTC</text></g></svg>')
    return "\n".join(parts) + "\n"


def generate(payload, output):
    if payload.get("errors"):
        raise ValueError("GitHub returned GraphQL errors; keeping the previous SVG")
    try:
        weeks = payload["data"]["user"]["contributionsCollection"]["contributionCalendar"]["weeks"]
        days = [day for week in weeks for day in week["contributionDays"]]
    except (KeyError, TypeError) as error:
        raise ValueError("GitHub returned an invalid contribution calendar") from error
    svg = render(days, dt.datetime.now(dt.timezone.utc).date())
    output.parent.mkdir(parents=True, exist_ok=True)
    temporary = output.with_suffix(".svg.tmp")
    temporary.write_text(svg, encoding="utf-8")
    temporary.replace(output)


if __name__ == "__main__":
    generate(json.loads(Path(sys.argv[1]).read_text()), Path(sys.argv[2]))
