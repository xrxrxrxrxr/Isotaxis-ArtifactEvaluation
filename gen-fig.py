import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
from matplotlib.patches import Patch

# -----------------------
# Global style (CCS-like)
# -----------------------
def setup_style():
    plt.rcParams.update({
        "font.family": "serif",
        "font.size": 9.5,
        "axes.labelsize": 10.5,
        "axes.titlesize": 10.5,
        "xtick.labelsize": 9.0,
        "ytick.labelsize": 9.0,
        "legend.fontsize": 8.8,
        # "axes.spines.top": False,
        # "axes.spines.right": False,
        "axes.linewidth": 0.8,
        "pdf.fonttype": 42,
        "ps.fonttype": 42,
    })


# -----------------------
# Helpers
# -----------------------
def format_k(x, pos):
    if x >= 1000:
        return f"{int(round(x/1000))}k"
    return f"{int(x)}"

ISO_COLOR = "#3F9ED8"       # clearer blue
# ISO_COLOR = "#9164DE"
POMPE_COLOR = "#D98A54"     # brighter orange-red
HOTSTUFF_COLOR = "#E0B11E"  # brighter golden yellow
SDUMBO_COLOR = "#3F9ED8"    # vibrant purple
NORMAL_COLOR = "#7DBCC6"    # fresh teal
ATTACK_COLOR = "#D98A54"    # warm orange
# GRID_COLOR = "#E6E6E6"
GRID_COLOR="#FFFFFF"  # slightly darker gray for grid
GRID_COLOR1="#D9D9D9"  # original lighter gray for grid
# SPINE_COLOR = "#6F6F6F"
SPINE_COLOR = "#3A3A3A"  # slightly lighter gray for spines
TICK_COLOR = "#3A3A3A"
PANEL_SIZE = (4.02, 2.52)
BAR_EDGE_COLOR = SPINE_COLOR
DOS_HATCH = "/"
LEGEND_DOS_HATCH = "////"


def _add_inset_legend(ax, loc, bbox_to_anchor, handles=None, fontsize=None):
    leg = ax.legend(
        handles=handles,
        loc=loc,
        bbox_to_anchor=bbox_to_anchor,
        fontsize=fontsize,
        frameon=True,
        fancybox=False,
        framealpha=0.9,
        borderpad=0.28,
        handlelength=1.55,
        handletextpad=0.42,
        labelspacing=0.24,
        borderaxespad=0.0,
    )
    leg.get_frame().set_edgecolor("#5F5F5F")
    leg.get_frame().set_linewidth(0.55)
    leg.get_frame().set_facecolor("white")
    return leg


def _attack_legend_handles(normal_color, attack_color):
    return [
        Patch(
            facecolor=normal_color,
            edgecolor=BAR_EDGE_COLOR,
            linewidth=0.55,
            label="Normal",
        ),
        Patch(
            facecolor=attack_color,
            edgecolor=BAR_EDGE_COLOR,
            linewidth=0.55,
            hatch=LEGEND_DOS_HATCH,
            label="Under DoS",
        ),
    ]


def _plot_protocol_curves(
    filename,
    isotaxis_points,
    pompe_points,
    isotaxis_label,
    pompe_label,
    xlabel,
    ylabel,
    x_scale,
    y_scale,
    xlim,
    ylim,
    xticks,
    yticks,
    legend_loc="lower right",
    legend_anchor=(0.98, 0.08),
    panel_note=None,
):
    fig, ax = plt.subplots(figsize=PANEL_SIZE)

    iso_x = [x / x_scale for x, _ in isotaxis_points]
    iso_y = [y / y_scale for _, y in isotaxis_points]
    pompe_x = [x / x_scale for x, _ in pompe_points]
    pompe_y = [y / y_scale for _, y in pompe_points]

    ax.plot(
        iso_x,
        iso_y,
        color=ISO_COLOR,
        linewidth=1.8,
        marker="x",
        markersize=4.6,
        # markerfacecolor="white",
        # markeredgecolor=ISO_COLOR,
        markeredgewidth=1.0,
        label=isotaxis_label,
        zorder=3,
    )

    ax.plot(
        pompe_x,
        pompe_y,
        color=POMPE_COLOR,
        linewidth=1.8,
        marker="D",
        markersize=4.2,
        markerfacecolor="white",
        markeredgewidth=0.9,
        label=pompe_label,
        zorder=3,
    )

    ax.set_xlabel(xlabel, labelpad=5)
    ax.set_ylabel(ylabel, labelpad=6)

    ax.set_xlim(*xlim)
    ax.set_ylim(*ylim)
    ax.set_xticks(xticks)
    ax.set_yticks(yticks)

    ax.grid(
        True,
        which="major",
        linestyle="-",
        linewidth=0.5,
        color=GRID_COLOR1,
        alpha=0.7,
        zorder=0,
    )

    ax.spines["left"].set_color(SPINE_COLOR)
    ax.spines["bottom"].set_color(SPINE_COLOR)
    ax.spines["top"].set_color(SPINE_COLOR)
    ax.spines["right"].set_color(SPINE_COLOR)
    ax.tick_params(axis="both", colors=TICK_COLOR, width=0.8, length=3)

    if panel_note is not None:
        note_x = 0.06
        note_y = 0.92
        note_ha = "left"
        note_va = "top"
        ax.text(
            note_x,
            note_y,
            panel_note,
            transform=ax.transAxes,
            ha=note_ha,
            va=note_va,
            fontsize=10.8,
            color="#4A4A4A",
            zorder=4,
        )

    _add_inset_legend(
        ax,
        loc=legend_loc,
        bbox_to_anchor=legend_anchor,
    )

    fig.tight_layout(pad=0.6)
    fig.savefig(f"python-fig/{filename}.pdf", bbox_inches="tight")
    plt.close(fig)

def plot_throughput_latency_intro():
    # -----------------------
    # Data
    # -----------------------
    iso_x = [3033.28, 11030.57, 12972.61, 24988.89, 33234.86]
    iso_y = [4.928, 8.941, 12.755, 20.895, 25.797]

    pompe_x = [3132.52, 8740.28, 11846.21, 15866.12]
    pompe_y = [4.746, 9.165, 15.586, 26.251]

    # -----------------------
    # Figure
    # -----------------------
    # Match a compact single-column paper figure around 10.2cm x 6.4cm.
    fig, ax = plt.subplots(figsize=(4.02, 2.52))

    # -----------------------
    # Plot lines
    # -----------------------
    ax.plot(
        iso_x, iso_y,
        color=ISO_COLOR,
        linewidth=1.5,
        marker="x",
        markersize=5.5,
        markeredgewidth=1.2,
        label="Isotaxis-HS-100",
        zorder=3,
    )

    ax.plot(
        pompe_x, pompe_y,
        color=POMPE_COLOR,
        linewidth=1.5,
        marker="D",
        markersize=4.8,
        markerfacecolor="white",
        markeredgewidth=1.0,
        label="Pompe-HS-100",
        zorder=3,
    )

    # -----------------------
    # Axes, ticks, grid
    # -----------------------
    ax.set_xlabel("Throughput (tx/s)", labelpad=6)
    ax.set_ylabel("Latency (s)", labelpad=6)

    ax.set_xlim(2000, 34000)
    ax.set_ylim(3, 28)

    ax.set_xticks([5000, 10000, 15000, 20000, 25000, 30000])
    ax.xaxis.set_major_formatter(FuncFormatter(format_k))

    ax.set_yticks([5, 10, 15, 20, 25])

    pompe_last_x = pompe_x[-1]
    ax.axvspan(
        pompe_last_x,
        ax.get_xlim()[1],
        color="#99A0AD",
        alpha=0.06,
        zorder=0,
    )
    ax.axvline(
        pompe_last_x,
        color=POMPE_COLOR,
        linestyle=(0, (3, 2)),
        linewidth=1.0,
        alpha=0.75,
        zorder=1,
    )
    ax.text(
        pompe_last_x + 650,
        27.15,
        "not observed\nwithin wait budget",
        color=SPINE_COLOR,
        fontsize=7.9,
        ha="left",
        va="top",
    )

    # ax.grid(
    #     False,
    #     which="major",
    #     linestyle="-",
    #     linewidth=0.5,
    #     color=GRID_COLOR1,
    #     alpha=0.8,
    #     zorder=0
    # )

    # Lighten visible spines
    ax.spines["left"].set_color(SPINE_COLOR)
    ax.spines["bottom"].set_color(SPINE_COLOR)
    ax.spines["top"].set_color(SPINE_COLOR)
    ax.spines["right"].set_color(SPINE_COLOR)

    ax.tick_params(axis="both", colors="#333333", width=0.8, length=3)

    # -----------------------
    # Legend
    # -----------------------
    _add_inset_legend(
        ax,
        loc="lower right",
        bbox_to_anchor=(0.98, 0.1),
    )

    # -----------------------
    # Layout & export
    # -----------------------
    fig.tight_layout(pad=0.6)

    fig.savefig("python-fig/tradeoff-100-intro.pdf", bbox_inches="tight")
    # fig.savefig("python-fig/tradeoff-100-intro.png", dpi=400, bbox_inches="tight")

    # plt.show()
    plt.close(fig)

def plot_attacks_intro():
    import matplotlib.pyplot as plt

    # -----------------------
    # Data
    # -----------------------
    categories = ["Normal", "Under DoS"]
    latency = [1.91, 14.439]
    throughput = [524, 69]

    # -----------------------
    # Style (match previous CCS-like figure)
    # -----------------------
    plt.rcParams.update({
        "font.family": "serif",
        "font.size": 10,
        "axes.labelsize": 11,
        "axes.titlesize": 11,
        "xtick.labelsize": 9.5,
        "ytick.labelsize": 9.5,
        "legend.fontsize": 9.5,
        "hatch.linewidth": 0.25,
        "axes.linewidth": 0.8,
        "pdf.fonttype": 42,
        "ps.fonttype": 42,
    })

    # normal_color = "#C6D39B"   # keep the original green for the intro bar chart
    normal_color = "#C8CFB0"
    attack_color = ATTACK_COLOR
    # grid_color = "#D9D9D9"
    grid_color = GRID_COLOR  # slightly darker gray for grid

    # -----------------------
    # Figure
    # -----------------------
    fig, axes = plt.subplots(1, 2, figsize=(5.6, 3.15))

    # Common x positions
    x = [0, 0.72]
    # Bar width is in data units; with a wider x-range it looks visually thinner,
    # so use a slightly wider bar to preserve the original perceived thickness.
    bar_width = 0.34
    x_limits = (x[0] - bar_width / 2 - 0.3, x[-1] + bar_width / 2 + 0.3)

    # -----------------------
    # Left subplot: Latency
    # -----------------------
    ax = axes[0]
    bars1 = ax.bar(
        x,
        latency,
        width=bar_width,
        color=[normal_color, attack_color],
        edgecolor=BAR_EDGE_COLOR,
        linewidth=0.55,
        zorder=3
    )
    bars1.patches[1].set_hatch(DOS_HATCH)

    # ax.set_title("Latency (s)", pad=6, fontsize=11)
    ax.set_ylabel("Latency (s)")
    ax.set_xlim(*x_limits)
    ax.set_xticks(x)
    ax.set_xticklabels(categories)
    ax.set_ylim(0, 16)
    ax.set_yticks(range(0, 17, 2))

    ax.grid(
        axis="y",
        linestyle="-",
        linewidth=0.5,
        color=grid_color,
        alpha=0.8,
        zorder=0
    )

    ax.spines["left"].set_color(SPINE_COLOR)
    ax.spines["bottom"].set_color(SPINE_COLOR)
    ax.spines["top"].set_color(SPINE_COLOR)
    ax.spines["right"].set_color(SPINE_COLOR)
    ax.tick_params(axis="both", colors="#333333", width=0.8, length=3)
    ax.tick_params(axis="x", labelsize=9.3)

    handles_left = _attack_legend_handles(normal_color, attack_color)
    _add_inset_legend(
        ax,
        loc="upper left",
        bbox_to_anchor=(0.04, 0.94),
        handles=handles_left,
        fontsize=8.6,
    )

    # value labels
    for bar, val in zip(bars1, latency):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + 0.35,
            f"{val:.3f}".rstrip("0").rstrip("."),
            ha="center",
            va="bottom",
            fontsize=8.5,
            color="#444444"
        )

    # -----------------------
    # Right subplot: Throughput
    # -----------------------
    ax = axes[1]
    bars2 = ax.bar(
        x,
        throughput,
        width=bar_width,
        color=[normal_color, attack_color],
        edgecolor=BAR_EDGE_COLOR,
        linewidth=0.55,
        zorder=3
    )
    bars2.patches[1].set_hatch(DOS_HATCH)

    # ax.set_title("Throughput (tx/s)", pad=6, fontsize=11)
    ax.set_ylabel("Throughput (tx/s)", labelpad=8)
    ax.set_xlim(*x_limits)
    ax.set_xticks(x)
    ax.set_xticklabels(categories)
    ax.set_ylim(0, 600)
    ax.set_yticks(range(0, 601, 100))

    ax.grid(
        axis="y",
        linestyle="-",
        linewidth=0.5,
        color=grid_color,
        alpha=0.8,
        zorder=0
    )

    ax.spines["left"].set_color(SPINE_COLOR)
    ax.spines["bottom"].set_color(SPINE_COLOR)
    ax.spines["top"].set_color(SPINE_COLOR)
    ax.spines["right"].set_color(SPINE_COLOR)
    ax.tick_params(axis="both", colors="#333333", width=0.8, length=3)
    ax.tick_params(axis="x", labelsize=9.3)

    handles_right = _attack_legend_handles(normal_color, attack_color)
    _add_inset_legend(
        ax,
        loc="upper right",
        bbox_to_anchor=(0.96, 0.94),
        handles=handles_right,
        fontsize=8.6,
    )

    # value labels
    for bar, val in zip(bars2, throughput):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + 8,
            f"{int(val)}",
            ha="center",
            va="bottom",
            fontsize=9,
            color="#333333"
        )

    # -----------------------
    # Layout & export
    # -----------------------
    fig.tight_layout(pad=0.7, w_pad=1.2)
    fig.subplots_adjust(top=0.96, wspace=0.48)
    # fig.legend(
    #     ["Normal", "Under DoS Attack"],
    #     loc="upper center",
    #     ncol=2,
    #     frameon=False,
    #     bbox_to_anchor=(0.5, 1.12),  
    #     fontsize=9
    # )

    # fig.tight_layout(rect=[0, 0, 1, 0.95])  

    fig.savefig("python-fig/attacks-intro.pdf", bbox_inches="tight")
    # fig.savefig("python-fig/attacks-intro.png", dpi=400, bbox_inches="tight")

    plt.close(fig)

def plot_latencies():
    # -----------------------
    # Data (approximated from the reference figure)
    # -----------------------
    nodes = [4, 10, 20, 30, 40, 50, 60, 70, 80, 100]
    iso_latency = [0.7, 3.3, 4.9, 4.1, 6.2, 5.5, 6.0, 7.8, 9.0, 12.1]
    pompe_latency = [0.8, 4.6, 7.0, 7.0, 8.0, 8.6, 9.0, 14.4, 16.0, 22.8]
    hotstuff_latency = [0.0, 0.1, 0.5, 0.6, 0.7, 0.8, 1.1, 2.2, 3.0, 4.2]
    # Approximate sDumbo points visible in the reference figure, restricted to
    # the current x-range of this plot so the global x-axis and ticks stay unchanged.
    sDumbo_nodes = [4, 10, 16, 32, 55, 82, 100]
    sDumbo_values = [0.1, 0.3, 0.7, 2.2, 5.2, 9.3, 13.6]

    # -----------------------
    # Figure
    # -----------------------
    fig, ax = plt.subplots(figsize=(4.02, 2.52))

    # -----------------------
    # Plot lines
    # -----------------------
    ax.plot(
        nodes,
        iso_latency,
        color=ISO_COLOR,
        linewidth=1.5,
        marker="x",
        markersize=5.0,
        markeredgewidth=1.1,
        label="Isotaxis-HS",
        zorder=3,
    )

    ax.plot(
        nodes,
        pompe_latency,
        color=POMPE_COLOR,
        linewidth=1.5,
        marker="D",
        markersize=4.6,
        markerfacecolor="white",
        markeredgewidth=1.0,
        label="Pompe-HS",
        zorder=3,
    )

    ax.plot(
        nodes,
        hotstuff_latency,
        color=HOTSTUFF_COLOR,
        linewidth=1.4,
        marker="^",
        markersize=4.6,
        markerfacecolor=HOTSTUFF_COLOR,
        markeredgewidth=0.8,
        label="HotStuff",
        zorder=3,
    )

    # ax.plot(
    #     sDumbo_nodes,
    #     sDumbo_values,
    #     color=SDUMBO_COLOR,
    #     linewidth=1.4,
    #     linestyle=(0, (3, 2)),
    #     marker="p",
    #     markersize=4.6,
    #     markerfacecolor=SDUMBO_COLOR,
    #     markeredgewidth=0.8,
    #     label="sDumbo (est.)",
    #     zorder=3,
    # )

    # -----------------------
    # Axes, ticks, grid
    # -----------------------
    ax.set_xlabel("# of Nodes", labelpad=5)
    ax.set_ylabel("Latency (s)", labelpad=6)

    ax.set_xlim(0, 105)
    ax.set_ylim(0, 25.5)
    ax.set_xticks(nodes)
    ax.set_yticks([0, 5, 10, 15, 20, 25])

    ax.grid(
        True,
        which="major",
        linestyle="-",
        linewidth=0.5,
        # color="#D9D9D9",
        color=GRID_COLOR,
        alpha=0.8,
        zorder=0,
    )

    ax.spines["left"].set_color(SPINE_COLOR)
    ax.spines["bottom"].set_color(SPINE_COLOR)
    ax.spines["top"].set_color(SPINE_COLOR)
    ax.spines["right"].set_color(SPINE_COLOR)

    ax.tick_params(axis="both", colors="#333333", width=0.8, length=3)

    # -----------------------
    # Legend
    # -----------------------
    _add_inset_legend(
        ax,
        loc="upper left",
        bbox_to_anchor=(0.06, 0.95),
    )

    # -----------------------
    # Layout & export
    # -----------------------
    fig.tight_layout(pad=0.6)

    fig.savefig("python-fig/latency.pdf", bbox_inches="tight")
    # fig.savefig("python-fig/latencies.png", dpi=400, bbox_inches="tight")

    plt.close(fig)


def plot_tps_16():
    isotaxis_points = [
        (17, 2042.0),
        (162, 2991.26),
        (1627, 13918.77),
        (8114, 16729.22),
        (16503, 18121.6),
        (81767, 30350.46),
        (161655, 37132.8),
    ]
    pompe_points = [
        (17, 1202.95),
        (162, 3903.45),
        (1627, 8464.41),
        (8114, 15231.75),
        (12171, 17829.28),
        (16503, 17740.48),
        (81767, 27941.13),
        (161655, 30690.54),
    ]

    _plot_protocol_curves(
        filename="tps-16",
        isotaxis_points=isotaxis_points,
        pompe_points=pompe_points,
        isotaxis_label="Isotaxis-HS-16",
        pompe_label="Pompe-HS-16",
        xlabel=r"Batch Size ($10^4$ txs)",
        ylabel=r"Throughput ($10^4$ tx/s)",
        x_scale=10000.0,
        y_scale=10000.0,
        xlim=(0, 20),
        ylim=(0, 4.0),
        xticks=[0, 5, 10, 15, 20],
        yticks=[0, 1, 2, 3, 4],
        legend_anchor=(0.98, 0.08),
        panel_note=r"$n=16$",
    )


def plot_tps_64():
    isotaxis_points = [
        (17, 1191.38),
        (810, 4108.06),
        (1627, 12948.98),
        (8114, 18866.48),
        (16503, 30301.12),
        (49060, 35734.66),
        (81767, 43007.3),
        (161655, 41755.23),
    ]
    pompe_points = [
        (17, 1069.2),
        (1627, 7324.0),
        (8114, 12651.42),
        (12171, 17621.85),
        (16503, 19947.585),
        (32081, 19409.13),
        (49060, 20492.19),
        (66166, 22598.87),
        (81767, 20557.27),
        (161655, 27412.83),
    ]

    _plot_protocol_curves(
        filename="tps-64",
        isotaxis_points=isotaxis_points,
        pompe_points=pompe_points,
        isotaxis_label="Isotaxis-HS-64",
        pompe_label="Pompe-HS-64",
        xlabel=r"Batch Size ($10^4$ txs)",
        ylabel=r"Throughput ($10^4$ tx/s)",
        x_scale=10000.0,
        y_scale=10000.0,
        xlim=(0, 20),
        ylim=(0, 5.0),
        xticks=[0, 5, 10, 15, 20],
        yticks=[0, 1, 2, 3, 4, 5],
        legend_anchor=(0.98, 0.08),
        panel_note=r"$n=64$",
    )


def plot_tps_100():
    isotaxis_points = [
        (162, 3033.28),
        (1627, 11030.57),
        (3027, 12972.61),
        (8114, 17550.62),
        (16503, 24988.89),
        (20710, 28253.0),
        (24000, 31934.71),
        (32081, 32735.21),
        (49060, 30129.49),
    ]
    pompe_points = [
        (17, 160.2),
        (162, 3132.52),
        (1627, 8740.28),
        (3027, 11846.21),
        (8114, 15866.12),
        (16503, 16443.48),
        (20710, 15648.175),
    ]

    _plot_protocol_curves(
        filename="tps-100",
        isotaxis_points=isotaxis_points,
        pompe_points=pompe_points,
        isotaxis_label="Isotaxis-HS-100",
        pompe_label="Pompe-HS-100",
        xlabel=r"Batch Size ($10^4$ txs)",
        ylabel=r"Throughput ($10^4$ tx/s)",
        x_scale=10000.0,
        y_scale=10000.0,
        xlim=(0, 6),
        ylim=(0, 3.5),
        xticks=[0, 1, 2, 3, 4, 5, 6],
        yticks=[0, 0.5, 1, 1.5, 2, 2.5, 3, 3.5],
        legend_anchor=(0.98, 0.08),
        panel_note=r"$n=100$",
    )


def plot_tradeoff_16():
    isotaxis_points = [
        (2039.16, 7.874),
        (7753.74, 7.49),
        (8765.49, 8.548),
        (12244.9, 10.977),
        (17199.14, 13.655),
        (51069.3, 26.657),
    ]
    pompe_points = [
        (4447.41, 11.197),
        (8514.81, 13.225),
        (15239.91, 14.717),
        (27486.51, 22.0),
        (42335.12, 28.412),
    ]

    _plot_protocol_curves(
        filename="tradeoff-16",
        isotaxis_points=isotaxis_points,
        pompe_points=pompe_points,
        isotaxis_label="Isotaxis-HS-16",
        pompe_label="Pompe-HS-16",
        xlabel=r"Throughput ($10^4$ tx/s)",
        ylabel="Latency (s)",
        x_scale=10000.0,
        y_scale=1.0,
        xlim=(0, 6),
        ylim=(0, 30),
        xticks=[0, 1, 2, 3, 4, 5, 6],
        yticks=[0, 5, 10, 15, 20, 25, 30],
        legend_anchor=(0.98, 0.08),
        panel_note=r"$n=16$",
    )


def plot_tradeoff_64():
    isotaxis_points = [
        (1191.38, 2.402),
        (9032.55, 17.57),
        (12948.98, 23.942),
        (18866.48, 24.573),
        (22353.31, 26.869),
        (27289.85, 28.204),
    ]
    pompe_points = [
        (1069.2, 2.705),
        (8320.44, 19.848),
        (13910.33, 25.965),
        (19409.13, 29.123),
        (22231.83, 28.988),
        (28813.83, 35.616),
    ]

    _plot_protocol_curves(
        filename="tradeoff-64",
        isotaxis_points=isotaxis_points,
        pompe_points=pompe_points,
        isotaxis_label="Isotaxis-HS-64",
        pompe_label="Pompe-HS-64",
        xlabel=r"Throughput ($10^4$ tx/s)",
        ylabel="Latency (s)",
        x_scale=10000.0,
        y_scale=1.0,
        xlim=(0, 3.5),
        ylim=(0, 40),
        xticks=[0, 0.5, 1, 1.5, 2, 2.5, 3, 3.5],
        yticks=[0, 5, 10, 15, 20, 25, 30, 35, 40],
        legend_anchor=(0.98, 0.08),
        panel_note=r"$n=64$",
    )


def plot_tradeoff_100():
    isotaxis_points = [
        (3033.28, 4.928),
        (11030.57, 8.941),
        (12972.61, 12.755),
        (24988.89, 20.895),
        (33234.86, 25.797),
    ]
    pompe_points = [
        (3132.52, 4.746),
        (8740.28, 9.165),
        (11846.21, 15.586),
        (15866.12, 26.251),
    ]

    _plot_protocol_curves(
        filename="tradeoff-100",
        isotaxis_points=isotaxis_points,
        pompe_points=pompe_points,
        isotaxis_label="Isotaxis-HS-100",
        pompe_label="Pompe-HS-100",
        xlabel=r"Throughput ($10^4$ tx/s)",
        ylabel="Latency (s)",
        x_scale=10000.0,
        y_scale=1.0,
        xlim=(0, 3.5),
        ylim=(0, 30),
        xticks=[0, 0.5, 1, 1.5, 2, 2.5, 3, 3.5],
        yticks=[0, 5, 10, 15, 20, 25, 30],
        legend_anchor=(0.98, 0.08),
        panel_note=r"$n=100$",
    )

def plot_attacks_exp():
    protocols = ["Isotaxis", "Pompe"]
    colors = {
        'Isotaxis Normal': '#7DBCC6',   
        'Isotaxis DoS':    '#4A8E9A',   
        'Pompe Normal':    '#C6A07D',   
        'Pompe DoS':       '#9A6E4A',   
    }

    latency_normal = [2.597, 2.03]
    latency_attack = [3.067, 33.474]
    throughput_normal = [1155, 1478]
    throughput_attack = [978, 90]

    normal_colors = [colors["Isotaxis Normal"], colors["Pompe Normal"]]
    attack_colors = [colors["Isotaxis DoS"], colors["Pompe DoS"]]
    plt.rcParams["hatch.linewidth"] = 0.25

    fig, (ax_lat, ax_tps) = plt.subplots(1, 2, figsize=(5.6, 3.15))

    x = [0.06, 0.94]
    bar_width = 0.28
    x_limits = (-0.46, 1.46)
    x_normal = [v - bar_width / 2 for v in x]
    x_attack = [v + bar_width / 2 for v in x]
    latency_change = [
        (attack / normal - 1) * 100
        for normal, attack in zip(latency_normal, latency_attack)
    ]
    throughput_change = [
        (attack / normal - 1) * 100
        for normal, attack in zip(throughput_normal, throughput_attack)
    ]

    def style_axis(ax, grid_axis="y"):
        ax.grid(
            True,
            axis=grid_axis,
            linestyle="-",
            linewidth=0.5,
            color=GRID_COLOR,
            alpha=0.7,
            zorder=0,
        )
        ax.spines["left"].set_color(SPINE_COLOR)
        ax.spines["bottom"].set_color(SPINE_COLOR)
        ax.spines["top"].set_color(SPINE_COLOR)
        ax.spines["right"].set_color(SPINE_COLOR)
        ax.tick_params(axis="both", colors=TICK_COLOR, width=0.8, length=3)

    # Latency subplot
    ax_lat.bar(
        x_normal,
        latency_normal,
        width=bar_width,
        color=normal_colors,
        edgecolor=BAR_EDGE_COLOR,
        linewidth=0.55,
        zorder=3,
    )
    ax_lat.bar(
        x_attack,
        latency_attack,
        width=bar_width,
        color=attack_colors,
        edgecolor=BAR_EDGE_COLOR,
        linewidth=0.55,
        hatch=DOS_HATCH,
        zorder=3,
    )
    style_axis(ax_lat)
    ax_lat.set_ylabel("Latency (s)", labelpad=6)
    ax_lat.set_xlim(*x_limits)
    ax_lat.set_xticks(x)
    ax_lat.set_xticklabels(protocols)
    ax_lat.set_ylim(0, 38)
    ax_lat.set_yticks([0, 5, 10, 15, 20, 25, 30, 35])

    for xpos, val in zip(x_normal, latency_normal):
        ax_lat.text(
            xpos,
            val + 0.18,
            f"{val:.2f}",
            ha="center",
            va="bottom",
            fontsize=7.8,
            color="#444444",
        )
    ax_lat.text(
        x_attack[0],
        latency_attack[0] + 0.18,
        f"{latency_attack[0]:.2f}",
        ha="center",
        va="bottom",
        fontsize=7.8,
        color="#444444",
    )
    ax_lat.text(
        x_normal[1],
        latency_normal[1] + 0.18,
        f"{latency_normal[1]:.2f}",
        ha="center",
        va="bottom",
        fontsize=7.8,
        color="#444444",
    )
    ax_lat.text(
        x_attack[1],
        latency_attack[1] + 0.55,
        f"{latency_attack[1]:.2f}",
        ha="center",
        va="bottom",
        fontsize=7.8,
        color="#444444",
    )
    ax_lat.text(
        x_attack[0] + 0.12,
        latency_attack[0] + 0.15,
        f"+{latency_change[0]:.0f}%",
        ha="left",
        va="bottom",
        fontsize=6,
        color=attack_colors[0],
        fontweight="semibold",
    )
    ax_lat.text(
        x_attack[1] - 0.15,
        latency_attack[1] - 1.4,
        f"+{latency_change[1]:.0f}%",
        ha="right",
        va="center",
        fontsize=6,
        color=attack_colors[1],
        fontweight="semibold",
    )

    # Inset: zoom into the small-latency region to recover the visual gap.
    # Temporarily disabled to compare direct percentage annotations.
    # axins = inset_axes(
    #     ax_lat,
    #     width="47%",
    #     height="42%",
    #     loc="upper left",
    #     borderpad=0.9,
    # )
    # axins.bar(
    #     x_normal,
    #     latency_normal,
    #     width=bar_width,
    #     color=normal_color,
    #     edgecolor="none",
    #     zorder=3,
    # )
    # axins.bar(
    #     x_attack,
    #     latency_attack,
    #     width=bar_width,
    #     color=attack_color,
    #     edgecolor="none",
    #     zorder=3,
    # )
    # axins.set_xlim(-0.45, 1.45)
    # axins.set_ylim(1.8, 3.3)
    # axins.set_xticks(x)
    # axins.set_xticklabels(["Iso", "Pom"])
    # axins.set_yticks([2.0, 2.5, 3.0])
    # axins.grid(
    #     True,
    #     axis="y",
    #     linestyle="-",
    #     linewidth=0.45,
    #     color=GRID_COLOR,
    #     alpha=0.65,
    #     zorder=0,
    # )
    # for side in ("left", "bottom", "top", "right"):
    #     axins.spines[side].set_visible(True)
    #     axins.spines[side].set_color("#B5B5B5")
    #     axins.spines[side].set_linewidth(0.6)
    # axins.yaxis.tick_right()
    # axins.tick_params(axis="x", colors=TICK_COLOR, width=0.6, length=2, labelsize=7.2)
    # axins.tick_params(
    #     axis="y",
    #     colors=TICK_COLOR,
    #     width=0.6,
    #     length=2,
    #     labelsize=7.2,
    #     left=False,
    #     labelleft=False,
    #     right=True,
    #     labelright=True,
    #     pad=1.5,
    # )
    # axins.set_title("Zoom", fontsize=7.4, color=TICK_COLOR, pad=1.5)

    # Throughput subplot
    ax_tps.bar(
        x_normal,
        throughput_normal,
        width=bar_width,
        color=normal_colors,
        edgecolor=BAR_EDGE_COLOR,
        linewidth=0.55,
        zorder=3,
    )
    ax_tps.bar(
        x_attack,
        throughput_attack,
        width=bar_width,
        color=attack_colors,
        edgecolor=BAR_EDGE_COLOR,
        linewidth=0.55,
        hatch=DOS_HATCH,
        zorder=3,
    )
    style_axis(ax_tps)
    ax_tps.set_ylabel("Throughput (tx/s)", labelpad=6)
    ax_tps.set_xlim(*x_limits)
    ax_tps.set_xticks(x)
    ax_tps.set_xticklabels(protocols)
    ax_tps.set_ylim(0, 1650)
    ax_tps.set_yticks([0, 400, 800, 1200, 1600])
    ax_lat.tick_params(axis="x", labelsize=9.3)
    ax_tps.tick_params(axis="x", labelsize=9.3)


    for xpos, val in zip(x_normal, throughput_normal):
        ax_tps.text(
            xpos,
            val + 28,
            f"{int(val)}",
            ha="center",
            va="bottom",
            fontsize=7.8,
            color="#444444",
        )
    for xpos, val in zip(x_attack, throughput_attack):
        ax_tps.text(
            xpos,
            val + 20,
            f"{int(val)}",
            ha="center",
            va="bottom",
            fontsize=7.8,
            color="#444444",
        )
    ax_tps.text(
        x_attack[0] + 0.12,
        throughput_attack[0] ,
        f"{throughput_change[0]:.0f}%",
        ha="left",
        va="bottom",
        fontsize=6,
        color=attack_colors[0],
        fontweight="semibold",
    )
    ax_tps.text(
        x_attack[1] + 0.32,
        throughput_attack[1]+10,
        f"{throughput_change[1]:.0f}%",
        ha="right",
        va="bottom",
        fontsize=6,
        color=attack_colors[1],
        fontweight="semibold",
    )

    protocol_handles = [
        Patch(
            facecolor=colors["Isotaxis Normal"],
            edgecolor=BAR_EDGE_COLOR,
            linewidth=0.55,
            label="Isotaxis",
        ),
        Patch(
            facecolor=colors["Pompe Normal"],
            edgecolor=BAR_EDGE_COLOR,
            linewidth=0.55,
            label="Pompe",
        ),
    ]
    fig.legend(
        handles=protocol_handles,
        loc="upper center",
        bbox_to_anchor=(0.35, 0.945),
        ncol=2,
        frameon=False,
        handlelength=1.0,
        handletextpad=0.35,
        columnspacing=1.0,
        fontsize=8.2,
    )
    fig.text(
        0.77,
        0.926,
        "Normal (solid), DoS attack (hatched)",
        ha="center",
        va="top",
        fontsize=7.8,
        # color="#000000",
    )

    fig.subplots_adjust(top=0.84, bottom=0.14, left=0.09, right=0.98, wspace=0.38)
    fig.savefig("python-fig/attacks-exp.pdf", bbox_inches="tight")
    plt.close(fig)

# -------- 主函数 --------

if __name__ == "__main__":

    setup_style()

    plot_tps_16()   # Fig. 6(1)
    plot_tps_64()   # Fig. 6(2)
    plot_tps_100()  # Fig. 6(3)
    plot_tradeoff_16()  # Fig. 6(4)
    plot_tradeoff_64()  # Fig. 6(5)
    plot_tradeoff_100() # Fig. 6(6)

    plot_throughput_latency_intro()    # Fig.3  
    plot_latencies()    # Fig. 5
    plot_attacks_intro()    #Fig.2 
    plot_attacks_exp()  # Fig.7
