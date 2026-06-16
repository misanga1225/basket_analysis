"""各試行の平均有効ボロノイ領域を analysis_dataset_voronoi_shizudai.csv 形式で出力する。

テンプレート CSV (Game, Session, Trial, Phase, Per_final, O1, O2, O3, D1, D2, D3)
の O1〜D3 列を、各試行の平均有効ボロノイ領域 [m^2] で埋める。
theta=30, theta=45 それぞれについて 1 ファイルずつ出力する。

実行（リポジトリルートから）:
    python src/analyzers/effective_voronoi_timeseries/export_mean_voronoi.py
"""
import sys
from pathlib import Path

src_dir = str(Path(__file__).resolve().parents[2])
if src_dir not in sys.path:
    sys.path.append(src_dir)

import numpy as np
import pandas as pd

from analyzers.datamanager import DataManager

THETA_DEG_LIST = [30, 45]
PROCESSED_DATA_DIR = str(Path(__file__).resolve().parent.parent / "processed_data")
REPO_ROOT = Path(__file__).resolve().parents[3]
# 出力先（.gitignore の **_dataset** / **results** に掛からない名前にする）。
# テンプレートも同梱し、clone & run で再現できるよう自己完結させる。
OUTPUT_DIR = REPO_ROOT / "analysis_output"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
TEMPLATE_CSV = OUTPUT_DIR / "voronoi_template.csv"

# テンプレートの列名 -> pickle 内の選手名
COLUMN_TO_PLAYER = {
    "O1": "O1red",
    "O2": "O2blue",
    "O3": "O3pink",
    "D1": "D1black",
    "D2": "D2orange",
    "D3": "D3yellow",
}
PLAYER_COLUMNS = list(COLUMN_TO_PLAYER.keys())
CM2_PER_M2 = 10000.0


def _mean_area_m2(trajectory) -> float:
    """1 試行・1 選手の平均有効ボロノイ領域 [m^2]。NaN フレームは除外。"""
    arr = np.asarray(trajectory, dtype=float)
    if arr.size == 0 or np.all(np.isnan(arr)):
        return np.nan
    return float(np.nanmean(arr)) / CM2_PER_M2


def _export_for_theta(theta_deg: int) -> Path:
    pickle_filename = f"effective_area_trajectories_theta{theta_deg}.pkl"
    data_manager = DataManager(PROCESSED_DATA_DIR, pickle_filename=pickle_filename)
    all_data = data_manager.get_all_trajectories()

    df = pd.read_csv(TEMPLATE_CSV)

    # 出力用に player 列を float(NaN) で初期化
    for col in PLAYER_COLUMNS:
        df[col] = np.nan

    n_filled = 0
    n_missing = 0
    for i, row in df.iterrows():
        game, session, trial = int(row["Game"]), int(row["Session"]), int(row["Trial"])
        match_type = f"G{game}"
        game_name = f"basket_G{game}-S{session}T{trial}"
        player_data = all_data.get(match_type, {}).get(game_name)
        if not player_data:
            n_missing += 1
            print(f"  [WARN] no data: {game_name} -> 空欄のまま")
            continue
        for col, player in COLUMN_TO_PLAYER.items():
            if player in player_data:
                df.at[i, col] = _mean_area_m2(player_data[player])
        n_filled += 1

    out_path = OUTPUT_DIR / f"voronoi_mean_theta{theta_deg}.csv"
    # player 列のみ小数第5位、Phase/Per_final 等は整数のまま維持
    out_df = df.copy()
    for col in PLAYER_COLUMNS:
        out_df[col] = out_df[col].map(
            lambda v: "" if pd.isna(v) else f"{v:.5f}"
        )
    out_df.to_csv(out_path, index=False)
    print(f"[theta={theta_deg}] filled={n_filled} missing={n_missing} -> {out_path}")
    return out_path


if __name__ == "__main__":
    for theta in THETA_DEG_LIST:
        _export_for_theta(theta)
