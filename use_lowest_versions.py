# script for workflows to use the lowest versions of targeted main dependencies
# usually to be run with 'poetry lock && poetry install && python test.py' afterwards

from os import system
from pathlib import Path
from sys import stderr

pyproj = Path(__file__).parent.joinpath("pyproject.toml").read_text("utf-8")
for line in pyproj.splitlines():
    if (">=" in line) and line.strip().endswith("# target"):
        replacing_line = line.replace(">=", "==")
        stderr.write(f"{line}\n")
        stderr.write(f"-> {replacing_line}\n")
        pyproj = pyproj.replace(line, replacing_line)

Path(__file__).parent.joinpath("pyproject.toml").write_text(pyproj, "utf-8")
