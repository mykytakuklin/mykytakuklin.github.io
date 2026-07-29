import json
import os
import shutil
import xml.etree.ElementTree as ET
from datetime import datetime, timezone

REPORTS_DIR = "reports"
HISTORY_PATH = os.path.join(REPORTS_DIR, "history.json")
STREAK_PATH = os.path.join(REPORTS_DIR, "streak.json")
MAX_HISTORY = 5


def parse_results():
    tree = ET.parse("results.xml")
    root = tree.getroot()
    suite = root if root.tag == "testsuite" else root.find("testsuite")
    total = int(suite.get("tests", 0))
    failed = int(suite.get("failures", 0)) + int(suite.get("errors", 0))
    duration = round(float(suite.get("time", 0)))
    return total - failed, failed, duration


def main():
    passed, failed, duration = parse_results()
    now = datetime.now(timezone.utc)
    run_id = now.strftime("%Y-%m-%dT%H-%M-%S")
    date_str = now.strftime("%Y-%m-%d")
    timestamp = now.strftime("%Y-%m-%d %H:%M UTC")

    run_dir = os.path.join(REPORTS_DIR, run_id)
    os.makedirs(run_dir, exist_ok=True)
    shutil.copy("report.html", os.path.join(run_dir, "report.html"))
    if os.path.isdir("assets"):
        shutil.copytree("assets", os.path.join(run_dir, "assets"))

    history = []
    if os.path.exists(HISTORY_PATH):
        with open(HISTORY_PATH) as f:
            history = json.load(f)

    history.insert(0, {
        "date": date_str,
        "timestamp": timestamp,
        "passed": passed,
        "failed": failed,
        "duration": duration,
        "report": f"reports/{run_id}/report.html",
    })

    while len(history) > MAX_HISTORY:
        dropped = history.pop()
        dropped_path = dropped["report"]
        dropped_dir = os.path.dirname(dropped_path)
        if dropped_dir and dropped_dir != REPORTS_DIR and os.path.isdir(dropped_dir):
            shutil.rmtree(dropped_dir)
        elif os.path.isfile(dropped_path):
            os.remove(dropped_path)

    with open(HISTORY_PATH, "w") as f:
        json.dump(history, f, indent=2)

    update_streak(date_str, failed)


def update_streak(date_str, failed):
    streak = {"days": 0, "lastCountedDate": None}
    if os.path.exists(STREAK_PATH):
        with open(STREAK_PATH) as f:
            streak = json.load(f)

    if failed > 0:
        streak["days"] = 0
    elif streak["lastCountedDate"] != date_str:
        streak["days"] += 1
        streak["lastCountedDate"] = date_str

    with open(STREAK_PATH, "w") as f:
        json.dump(streak, f, indent=2)


if __name__ == "__main__":
    main()
