import sys
from pathlib import Path

src_dir = str(Path(__file__).resolve().parents[2])
if src_dir not in sys.path:
    sys.path.append(src_dir)

import numpy as np

from analyzers import calculator, utils
from analyzers.datamanager import DataManager
from analyzers.effective_voronoi_timeseries.drawer import plot_session_grid
from analyzers.voronoi_timeseries.event_loader import (
    build_event_path,
    get_first_catch_frame,
)

THETA_DEG_LIST = [30, 45]
THETA_YLIM_OVERRIDE = {30: 70.0}
PROCESSED_DATA_DIR = str(Path(__file__).resolve().parent.parent / "processed_data")
DATASET_DIR = Path(__file__).resolve().parents[3] / "_dataset_yamaha"
RESULTS_DIR = Path(__file__).resolve().parent / "results"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)


def _nan_safe_max_recursive(data) -> float:
    if isinstance(data, np.ndarray):
        if data.size == 0 or np.all(np.isnan(data)):
            return 0.0
        return float(np.nanmax(data))
    elif isinstance(data, dict):
        if not data:
            return 0.0
        return max(_nan_safe_max_recursive(v) for v in data.values())
    return float(data)


def _draw_for_theta(theta_deg: int) -> None:
    pickle_filename = f"effective_area_trajectories_theta{theta_deg}.pkl"
    data_manager = DataManager(PROCESSED_DATA_DIR, pickle_filename=pickle_filename)
    all_data = data_manager.get_all_trajectories()

    g_data = {k: v for k, v in all_data.items() if k.startswith("G")}
    if not g_data:
        print(f"[theta={theta_deg}] No yamaha (G*) data found, skipping.")
        return

    max_value = _nan_safe_max_recursive(g_data)
    if theta_deg in THETA_YLIM_OVERRIDE:
        graph_ylim = THETA_YLIM_OVERRIDE[theta_deg]
    else:
        graph_ylim = utils.round_up(max_value / 10000.0)
    print(f"[theta={theta_deg}] Y-axis limit: {graph_ylim} m2 (X-axis: per-panel)")

    for game_num in range(1, 5):
        match_type = f"G{game_num}"
        if match_type not in all_data:
            continue
        for session_num in range(1, 4):
            trials_data = []
            for trial_num in range(1, 8):
                game_name = f"basket_G{game_num}-S{session_num}T{trial_num}"
                if game_name not in all_data[match_type]:
                    continue
                player_data = all_data[match_type][game_name]
                event_path = build_event_path(
                    str(DATASET_DIR), game_num, session_num, trial_num
                )
                catch_frame = get_first_catch_frame(event_path)
                trials_data.append(
                    {
                        "player_data": player_data,
                        "catch_frame": catch_frame,
                        "title": f"T{trial_num} ({game_name})",
                    }
                )
            if not trials_data:
                continue
            save_path = (
                RESULTS_DIR
                / f"effective_voronoi_timeseries_G{game_num}_S{session_num}_theta{theta_deg}.png"
            )
            plot_session_grid(
                trials_data=trials_data,
                ylim=graph_ylim,
                save_path=str(save_path),
                suptitle=f"Effective Voronoi (theta={theta_deg}deg)  G{game_num} S{session_num}",
            )
            print(f"Saved: {save_path}")


if __name__ == "__main__":
    for theta in THETA_DEG_LIST:
        _draw_for_theta(theta)
