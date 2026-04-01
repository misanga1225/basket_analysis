import sys
from pathlib import Path

src_dir = str(Path(__file__).resolve().parents[2])
if src_dir not in sys.path:
    sys.path.append(src_dir)

from analyzers.datamanager import DataManager
from analyzers import utils, calculator
from analyzers.voronoi_timeseries.event_loader import get_first_catch_frame, build_event_path
from analyzers.voronoi_timeseries.drawer import plot_session_grid

data_manager = DataManager(str(Path(__file__).resolve().parent.parent / 'processed_data'))
all_data = data_manager.get_all_trajectories()

g_data = {k: v for k, v in all_data.items() if k.startswith('G')}
max_value = calculator.max_recursive(g_data)
graph_ylim = utils.round_up(max_value / 10000.0)
max_len = calculator.max_len_recursive(g_data)
graph_xlim = max_len
print(f'Y-axis limit: {graph_ylim} m2')
print(f'X-axis limit: {graph_xlim} frames')

DATASET_DIR = Path(__file__).resolve().parents[3] / '_dataset_yamaha'
RESULTS_DIR = Path(__file__).resolve().parent / 'results'
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

for game_num in range(1, 5):
    match_type = f'G{game_num}'
    for session_num in range(1, 4):
        trials_data = []
        for trial_num in range(1, 8):
            game_name = f'basket_G{game_num}-S{session_num}T{trial_num}'
            player_data = all_data[match_type][game_name]
            event_path = build_event_path(str(DATASET_DIR), game_num, session_num, trial_num)
            catch_frame = get_first_catch_frame(event_path)
            trials_data.append({
                'player_data': player_data,
                'catch_frame': catch_frame,
                'title': f'T{trial_num} ({game_name})',
            })
        save_path = RESULTS_DIR / f'voronoi_timeseries_G{game_num}_S{session_num}.png'
        plot_session_grid(
            trials_data=trials_data,
            ylim=graph_ylim,
            xlim=graph_xlim,
            save_path=str(save_path),
        )
        print(f'Saved: {save_path}')
