import numpy as np

from tslearn.metrics import cdist_dtw
from sklearn.metrics import silhouette_score
from kmedoids import KMedoids

def dynamic_time_warping(
    data: list[np.ndarray]
) -> np.ndarray:
    return cdist_dtw(data)

def k_medoids(
    data: list[np.ndarray],
    n_clusters: int,
) -> tuple[list[int], list[int], float]:
    dtw_matrix = dynamic_time_warping(data)
    
    kmedoids = KMedoids(n_clusters=n_clusters, metric='precomputed')
    kmedoids.fit(dtw_matrix)

    sil_score = silhouette_score(dtw_matrix, kmedoids.labels_, metric='precomputed')

    return kmedoids.labels_, kmedoids.medoid_indices_, sil_score