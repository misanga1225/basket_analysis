import os
import pandas as pd
import matplotlib.pyplot as plt
import IPython.display as HTML
import pickle

def get_csv_file_path(dir_name: str) -> list:
    """
    Get all sorted file paths in the given directory.
    :param dir_name: Directory to search for CSV files.
    :return: List of file paths.
    """
    file_paths = []
    
    for file_name in os.listdir(dir_name):
        if file_name.endswith('.csv'):
            file_paths.append(os.path.join(dir_name, file_name))
        else:
            continue

    file_paths.sort()

    return file_paths

def get_data_from_csv(file_path: str) -> pd.DataFrame:
    """
    Read data from a CSV file and return it as a dictionary.
    :param file_path: Path to the CSV file.
    :return: Dictionary with data from the CSV file.
    """
    data = pd.read_csv(file_path)
    return data

def make_dir(dir_name: str) -> None:
    """
    Create a directory if it does not exist.
    :param dir_name: Directory to create.
    """
    os.makedirs(dir_name, exist_ok=True)
    print(f"Directory '{dir_name}' is ready.")

def show_plot(fig) -> None:
    """
    Display the plot.
    :param fig: Matplotlib figure object.
    :param ax: Matplotlib axes object.
    """
    plt.show()
    plt.close(fig)

def save_plot(fig, dir_name: str, file_name: str) -> None:
    """
    Save the plot to a file.
    :param fig: Matplotlib figure object.
    :param dir_name: Directory to save the plot.
    :param file_name: Name of the file to save the plot.
    """
    make_dir(dir_name)
    if not file_name.endswith('.png'):
        file_name += '.png'
    file_path = os.path.join(dir_name, file_name)
    fig.savefig(file_path, bbox_inches='tight', dpi=300)
    plt.close(fig)

def save_voronoi_animation(anim, dir_name: str, file_name: str) -> None:
    """
    Save the Voronoi animation to a file.
    :param anim: Matplotlib animation object.
    :param dir_name: Directory to save the animation.
    :param file_name: Name of the file to save the animation.
    """
    make_dir(dir_name)
    if not file_name.endswith('.mp4'):
        file_name += '.mp4'
    file_path = os.path.join(dir_name, file_name)
    anim.save(file_path, fps=20, extra_args=['-vcodec', 'libx264'], writer='ffmpeg', dpi=100)
    plt.close(anim._fig)

def save_pickle(obj, dir_name: str, file_name: str) -> None:
    """
    Save an object to a pickle file.
    :param obj: Object to save.
    :param dir_name: Directory to save the pickle file.
    :param file_name: Name of the pickle file.
    """
    make_dir(dir_name)
    if not file_name.endswith('.pkl'):
        file_name += '.pkl'
    file_path = os.path.join(dir_name, file_name)
    
    with open(file_path, 'wb') as f:
        pickle.dump(obj, f)

def load_pickle(dir_name: str, file_name: str):
    """
    Load an object from a pickle file.
    :param dir_name: Directory where the pickle file is located.
    :param file_name: Name of the pickle file.
    :return: Loaded object.
    """
    if not file_name.endswith('.pkl'):
        file_name += '.pkl'
    file_path = os.path.join(dir_name, file_name)
    
    with open(file_path, 'rb') as f:
        obj = pickle.load(f)
    
    return obj

def write_data_to_csv(data: pd.DataFrame, dir_name: str, file_name: str) -> None:
    """
    Write a DataFrame to a CSV file.
    :param data: DataFrame to write.
    :param dir_name: Directory to save the CSV file.
    :param file_name: Name of the CSV file.
    """
    make_dir(dir_name)
    if not file_name.endswith('.csv'):
        file_name += '.csv'
    file_path = os.path.join(dir_name, file_name)
    
    data.to_csv(file_path, index=False)

def flatten_silhouette_dict(data: dict) -> pd.DataFrame:
    """
    :param data: dict[Player][MatchType][n_clusters] = score
    :return: pd.DataFrame
    """
    rows = []
    for player, match_scores in data.items():
        for match_type, clusters in match_scores.items():
            for k, score in clusters.items():
                rows.append({
                    "Player": player,
                    "MatchType": match_type,
                    "n_clusters": int(k),
                    "SilhouetteScore": float(score)
                })
    df = pd.DataFrame(rows)
    return df


#