from pathlib import Path


def test_constitution_scaffold_exists():
    root = Path(__file__).resolve().parents[2]
    cdir = root / "constitution"
    assert (cdir / "invariants.yaml").exists()
    assert (cdir / "budgets.yaml").exists()

