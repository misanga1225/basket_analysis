import matplotlib.pyplot as plt
import numpy as np

PLAYERS = ["O1red", "O2blue", "O3pink", "D1black", "D2orange", "D3yellow"]
COLORS = {
    "O1red": "red",
    "O2blue": "blue",
    "O3pink": "deeppink",
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
    ylabel: str = "Effective Area (m²)",
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
            if np.isfinite(y_val):
                ax.plot(
                    idx,
                    y_val,
                    "x",
                    markeredgecolor="deeppink",
                    markersize=16,
                    markeredgewidth=3,
                )

    ax.set_title(title, fontsize=22)
    ax.set_xlabel("Frame", fontsize=20)
    ax.set_ylabel(ylabel, fontsize=20)
    ax.tick_params(axis="both", labelsize=18)
    ax.legend(fontsize=16, loc="upper right")
    ax.grid(True)

    if xlim is not None:
        ax.set_xlim(0, xlim)
    if ylim is not None:
        ax.set_ylim(0, ylim)


def plot_session_grid(
    trials_data: list[dict],
    ylim: float,
    save_path: str,
    suptitle: str | None = None,
    ylabel: str = "Effective Area (m²)",
):
    fig, axes = plt.subplots(3, 3, figsize=(45, 21))
    axes = axes.flatten()

    for i, trial in enumerate(trials_data):
        pdata = trial["player_data"]
        trial_xlim = len(next(iter(pdata.values()))) if pdata else None
        plot_trial_panel(
            ax=axes[i],
            player_data=pdata,
            title=trial["title"],
            catch_frame=trial["catch_frame"],
            ylim=ylim,
            xlim=trial_xlim,
            ylabel=ylabel,
        )

    for i in range(len(trials_data), 9):
        axes[i].set_visible(False)

    if suptitle:
        fig.suptitle(suptitle, fontsize=28)
        plt.tight_layout(rect=(0, 0, 1, 0.97))
    else:
        plt.tight_layout()
    plt.savefig(save_path, bbox_inches="tight", dpi=150)
    plt.close(fig)
