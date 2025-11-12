#!/usr/bin/env python3
"""
Lightweight regression checks for notebook datasets.

Run: python scripts/validate_notebooks.py
"""
from __future__ import annotations

import csv
import sys
from pathlib import Path
from typing import Iterable, List

REPO_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = REPO_ROOT / "notebooks" / "data"

DatasetSpec = dict


def ok(label: str, condition: bool, extra: str | None = None) -> bool:
    status = "[OK] " if condition else "[FAIL] "
    print(f"{status}{label}" + (f"  {extra}" if extra else ""))
    return condition


def load_csv(path: Path) -> tuple[List[str], List[dict]]:
    with path.open("r", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        rows = list(reader)
        return reader.fieldnames or [], rows


def require_sorted(values: Iterable[float]) -> bool:
    as_list = list(values)
    return all(a <= b for a, b in zip(as_list, as_list[1:]))


def validate_temperature_dataset(file_path: Path) -> bool:
    expected_columns = [
        "temperature",
        "avg_response_time",
        "response_time_std",
        "consistency_pct",
        "creativity_score",
        "sample_size",
    ]
    cols, rows = load_csv(file_path)
    success = True
    success &= ok(
        "temperature_experiment.csv present",
        file_path.exists(),
        str(file_path) if file_path.exists() else "file missing",
    )
    success &= ok(
        "columns match expected schema",
        cols == expected_columns,
        f"expected {expected_columns}, got {cols}",
    )
    success &= ok(
        "row count == 5 (temperatures 0.0–1.0)",
        len(rows) == 5,
        f"found {len(rows)} rows",
    )

    numeric_columns = [
        "temperature",
        "avg_response_time",
        "response_time_std",
        "consistency_pct",
        "creativity_score",
    ]
    int_columns = ["sample_size"]
    try:
        for row in rows:
            for col in numeric_columns:
                float(row[col])
            for col in int_columns:
                int(row[col])
    except (KeyError, ValueError) as exc:
        success &= ok("numeric columns parseable", False, str(exc))
    else:
        success &= ok("numeric columns parseable", True)

    temperatures = [float(r["temperature"]) for r in rows]
    success &= ok(
        "temperatures sorted ascending",
        require_sorted(temperatures),
        f"temperatures order: {temperatures}",
    )

    sample_sizes = {int(r["sample_size"]) for r in rows}
    success &= ok(
        "sample_size consistent per row",
        sample_sizes == {5},
        f"sample sizes found: {sorted(sample_sizes)}",
    )

    return success


def main() -> int:
    specs: dict[str, DatasetSpec] = {
        "temperature_experiment.csv": {
            "file": DATA_DIR / "temperature_experiment.csv",
            "validator": validate_temperature_dataset,
        }
    }

    overall_success = True
    print("== Notebook Data Validation ==")
    for name, spec in specs.items():
        print(f"\nValidating: {name}")
        validator = spec["validator"]
        overall_success &= validator(spec["file"])

    print("\nValidation complete.")
    return 0 if overall_success else 1


if __name__ == "__main__":
    sys.exit(main())
