from collections.abc import Iterable

import pickle
import numpy as np

from pathlib import Path
from collections import OrderedDict

class DataManager:
    """
    Class to manage all game data using pickle.
    """
    def __init__(self, data_dir: str):
        """
        :param data_dir: Directory containing the pickle files.
        """
        self._trajectories = {}
        data_path = Path(data_dir)

        for match_dir in data_path.iterdir():
            if not match_dir.is_dir():
                continue
            match_type = match_dir.name
            self._trajectories[match_type] = {}

            for game_dir in match_dir.iterdir():
                if not game_dir.is_dir():
                    continue
                game_name = game_dir.name
                self._trajectories[match_type][game_name] = {}

                for file_path in game_dir.glob('*.pkl'):
                    with open(file_path, 'rb') as f:
                        raw_data = pickle.load(f)
                        self._trajectories[match_type][game_name] = {
                            player: np.array(traj) for player, traj in raw_data.items()
                        }
        
        # Sort self.trajectories by match_type, game_name, and player_name
        self._trajectories = OrderedDict(
            sorted(
                (match_type, OrderedDict(
                    sorted(
                        (game_name, OrderedDict(
                            sorted(players_data.items())
                        )) for game_name, players_data in games.items()
                    )
                )) for match_type, games in self._trajectories.items()
            )
        )

        # display all match_type
        print("Match Type: ", self._trajectories.keys())

    def get_all_match_types(self) -> list[str]:
        return list(self._trajectories.keys())

    def get_all_game_names(self) -> list[str]:
        all_game_names = set()
        for match_type in self.get_all_match_types():
            all_game_names.update(self._trajectories[match_type].keys())
        return list(all_game_names)

    def get_all_player_names(self) -> list[str]:
        all_player_names = set()
        for match_type in self.get_all_match_types():
            for game_name in self._trajectories[match_type].keys():
                all_player_names.update(self._trajectories[match_type][game_name].keys())
        return sorted(list(all_player_names))

    def get_all_teams(self) -> list[str]:
        all_teams = set()
        for match_type in self.get_all_match_types():
            for game_name in self._trajectories[match_type].keys():
                for player_name in self._trajectories[match_type][game_name].keys():
                    all_teams.add(player_name[0])
        return sorted(list(all_teams))

    def get_trajectory(self, match_type: str, game_name: str, player_name: str) -> np.ndarray:
        return self._trajectories[match_type][game_name][player_name]

    def get_data_by_player(self, player_name: str) -> dict[str, dict[str, np.ndarray]]:
        return {match_type: {game_name: self._trajectories[match_type][game_name][player_name] for game_name in self._trajectories[match_type].keys()} for match_type in self._trajectories.keys()}

    def get_data_by_team(self, team_name: str) -> dict[str, dict[str, np.ndarray]]:
        """
        指定されたチーム（プレイヤー名の一文字目が一致する）のデータの総和（ndarray）を返すメソッド
        :param team_name: チームの識別子（例: 'A', 'B'）
        :return: match_type -> game_name -> チームデータの総和(np.ndarray) の辞書
        """
        team_data: dict[str, dict[str, np.ndarray]] = {}
        for match_type, games in self._trajectories.items():
            team_data[match_type] = {}
            for game_name, players in games.items():
                target_players_data = [data for player, data in players.items() if player.startswith(team_name)]
                if target_players_data:
                    team_data[match_type][game_name] = np.sum(target_players_data, axis=0)
                else:
                    team_data[match_type][game_name] = np.array([])
                    
        return team_data

    def z_normalize_trajectory(self, trajectory: np.ndarray) -> np.ndarray:
        return (trajectory - np.mean(trajectory)) / np.std(trajectory)

    def get_all_trajectories(self) -> dict[str, dict[str, dict[str, np.ndarray]]]:
        return self._trajectories