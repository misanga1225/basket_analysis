from courts.court import BaseCourt

import numpy as np
import pandas as pd

from scipy.spatial import Voronoi
from shapely.geometry import box, LineString, Point
from shapely.geometry import Polygon as ShapelyPolygon

class VoronoiPreProcessor():

    def __init__(self, court: BaseCourt):
        self.court = court
        self.border = box(0, 0, court.court_width, court.court_height)

    def compute_all_frames(self, data: pd.DataFrame):
        """
        Compute Voronoi regions and areas for all frames at once.
        :param data: DataFrame containing player positions.
        :return: List of ((player_ridge_vertices, clipped_vertices), voronoi_areas) per frame.
        """
        player_names = self.court.players
        results = []
        for frame in range(len(data)):
            points = np.array([
                [data[f'x_{player}'][frame], data[f'y_{player}'][frame]]
                for player in player_names
            ])
            result = self.compute_voronoi_regions_and_areas(points)
            results.append(result)
        return results

    def get_players_area_trajectories(self, data: pd.DataFrame, precomputed_results=None):
        """
        Calculate Voronoi areas for players based on their trajectories.
        :param data: DataFrame containing player positions.
        :param precomputed_results: Optional precomputed Voronoi results from compute_all_frames().
        :return: Dictionary mapping player names to their Voronoi area trajectories.
        """
        players_area_trajectories = {}
        player_names = self.court.players

        if precomputed_results is None:
            precomputed_results = self.compute_all_frames(data)

        for (player_ridge_vertices, clipped_vertices), voronoi_areas in precomputed_results:
            if not self._check_area_validity(voronoi_areas):
                raise ValueError("Voronoi areas do not match the court area. Please check the input points.")

            for player_idx, area in voronoi_areas.items():
                player_name = player_names[player_idx]
                if player_name not in players_area_trajectories:
                    players_area_trajectories[player_name] = []
                players_area_trajectories[player_name].append(area)

        return players_area_trajectories

    def compute_voronoi_regions_and_areas(self, points: np.array):
        """
        Compute Voronoi regions and areas for the given points.
        :param points: Array of points for Voronoi calculation.
        :return: Dictionary mapping player indices to their Voronoi areas.
        """
        player_ridge_vertices, clipped_vertices = self._voronoi(points)
        voronoi_areas = self._calculate_voronoi_areas(player_ridge_vertices, clipped_vertices)
        if not self._check_area_validity(voronoi_areas):
            raise ValueError("Voronoi areas do not match the court area. Please check the input points.")
        
        return (player_ridge_vertices, clipped_vertices), voronoi_areas

    def _check_area_validity(self, voronoi_areas: dict):
        """
        Check if the Voronoi areas for all players are valid.
        :param voronoi_areas: Dictionary mapping player indices to their Voronoi areas.
        :return: Boolean indicating if all players have valid areas.
        """
        total_area = sum(voronoi_areas.values())
        court_area = self.border.area
        return np.isclose(total_area, court_area, atol=1e-8)

    def _calculate_voronoi_areas(self, player_ridge_vertices: dict, clipped_vertices: np.array):
        """
        Calculate Voronoi areas for the given points.
        :param player_ridge_vertices: Dictionary mapping player indices to their ridge vertices.
        :param clipped_vertices: Array of clipped vertices from Voronoi calculation.
        :return: Dictionary mapping player indices to their Voronoi areas.
        """        
        voronoi_areas = {}
        for player_idx, indices in player_ridge_vertices.items():
            vertices = clipped_vertices[indices]
            if len(vertices) < 3:
                voronoi_areas[player_idx] = 0.0
                continue
            polygon = ShapelyPolygon(vertices)
            area = polygon.area
            voronoi_areas[player_idx] = area

        return voronoi_areas

    def _voronoi(self, points: np.array):
        """
        Calculate Voronoi areas for the given points.
        :param points: Array of points for Voronoi calculation.
        :return: List of Voronoi areas.
        """
        vor = Voronoi(points)

        points_ridge_vertices = {i: [] for i in range(len(vor.points))}
        clipped_vertices = np.empty((0, 2))

        center = vor.points.mean(axis=0)
        ptp_bound = np.ptp(vor.points, axis=0)

        for pointidx, simplex in zip(vor.ridge_points, vor.ridge_vertices):
            simplex = np.asarray(simplex)

            if np.all(simplex >= 0):
                ridge_line = LineString(vor.vertices[simplex])
                intersection = ridge_line.intersection(self.border)
            else:
                i = int(simplex[simplex >= 0][0])

                t = vor.points[pointidx[1]] - vor.points[pointidx[0]]
                t /= np.linalg.norm(t)
                n = np.array([-t[1], t[0]])

                midpoint = vor.points[[pointidx[0], pointidx[1]]].mean(axis=0)
                direction = np.sign(np.dot(midpoint - center, n)) * n
                if (vor.furthest_site):
                    direction = -direction
                aspect_factor = abs(ptp_bound.max() / ptp_bound.min())
                far_point = vor.vertices[i] + direction * aspect_factor * ptp_bound.max() * 10
                
                ridge_line = LineString([vor.vertices[i], far_point])
                intersection = ridge_line.intersection(self.border)

            coords = np.array(ridge_line.coords[0])

            if intersection.is_empty:
                continue

            coords = np.array(intersection.coords)

            if isinstance(intersection, Point):
                if not np.any(np.all(np.isclose(clipped_vertices, coords[0], atol=1e-8), axis=1)):
                    clipped_vertices = np.vstack([clipped_vertices, coords[0]])
            elif isinstance(intersection, LineString):
                if not np.any(np.all(np.isclose(clipped_vertices, coords[0], atol=1e-8), axis=1)):
                    clipped_vertices = np.vstack([clipped_vertices, coords[0]])
                if not np.any(np.all(np.isclose(clipped_vertices, coords[1], atol=1e-8), axis=1)):
                    clipped_vertices = np.vstack([clipped_vertices, coords[1]])
            else:
                print(f"Unexpected intersection type: {type(intersection)}")
                continue

            for coord in coords:
                index = int(np.where(np.all(np.isclose(clipped_vertices, coord, atol=1e-8), axis=1))[0])
                if index not in points_ridge_vertices[pointidx[0]]:
                    points_ridge_vertices[pointidx[0]].append(index)
                if index not in points_ridge_vertices[pointidx[1]]:
                    points_ridge_vertices[pointidx[1]].append(index)

        # Add court corners if necessary
        corner_coords = np.array([
            [self.border.bounds[0], self.border.bounds[1]],
            [self.border.bounds[2], self.border.bounds[1]],
            [self.border.bounds[2], self.border.bounds[3]],
            [self.border.bounds[0], self.border.bounds[3]]
        ])
        for corner in corner_coords:
            if not np.any(np.all(np.isclose(clipped_vertices, corner, atol=1e-8), axis=1)):
                clipped_vertices = np.vstack([clipped_vertices, corner])

            corner_index = int(np.where(np.all(np.isclose(clipped_vertices, corner, atol=1e-8), axis=1))[0])
            dists = np.linalg.norm(vor.points - corner, axis=1)
            closest_point_index = np.argmin(dists)
            if corner_index not in points_ridge_vertices[closest_point_index]:
                points_ridge_vertices[closest_point_index].append(corner_index)

        # Sort each list of indices based on their angle from the centroid of the corresponding player's vertices
        for player_idx, indices in points_ridge_vertices.items():
            if len(indices) < 3:
                continue
            pts = clipped_vertices[indices]
            center = pts.mean(axis=0)
            angles = np.arctan2(pts[:, 1] - center[1], pts[:, 0] - center[0])
            sorted_indices = [indices[i] for i in np.argsort(angles)]
            points_ridge_vertices[player_idx] = sorted_indices

        return points_ridge_vertices, clipped_vertices

