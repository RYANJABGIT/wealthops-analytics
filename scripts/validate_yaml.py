"""Validate YAML syntax without cloud credentials."""
from pathlib import Path
import yaml


def main() -> None:
    paths = [p for p in Path(".").rglob("*") if p.suffix in (".yaml", ".yml")
             and ".git" not in p.parts and ".venv" not in p.parts
             and "target" not in p.parts and "dbt_packages" not in p.parts]
    for path in paths:
        with path.open(encoding="utf-8") as file:
            list(yaml.safe_load_all(file))
        print("OK", path)


if __name__ == "__main__":
    main()

