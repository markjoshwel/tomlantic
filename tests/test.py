from pathlib import Path
from subprocess import CompletedProcess, run
from sys import stderr
from textwrap import indent


def main():
    failed_tests: dict[str, str] = {}
    total_tests = 0

    for test_path in Path(__file__).parent.glob("test-*.py"):
        cp: CompletedProcess[bytes] = run(
            f"uv run {test_path}", shell=True, capture_output=True
        )
        total_tests += 1

        if cp.returncode == 0:
            continue
        failed_tests[test_path.name] = cp.stderr.decode("utf-8")

    if len(failed_tests) == 0:
        print(
            f"tomlantic tests: passed all tests ({len(failed_tests)}/{total_tests} failed)",
            file=stderr,
        )
        exit(0)
    else:
        print(
            f"tomlantic tests: failed {len(failed_tests)}/{total_tests} ({len(failed_tests) / total_tests * 100:.2f}%) tests"
        )
        for test_name, error_message in failed_tests.items():
            print(f"- {test_name}", file=stderr)
            print(
                indent(error_message, prefix="  ... ", predicate=lambda _: True),
                file=stderr,
            )
        exit(len(failed_tests))


if __name__ == "__main__":
    main()
