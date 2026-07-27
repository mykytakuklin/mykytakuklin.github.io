import json
import os
import shutil
import xml.etree.ElementTree as ET
from datetime import datetime, timezone

REPORTS_DIR = "reports"
HISTORY_PATH = os.path.join(REPORTS_DIR, "history.json")
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

    os.makedirs(REPORTS_DIR, exist_ok=True)
    report_filename = f"{run_id}.html"
    shutil.copy("report.html", os.path.join(REPORTS_DIR, report_filename))
    shutil.copy("report.html", os.path.join(REPORTS_DIR, "latest.html"))

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
        "report": f"reports/{report_filename}",
    })

    while len(history) > MAX_HISTORY:
        dropped = history.pop()
        if os.path.exists(dropped["report"]):
            os.remove(dropped["report"])

    with open(HISTORY_PATH, "w") as f:
        json.dump(history, f, indent=2)


if __name__ == "__main__":
    main()
