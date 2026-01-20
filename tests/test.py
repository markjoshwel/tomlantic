from os import getenv
from pathlib import Path
from shutil import which
from subprocess import CompletedProcess, run
from sys import argv, executable, stderr
from textwrap import indent

TEST_PATHS: list[Path] = [
    Path(__file__).parent.parent.joinpath("showcase.py"),
    *Path(__file__).parent.glob("test-*.py"),
]


def resolve_binaries() -> dict[str, list[str]]:
    versions_and_binaries: dict[str, list[str]] = {
        "39": [],
        "310": [],
        "311": [],
        "312": [],
        "313": [],
        "314": [],
    }

    # test for uv, and/or signs of being run from the nix flake, or being in a nix environment
    if not any(
        [
            getenv("name", default="").startswith("nix"),
            getenv("NIX_STORE", default=None) is not None,
            getenv("IN_NIX_SHELL", default=None) is not None,
            str(which("python")).startswith(
                getenv("NIX_STORE", default="zsxgdfchgvjhbj")
            ),
        ]
    ):
        # not in nix, detect uv or die
        if not (bin_uv := which("uv")):
            print(
                "tomlantic tests: note: using whichever python is executing this",
                file=stderr,
            )
            versions_and_binaries["local"] = [executable]
            return versions_and_binaries

        print("tomlantic tests: note: using uv for python management", file=stderr)
        versions_and_binaries["39"] = [bin_uv, "run", "--python", "python3.9"]
        versions_and_binaries["310"] = [bin_uv, "run", "--python", "python3.10"]
        versions_and_binaries["311"] = [bin_uv, "run", "--python", "python3.11"]
        versions_and_binaries["312"] = [bin_uv, "run", "--python", "python3.12"]
        versions_and_binaries["313"] = [bin_uv, "run", "--python", "python3.13"]
        # versions_and_binaries["314"] = [bin_uv, "run", "--python", "python3.14"]
        return versions_and_binaries

    print(
        "tomlantic tests: note: nix detected, if you would like to test across multiple versions, run `nix run .#tests`",
        file=stderr,
    )

    if len(argv) > 1:
        print(
            "tomlantic tests: note: using argument-provided python binaries",
            file=stderr,
        )
        # the argv is passed in from the nix flake like a key value pair
        # (a la `.../python tests/test.py -- 3.9=/nix/store/... 3.10=/nix/store/... ...`)
        for arg in argv[1:]:
            version, binary_path = arg.split("=")
            if version in versions_and_binaries:
                versions_and_binaries[version].append(binary_path)
    else:
        print(
            "tomlantic tests: note: using whichever python is executing this",
            file=stderr,
        )
        versions_and_binaries["local"] = [executable]

    for version, binary in versions_and_binaries.items():
        print(
            f" ... {version} -> {'`' + ' '.join(binary) + ' ... `' if binary else '(unresolved)'}",
            file=stderr,
        )

    return versions_and_binaries


def main() -> None:
    versions_and_binaries = resolve_binaries()
    failed_tests: dict[str, str] = {}
    total_tests = 0

    for version, binary in versions_and_binaries.items():
        if len(binary) == 0:  # unresolved or not given
            continue

        for test_path in TEST_PATHS:
            print(
                f"tomlantic tests: running {test_path.name}@py{version}...", file=stderr
            )
            cp: CompletedProcess[bytes] = run(
                [*binary, test_path],
                capture_output=True,
            )
            total_tests += 1

            if cp.returncode == 0:
                continue

            failed_tests[f"{test_path.name}@py{version}"] = cp.stderr.decode("utf-8")

    if len(failed_tests) == 0:
        print(
            f"tomlantic tests: passed all tests ({len(failed_tests)}/{total_tests} failed)",
            file=stderr,
        )
        exit(0)

    else:
        for test_name, error_message in failed_tests.items():
            print(f"- {test_name}", file=stderr)
            print(
                indent(error_message, prefix="  ... ", predicate=lambda _: True),
                file=stderr,
            )
        failure_percentage = len(failed_tests) / total_tests * 100
        print(
            f"tomlantic tests: failed {len(failed_tests)}/{total_tests} ({failure_percentage:.2f}%) tests"
        )
        exit(int(failure_percentage))


if __name__ == "__main__":
    main()
