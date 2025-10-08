"""Generate synthetic gold fixtures for CIP and PCP datasets."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta
import csv
import math
import random
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FIXTURES = ROOT / "fixtures" / "gold"

@dataclass
class CIPParams:
    start: date = date(2025, 1, 2)
    days: int = 10
    tenor_days: int = 30
    base_spot: float = 1.0
    base_dom: float = 0.03
    base_for: float = 0.028


def generate_cip(path: Path, params: CIPParams) -> None:
    rng = random.Random(17)
    tau = params.tenor_days / 360
    rows: list[list[str]] = []
    for i in range(params.days):
        current = params.start + timedelta(days=i)
        spot = params.base_spot + 0.0002 * (i % 3) - 0.0001 * (i // 3)
        dom_rate = params.base_dom + 0.0002 * ((i + 1) % 4)
        for_rate = params.base_for + 0.0001 * (i % 5)
        noise = (rng.choice([-1, 1]) * 0.00001)
        forward = spot * (1 + (dom_rate - for_rate) * tau) + noise
        rows.append([
            current.isoformat(),
            f"{spot:.4f}",
            f"{forward:.4f}",
            f"{dom_rate:.4f}",
            f"{for_rate:.4f}",
        ])

    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as fh:
        writer = csv.writer(fh)
        writer.writerow(["date", "spot", "forward", "dom_rate", "for_rate"])
        writer.writerows(rows)


@dataclass
class PCPParams:
    start: date = date(2025, 1, 2)
    days: int = 10
    tenor_days: int = 30
    base_spot: float = 100.0
    base_rate: float = 0.02
    base_div: float = 0.01


def generate_pcp(path: Path, params: PCPParams) -> None:
    rng = random.Random(23)
    tau = params.tenor_days / 365
    rows: list[list[str]] = []
    for i in range(params.days):
        current = params.start + timedelta(days=i)
        spot = params.base_spot + 0.5 * (i % 4) - 0.3 * (i // 4)
        strike = params.base_spot + (i % 3) * 0.25
        rate = params.base_rate + 0.0005 * (i % 5)
        div = params.base_div + 0.0003 * (i % 3)
        parity = spot - strike * math.exp(-rate * tau)
        skew = rng.choice([-1, 1]) * 0.0005
        call = parity + 2.45 + 0.01 * (i % 2) + skew
        put = call - parity - skew * 0.8
        rows.append([
            current.isoformat(),
            f"{spot:.2f}",
            f"{strike:.2f}",
            f"{call:.2f}",
            f"{put:.2f}",
            f"{rate:.2f}",
            f"{div:.2f}",
        ])

    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as fh:
        writer = csv.writer(fh)
        writer.writerow(["date", "spot", "strike", "call", "put", "rate", "div"])
        writer.writerows(rows)


def main() -> None:
    generate_cip(FIXTURES / "cip_synth.csv", CIPParams())
    generate_pcp(FIXTURES / "pcp_synth.csv", PCPParams())


if __name__ == "__main__":
    main()