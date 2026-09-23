"""Run the shipped offline regression suites without third-party packages."""
from pathlib import Path
import os
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
SKILLS = ("prompt-remix-kit", "source-action-brief")


def main():
    if sys.version_info < (3, 10):
        print("Python 3.10+ is required.", file=sys.stderr)
        return 2
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1", PYTHONUTF8="1")
    for name in SKILLS:
        skill = ROOT / "skills" / name
        for required in ("SKILL.md", "agents/openai.yaml"):
            if not (skill / required).is_file():
                print(f"Missing: skills/{name}/{required}", file=sys.stderr)
                return 1
        tests = sorted((skill / "tests").glob("test*.py"))
        if not tests:
            print(f"Missing regression tests: {name}", file=sys.stderr)
            return 1
        print(f"Checking {name}", flush=True)
        result = subprocess.run(
            [sys.executable, "-B", "-m", "unittest", "discover", "-s", str(skill / "tests"), "-v"],
            cwd=ROOT, env=env, check=False,
        )
        if result.returncode:
            return result.returncode
    print("All offline suites passed. Semantic quality still needs human review.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
