import matplotlib.pyplot as plt
import numpy as np

PLAYERS = ["O1red", "O2blue", "O3pink", "D1black", "D2orange", "D3yellow"]
COLORS = {
    "O1red": "red",
    "O2blue": "blue",
    "O3pink": "pink",
    "D1black": "black",
    "D2orange": "orange",
    "D3yellow": "yellow",
}


def plot_trial_panel(
    ax: plt.Axes,
    player_data: dict[str, np.ndarray],
    title: str,
    catch_frame: int | None = None,
    ylim: tuple[float, float] | None = None,
    xlim: tuple[float, float] | None = None,
):
    for player in PLAYERS:
        if player not in player_data:
            continue
        data_m2 = player_data[player] / 10000.0
        ax.plot(data_m2, color=COLORS[player], label=player, linewidth=1)

    if catch_frame is not None and "O3pink" in player_data:
        idx = catch_frame - 1  # frame_number is 1-based
        if 0 <= idx < len(player_data["O3pink"]):
            y_val = player_data["O3pink"][idx] / 10000.0
            ax.plot(
                idx,
                y_val,
                "o",
                markerfacecolor="none",
                markeredgecolor="pink",
                markersize=8,
                markeredgewidth=3,
            )

    ax.set_title(title)
    ax.set_xlabel("Frame")
    ax.set_ylabel("Area (m²)")
    ax.legend(fontsize="small", loc="upper right")
    ax.grid(True)

    if xlim is not None:
        ax.set_xlim(0, xlim)
    if ylim is not None:
        ax.set_ylim(0, ylim)


def plot_session_grid(
    trials_data: list[dict],
    ylim: float,
    xlim: float,
    save_path: str,
):
    fig, axes = plt.subplots(3, 3, figsize=(45, 21))
    axes = axes.flatten()

    for i, trial in enumerate(trials_data):
        plot_trial_panel(
            ax=axes[i],
            player_data=trial["player_data"],
            title=trial["title"],
            catch_frame=trial["catch_frame"],
            ylim=ylim,
            xlim=xlim,
        )

    for i in range(len(trials_data), 9):
        axes[i].set_visible(False)

    plt.tight_layout()
    plt.savefig(save_path, bbox_inches="tight", dpi=150)
    plt.close(fig)
