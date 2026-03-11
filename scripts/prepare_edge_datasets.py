"""Découpe le dataset global en sous-datasets par région Edge."""

from __future__ import annotations

import pandas as pd

SOURCE = "data/raw/transactions_synthetic.csv"

EDGE_TO_REGION = {
    "nouakchott": "Nouakchott",
    "rosso": "Rosso",
    "kaedi": "Kaedi",
}


def main() -> None:
    df = pd.read_csv(SOURCE)
    for edge_suffix, region in EDGE_TO_REGION.items():
        out = f"data/raw/transactions_{edge_suffix}.csv"
        df[df["region"] == region].to_csv(out, index=False)
        print(f"{region} -> {out}")


if __name__ == "__main__":
    main()
