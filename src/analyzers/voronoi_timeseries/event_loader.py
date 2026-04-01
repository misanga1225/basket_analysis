from pathlib import Path

import pandas as pd


def build_event_path(dataset_dir: str, game: int, session: int, trial: int) -> Path:
    return Path(dataset_dir) / f"basket_G{game}-S{session}T{trial}_event.csv"


def get_first_catch_frame(event_csv_path: str | Path, player_column: str = "O3_pink") -> int | None:
    path = Path(event_csv_path)
    if not path.exists():
        return None

    df = pd.read_csv(path)
    if player_column not in df.columns:
        return None

    catch_rows = df[df[player_column] == "catch"]
    if catch_rows.empty:
        return None

    return int(catch_rows.iloc[0]["frame_number"])
