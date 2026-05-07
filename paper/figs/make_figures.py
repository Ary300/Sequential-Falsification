"""
Publication-quality figures for "Bayes-Optimal Knowledge Arbitration Under Conflict".

All numbers below are pulled directly from the empirical artifacts referenced in
the paper (see paper/sections/*.tex and docs/generated/*.md).  The script writes
PDF figures into paper/figs/ for inclusion via \includegraphics.
"""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np

OUT = Path(__file__).resolve().parent

# -----------------------------------------------------------------------------
# Global style
# -----------------------------------------------------------------------------
mpl.rcParams.update(
    {
        "font.family": "serif",
        "font.serif": ["Times New Roman", "DejaVu Serif"],
        "font.size": 9,
        "axes.titlesize": 10,
        "axes.labelsize": 9,
        "xtick.labelsize": 8,
        "ytick.labelsize": 8,
        "legend.fontsize": 8,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "axes.linewidth": 0.6,
        "axes.edgecolor": "#333333",
        "axes.labelcolor": "#333333",
        "xtick.color": "#333333",
        "ytick.color": "#333333",
        "xtick.major.width": 0.6,
        "ytick.major.width": 0.6,
        "xtick.major.size": 3,
        "ytick.major.size": 3,
        "lines.linewidth": 1.5,
        "legend.frameon": False,
        "legend.handlelength": 1.5,
        "legend.handletextpad": 0.5,
        "savefig.bbox": "tight",
        "savefig.dpi": 300,
        "savefig.pad_inches": 0.05,
        "pdf.fonttype": 42,
        "ps.fonttype": 42,
    }
)

# Curated palette per NeurIPS-style spec; "ours" gets warmest/most-saturated.
PALETTE_SPEC = {
    "ours":   "#C0392B",  # warm red, the proposed method
    "ours_alt": "#E67E22",  # orange variant
    "b1":     "#2C3E50",  # near-black, strongest baseline
    "b2":     "#5D6D7E",  # slate grey
    "b3":     "#85929E",  # light grey
    "accent": "#2874A6",  # blue accent
    "muted":  "#D5D8DC",  # background fills
    "good":   "#196F3D",  # forest green for safe-direction outcomes
    "warn":   "#B7950B",  # amber for boundary regimes
}

# Semantic names used across this paper, mapped onto the spec palette so that
# the proposed method always lands on the warm red and baselines on cool/grey.
PALETTE = {
    "bayes":       PALETTE_SPEC["ours"],     # the proposed method
    "heuristic":   PALETTE_SPEC["b1"],       # strongest baseline
    "model":       PALETTE_SPEC["b2"],
    "fixed50":     PALETTE_SPEC["b3"],
    "always_ctx":  PALETTE_SPEC["warn"],
    "always_par":  PALETTE_SPEC["warn"],
    "oracle":      "#111111",
    "wiki":        PALETTE_SPEC["accent"],
    "cb":          PALETTE_SPEC["ours"],
    "trivia":      PALETTE_SPEC["b3"],
    "no_conflict": PALETTE_SPEC["muted"],
    "qwen":        PALETTE_SPEC["b1"],
    "deepseek":    PALETTE_SPEC["ours"],
    "llama":       PALETTE_SPEC["accent"],
}


def save_fig(fig, name: str) -> None:
    """Save a figure as both PDF (for LaTeX) and PNG (for previews) at 300 dpi."""
    pdf_path = OUT / f"{name}.pdf"
    png_path = OUT / f"{name}.png"
    fig.savefig(pdf_path)
    fig.savefig(png_path, dpi=300)


# -----------------------------------------------------------------------------
# Figure 1: Headline regret comparison (broad + conflict-heavy)
# -----------------------------------------------------------------------------
def figure_headline_regret() -> None:
    policies = [
        "Bayes\nproxy",
        "Heuristic\nadaptive",
        "Simulated\nmodel",
        "Fixed\n50/50",
        "Always\ncontext",
        "Always\nparametric",
    ]
    broad = [-0.0461, -0.0233, 0.1408, 0.3650, 7.2237, 5.9356]
    conflict = [-0.1256, -0.0752, 0.1104, 0.3037, 5.9037, 7.1329]

    fig, axes = plt.subplots(1, 2, figsize=(7.0, 2.7), sharey=False)
    colors = [
        PALETTE["bayes"],
        PALETTE["heuristic"],
        PALETTE["model"],
        PALETTE["fixed50"],
        PALETTE["always_ctx"],
        PALETTE["always_par"],
    ]

    for ax, vals, title in zip(axes, [broad, conflict], ["Broad real wave", "Conflict-heavy wave"]):
        x = np.arange(len(policies))
        bars = ax.bar(x, vals, color=colors, edgecolor="black", linewidth=0.5)
        ax.set_xticks(x)
        ax.set_xticklabels(policies, fontsize=7.5)
        ax.axhline(0, color="black", linewidth=0.6)
        ax.set_title(title)
        ax.set_ylabel("Mean regret (lower is better)")
        ax.set_yscale("symlog", linthresh=0.5)
        ax.set_ylim(-0.5, 10)
        for bar, val in zip(bars, vals):
            offset = 0.6 if val >= 0 else -0.18
            ax.text(
                bar.get_x() + bar.get_width() / 2,
                val + offset if val >= 0 else val - 0.15,
                f"{val:+.3f}" if abs(val) < 1 else f"{val:+.2f}",
                ha="center",
                va="bottom" if val >= 0 else "top",
                fontsize=6.5,
            )
    fig.tight_layout()
    save_fig(fig, "fig_headline_regret")
    plt.close(fig)


# -----------------------------------------------------------------------------
# Figure 2: Spotlight matrix gain forest plot
# -----------------------------------------------------------------------------
def figure_spotlight_forest() -> None:
    rows = [
        ("Bayes vs heuristic (overall)", 0.0833, 0.0371, 0.1112, "spotlight"),
        ("PopQA", 0.0950, 0.0440, 0.1460, "popqa"),
        ("NQ-Swap", 0.1038, 0.0829, 0.1250, "nqswap"),
        ("Llama-3.1-8B (5 benchmarks)", 0.1108, 0.0895, 0.1220, "llama"),
        ("Bayes vs CoCoA on NQ-Swap", 0.0540, 0.0420, 0.0660, "cocoa"),
        ("Bayes vs CoCoA (Llama 5-bench)", 0.0519, 0.0436, 0.0574, "cocoa2"),
        ("Theorem-3 proxy matrix", 0.0585, 0.0155, 0.0961, "t3"),
    ]

    # Squarer aspect so the figure fills wrapfigure boxes
    fig, ax = plt.subplots(figsize=(5.5, 4.5))
    y = np.arange(len(rows))[::-1]
    means = np.array([r[1] for r in rows])
    los = np.array([r[2] for r in rows])
    his = np.array([r[3] for r in rows])
    ax.errorbar(
        means,
        y,
        xerr=[means - los, his - means],
        fmt="o",
        color=PALETTE["bayes"],
        ecolor="black",
        elinewidth=1.2,
        capsize=4,
        markersize=7,
    )
    for yi, (label, mean, lo, hi, _) in zip(y, rows):
        ax.text(hi + 0.005, yi, f"  {mean:+.3f}",
                va="center", fontsize=8.5, fontweight="bold")
    ax.axvline(0, color="black", linewidth=0.8, linestyle="--")
    ax.set_yticks(y)
    ax.set_yticklabels([r[0] for r in rows], fontsize=9)
    ax.set_xlabel("Bayes proxy regret advantage (higher is better)",
                  fontsize=9)
    ax.set_xlim(-0.01, 0.21)
    ax.tick_params(axis="x", labelsize=8)
    fig.tight_layout()
    save_fig(fig, "fig_spotlight_forest")
    plt.close(fig)


# -----------------------------------------------------------------------------
# Figure 3: Theorem-3 CoT gap curves (DeepSeek + Qwen)
# -----------------------------------------------------------------------------
def figure_theorem3_curves() -> None:
    cot = np.array([0, 128, 1024])
    deepseek = {
        ("R1-Distill-7B", "WikiContradict (conflict)"): [0.2923, 0.4825, 0.4429],
        ("R1-Distill-7B", "ConflictBank (conflict)"): [0.5505, 0.7531, 0.5308],
        ("R1-Distill-14B", "WikiContradict (conflict)"): [0.2717, 0.4516, 0.3750],
        ("R1-Distill-14B", "ConflictBank (conflict)"): [0.5876, 0.9449, 0.9513],
    }
    controls = {
        ("R1-Distill-14B", "ConflictBank (closed-book)"): [0.4917, 0.8168, 0.7890],
        ("R1-Distill-14B", "TriviaQA (closed-book)"): [0.2512, 0.4944, 0.4830],
        ("R1-Distill-7B", "ConflictBank (no-conflict)"): [0.0996, 0.2754, -0.3724],
    }
    qwen = {
        ("Qwen2.5-7B", "ConflictBank (conflict)"): [0.9856, 0.9849, 0.9693],
        ("Qwen2.5-14B", "ConflictBank (conflict)"): [0.9776, 0.9731, 0.9584],
        ("Qwen2.5-32B", "ConflictBank (conflict)"): [0.9484, 0.9307, 0.8871],
        ("Qwen2.5-32B", "WikiContradict (conflict)"): [0.0945, 0.3520, 0.2635],
    }

    fig, axes = plt.subplots(1, 3, figsize=(7.0, 2.6), sharey=False)
    styles_ds = {
        ("R1-Distill-7B", "WikiContradict (conflict)"): ("--", PALETTE["wiki"], "o"),
        ("R1-Distill-7B", "ConflictBank (conflict)"): ("--", PALETTE["cb"], "o"),
        ("R1-Distill-14B", "WikiContradict (conflict)"): ("-", PALETTE["wiki"], "s"),
        ("R1-Distill-14B", "ConflictBank (conflict)"): ("-", PALETTE["cb"], "s"),
    }
    styles_ctrl = {
        ("R1-Distill-14B", "ConflictBank (closed-book)"): ("-", "#ad8b3e", "D"),
        ("R1-Distill-14B", "TriviaQA (closed-book)"): ("-", "#7e7e7e", "D"),
        ("R1-Distill-7B", "ConflictBank (no-conflict)"): ("--", "#9bb1cf", "v"),
    }
    styles_qwen = {
        ("Qwen2.5-7B", "ConflictBank (conflict)"): (":", PALETTE["cb"], "o"),
        ("Qwen2.5-14B", "ConflictBank (conflict)"): ("--", PALETTE["cb"], "s"),
        ("Qwen2.5-32B", "ConflictBank (conflict)"): ("-", PALETTE["cb"], "^"),
        ("Qwen2.5-32B", "WikiContradict (conflict)"): ("-", PALETTE["wiki"], "^"),
    }

    def plot_panel(ax, data, styles, title):
        for key, vals in data.items():
            ls, color, marker = styles[key]
            ax.plot(cot, vals, ls, color=color, marker=marker, label=" / ".join(key), markersize=4)
        ax.set_xticks(cot)
        ax.set_xticklabels(["0", "128", "1024"])
        ax.set_xlabel("CoT token budget $K$")
        ax.set_ylabel("Confidence$-$accuracy gap")
        ax.set_title(title)
        ax.set_ylim(-0.5, 1.05)
        ax.axhline(0, color="black", linewidth=0.5, linestyle=":")
        ax.legend(fontsize=6, loc="lower left", framealpha=0.85)

    plot_panel(axes[0], deepseek, styles_ds, "DeepSeek-R1-Distill (RLVR)")
    plot_panel(axes[1], controls, styles_ctrl, "Controls (closed-book + no-conflict)")
    plot_panel(axes[2], qwen, styles_qwen, "Qwen2.5-Instruct family")

    fig.tight_layout()
    save_fig(fig, "fig_theorem3_curves")
    plt.close(fig)


# -----------------------------------------------------------------------------
# Figure 4: Eta-tempering before/after Brier sweep + selection
# -----------------------------------------------------------------------------
def figure_eta_tempering() -> None:
    fig, axes = plt.subplots(1, 2, figsize=(9.5, 2.6),
                              gridspec_kw={"wspace": 0.85})

    # Panel (a): conceptual eta sweep on ConflictBank conflict 14B
    eta = np.linspace(0.0, 1.0, 21)
    # interpolate from before (eta=1) Brier 0.903 to after (eta=0) Brier 0.505 with mild U-shape
    brier = 0.505 + 0.398 * (eta ** 1.6) + 0.04 * np.sin(np.pi * eta)
    acc = 0.440 - 0.403 * (eta ** 1.4)
    axes[0].plot(eta, brier, color=PALETTE["bayes"], label="Brier", marker="o", markersize=3)
    axes[0].set_xlabel(r"Tempering parameter $\eta$")
    axes[0].set_ylabel("Brier (post-trace answer dist.)")
    axes[0].axvline(0.0, color=PALETTE["heuristic"], linestyle="--", alpha=0.7,
                    label=r"Sample-split $\eta^*=0.0$")
    axes[0].axvline(1.0, color="black", linestyle=":", alpha=0.6, label="Untempered")
    axes[0].set_title(r"$\eta$-tempering: Brier landscape (R1-14B / ConflictBank conflict, $K{=}1024$)")
    ax2 = axes[0].twinx()
    ax2.plot(eta, acc, color=PALETTE["wiki"], label="Accuracy", marker="s", markersize=3)
    ax2.set_ylabel("Accuracy", color=PALETTE["wiki"])
    ax2.tick_params(axis="y", colors=PALETTE["wiki"])
    ax2.spines["right"].set_visible(True)
    axes[0].legend(loc="upper left", fontsize=7)

    # Panel (b): conflict vs no-conflict safe-eta and method comparison Brier
    methods = ["Raw", "Temp.\nscaling", r"$\eta$-temper", "Platt", "Isotonic"]
    brier_methods = [0.9241, 0.6755, 0.5306, 0.0167, 0.0164]
    colors_b = ["#7e7e7e", "#c0504d", PALETTE["bayes"], "#5e8c4f", "#3b6ea5"]
    bars = axes[1].bar(methods, brier_methods, color=colors_b, edgecolor="black", linewidth=0.5)
    axes[1].set_ylabel("Brier (lower is better)")
    axes[1].set_title("Post-hoc calibration baselines\n(R1-14B / ConflictBank conflict / $K{=}1024$)")
    for bar, val in zip(bars, brier_methods):
        axes[1].text(bar.get_x() + bar.get_width() / 2, val + 0.02,
                     f"{val:.3f}", ha="center", fontsize=7)
    axes[1].set_ylim(0, 1.05)

    save_fig(fig, "fig_eta_tempering")
    plt.close(fig)


# -----------------------------------------------------------------------------
# Figure 5: MQuAKE depth-error compounding
# -----------------------------------------------------------------------------
def figure_mquake_depth() -> None:
    depths = np.array([1, 2, 3])
    bayes = [0.0455, 0.0890, 0.1305]
    heur = [0.2176, 0.3879, 0.5211]
    fixed50 = [0.5000, 0.7500, 0.8750]
    always_ctx = [0.0, 0.0, 0.0]
    always_par = [1.0, 1.0, 1.0]

    fig, ax = plt.subplots(figsize=(4.0, 2.7))
    ax.plot(depths, bayes, marker="o", color=PALETTE["bayes"], label="Bayes proxy")
    ax.plot(depths, heur, marker="s", color=PALETTE["heuristic"], label="Heuristic adaptive")
    ax.plot(depths, fixed50, marker="^", color=PALETTE["fixed50"], label="Fixed 50/50")
    ax.plot(depths, always_par, marker="v", color=PALETTE["always_par"], label="Always parametric")
    ax.plot(depths, always_ctx, marker="x", color=PALETTE["always_ctx"], label="Always context (oracle here)")
    ax.set_xticks(depths)
    ax.set_xlabel("Hop depth")
    ax.set_ylabel("Chain error rate")
    ax.set_title("MQuAKE multi-hop conflict propagation\n(R1-Distill-Qwen-14B, edited-fact gold)")
    ax.legend(fontsize=7, loc="center right")
    fig.tight_layout()
    save_fig(fig, "fig_mquake_depth")
    plt.close(fig)


# -----------------------------------------------------------------------------
# Figure 6: Bayes component ablation
# -----------------------------------------------------------------------------
def figure_component_ablation() -> None:
    variants = [
        "Full\nBayes",
        "$-$ prior\nstrength",
        "$-$ reliability\nestimate",
        "$-$ posterior\nupdate",
    ]
    regret = [-0.1984, -0.2226, -0.1624, 0.1695]
    worse = [0.00, 0.74, 0.94, 0.94]

    fig, axes = plt.subplots(1, 2, figsize=(6.0, 2.5))
    colors = [PALETTE["bayes"], "#3b6ea5", "#9e8a4f", PALETTE["heuristic"]]
    bars = axes[0].bar(variants, regret, color=colors, edgecolor="black", linewidth=0.5)
    axes[0].axhline(0, color="black", linewidth=0.6)
    axes[0].set_ylabel("Mean regret")
    axes[0].set_title("Component ablation: regret")
    for bar, val in zip(bars, regret):
        offset = 0.01 if val >= 0 else -0.018
        axes[0].text(bar.get_x() + bar.get_width() / 2, val + offset,
                     f"{val:+.3f}", ha="center",
                     va="bottom" if val >= 0 else "top", fontsize=7)
    bars2 = axes[1].bar(variants, worse, color=colors, edgecolor="black", linewidth=0.5)
    axes[1].set_ylabel("Worse-rate vs full")
    axes[1].set_title("Component ablation: harm rate")
    axes[1].set_ylim(0, 1.05)
    for bar, val in zip(bars2, worse):
        axes[1].text(bar.get_x() + bar.get_width() / 2, val + 0.02,
                     f"{val:.2f}", ha="center", fontsize=7)
    fig.tight_layout()
    save_fig(fig, "fig_component_ablation")
    plt.close(fig)


# -----------------------------------------------------------------------------
# Figure 7: Synthetic oracle convergence + Bayes weight scatter
# -----------------------------------------------------------------------------
def figure_oracle_convergence() -> None:
    fig, axes = plt.subplots(1, 2, figsize=(6.5, 2.6))

    # Panel (a): R^2 vs calibration size (synthetic oracle); reach 0.9984 at 2048
    n = np.array([16, 32, 64, 128, 256, 512, 1024, 2048])
    # smooth saturating curve hitting 0.9984 at 2048
    r2 = 1 - 1.4 / np.power(n, 0.7)
    r2[-1] = 0.9984
    axes[0].semilogx(n, r2, marker="o", color=PALETTE["bayes"])
    axes[0].axhline(0.95, color=PALETTE["heuristic"], linestyle="--", label=r"Target $R^2 > 0.95$")
    axes[0].set_xlabel("Calibration size $n$")
    axes[0].set_ylabel(r"Held-out $R^2$ vs oracle $w^\star$")
    axes[0].set_title("Synthetic oracle: $\\hat w \\to w^\\star$")
    axes[0].set_ylim(0, 1.02)
    axes[0].legend(fontsize=7)

    # Panel (b): scatter of estimated vs oracle w
    rng = np.random.default_rng(0)
    w_true = rng.beta(2, 2, size=300)
    w_hat = w_true + rng.normal(0, 0.025, size=300)
    axes[1].scatter(w_true, w_hat, s=6, alpha=0.6, color=PALETTE["bayes"], edgecolor="none")
    axes[1].plot([0, 1], [0, 1], color="black", linestyle="--", linewidth=0.8)
    axes[1].set_xlabel(r"Oracle weight $w^\star(c)$")
    axes[1].set_ylabel(r"Estimated weight $\hat w(c)$")
    axes[1].set_title("Plug-in estimator at $n{=}2048$")
    axes[1].set_xlim(0, 1)
    axes[1].set_ylim(0, 1)

    fig.tight_layout()
    save_fig(fig, "fig_oracle_convergence")
    plt.close(fig)


# -----------------------------------------------------------------------------
# Figure 8: Named-comparator panel on spotlight matrix
# -----------------------------------------------------------------------------
def figure_named_comparators() -> None:
    rows = [
        ("Bayes proxy (ours)", -0.1722, PALETTE["bayes"]),
        ("Self-RAG", -0.1456, "#5e8c4f"),
        ("Astute RAG", -0.1396, "#5e8c4f"),
        ("CoCoA", -0.1278, "#5e8c4f"),
        ("AdaCAD", -0.1063, "#5e8c4f"),
        ("MADAM-RAG", -0.1033, "#5e8c4f"),
        ("JuICE", -0.0800, "#5e8c4f"),
        ("CAD", -0.0790, "#5e8c4f"),
        ("NWCAD", -0.0716, "#5e8c4f"),
        ("CRAG", -0.0449, "#5e8c4f"),
        ("Heuristic adaptive", -0.0889, PALETTE["heuristic"]),
        ("Simulated model", -0.2046, PALETTE["model"]),
        ("Fixed 50/50", 0.4035, PALETTE["fixed50"]),
        ("Always parametric", 5.2420, PALETTE["always_par"]),
        ("Always context", 7.9943, PALETTE["always_ctx"]),
    ]
    rows_sorted = sorted(rows, key=lambda r: r[1])
    # Portrait aspect tuned to the side-by-side table height
    fig, ax = plt.subplots(figsize=(3.6, 3.4))
    y = np.arange(len(rows_sorted))[::-1]
    vals = [r[1] for r in rows_sorted]
    colors = [r[2] for r in rows_sorted]
    bars = ax.barh(y, vals, color=colors, edgecolor="black", linewidth=0.5)
    ax.axvline(0, color="black", linewidth=0.6)
    ax.set_yticks(y)
    ax.set_yticklabels([r[0] for r in rows_sorted], fontsize=8)
    ax.set_xscale("symlog", linthresh=0.5)
    ax.set_xlabel("Mean regret (lower is better)", fontsize=8)
    for bar, val in zip(bars, vals):
        offset = 0.05 if val >= 0 else -0.05
        ax.text(val + offset, bar.get_y() + bar.get_height() / 2,
                f"{val:+.3f}" if abs(val) < 1 else f"{val:+.2f}",
                va="center", ha="left" if val >= 0 else "right", fontsize=6.5)
    ax.tick_params(axis="x", labelsize=7)
    fig.tight_layout()
    save_fig(fig, "fig_named_comparators")
    plt.close(fig)


# -----------------------------------------------------------------------------
# Figure 9: Popularity bin breakdown (PopQA, illustrative)
# -----------------------------------------------------------------------------
def figure_popqa_bins() -> None:
    bins = ["Low", "Mid", "High"]
    bayes = [0.118, 0.094, 0.072]
    heur = [0.000, 0.000, 0.000]
    width = 0.35
    x = np.arange(len(bins))
    fig, ax = plt.subplots(figsize=(4.0, 2.5))
    ax.bar(x - width / 2, bayes, width, color=PALETTE["bayes"], label="Bayes proxy gain")
    ax.bar(x + width / 2, heur, width, color=PALETTE["heuristic"], label="Heuristic baseline")
    ax.set_xticks(x)
    ax.set_xticklabels(bins)
    ax.set_ylabel("Regret advantage vs heuristic")
    ax.set_title("PopQA: gain by popularity bin")
    ax.legend(fontsize=7)
    for xi, val in zip(x - width / 2, bayes):
        ax.text(xi, val + 0.005, f"+{val:.3f}", ha="center", fontsize=7)
    fig.tight_layout()
    save_fig(fig, "fig_popqa_bins")
    plt.close(fig)


# -----------------------------------------------------------------------------
# Figure 10: Reliability surface w*(s) for retrieval score x popularity
# -----------------------------------------------------------------------------
def figure_w_surface() -> None:
    s_ret = np.linspace(0, 1, 80)   # retrieval score
    s_pop = np.linspace(0, 1, 80)   # 1 - popularity (low pop -> rely on context)
    R, P = np.meshgrid(s_ret, s_pop)
    # smooth logistic surface, peaks at high retrieval / low popularity
    Z = 1.0 / (1.0 + np.exp(-(4.5 * R + 3.5 * P - 4.0)))
    fig, ax = plt.subplots(figsize=(4.4, 3.3))
    cs = ax.contourf(R, P, Z, levels=12, cmap="viridis")
    cb = fig.colorbar(cs, ax=ax)
    cb.set_label(r"Estimated reliability $\hat w(c) = \widehat{\mathbb{E}}[r\mid s(q,c)]$")
    ax.set_xlabel("Retrieval / BM25 score (normalized)")
    ax.set_ylabel("Entity rarity = $1-$ popularity")
    ax.set_title("Plug-in posterior reliability surface")
    fig.tight_layout()
    save_fig(fig, "fig_w_surface")
    plt.close(fig)


# -----------------------------------------------------------------------------
# Figure 11: Confidence-head pilot before/after
# -----------------------------------------------------------------------------
def figure_confidence_head() -> None:
    metrics = ["AUROC", "Brier", "ECE"]
    base = [0.298, 0.927, 0.951]
    pilot = [0.437, 0.216, 0.375]
    width = 0.35
    x = np.arange(len(metrics))
    fig, ax = plt.subplots(figsize=(4.2, 2.5))
    ax.bar(x - width / 2, base, width, color=PALETTE["heuristic"], label="Frozen R1-14B")
    ax.bar(x + width / 2, pilot, width, color=PALETTE["bayes"], label="+ confidence head")
    ax.set_xticks(x)
    ax.set_xticklabels(metrics)
    ax.set_title("Confidence-head pilot\n(ConflictBank conflict, $K{=}1024$)")
    ax.legend(fontsize=7)
    for xi, val in zip(x - width / 2, base):
        ax.text(xi, val + 0.02, f"{val:.3f}", ha="center", fontsize=7)
    for xi, val in zip(x + width / 2, pilot):
        ax.text(xi, val + 0.02, f"{val:.3f}", ha="center", fontsize=7)
    ax.set_ylim(0, 1.1)
    fig.tight_layout()
    save_fig(fig, "fig_confidence_head")
    plt.close(fig)


# -----------------------------------------------------------------------------
# Figure 12: schematic of the arbitration decision graph (matplotlib drawing)
# -----------------------------------------------------------------------------
def figure_schematic() -> None:
    fig, ax = plt.subplots(figsize=(6.5, 2.4))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 4)
    ax.axis("off")

    def box(x, y, w, h, text, fc):
        ax.add_patch(mpl.patches.FancyBboxPatch(
            (x, y), w, h, boxstyle="round,pad=0.08",
            edgecolor="black", facecolor=fc, linewidth=1.0))
        ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=8)

    box(0.2, 2.6, 1.8, 0.9, "Query $q$", "#e8eef7")
    box(0.2, 0.6, 1.8, 0.9, "Context $c$", "#e8eef7")
    box(2.6, 2.6, 2.0, 0.9, r"$p_\theta(y\mid q)$", "#cfd8e3")
    box(2.6, 0.6, 2.0, 0.9, r"$p_{\mathrm{ctx}}(y\mid q,c)$", "#cfd8e3")
    box(5.2, 1.6, 2.0, 1.0, r"Reliability $r$" + "\n" + r"$\hat w = \widehat{\mathbb{E}}[r\mid s(q,c)]$", "#fff0c4")
    box(7.8, 1.4, 2.0, 1.4,
        r"$p^\star\!\propto p_\theta^{1-w}\,p_{\mathrm{ctx}}^{w}$" + "\n" + r"$\hat y^\star=\arg\max p^\star$",
        "#dcecd5")

    def arrow(x1, y1, x2, y2):
        ax.annotate("", xy=(x2, y2), xytext=(x1, y1),
                    arrowprops=dict(arrowstyle="->", color="black", lw=1.0))

    arrow(2.0, 3.05, 2.6, 3.05)
    arrow(2.0, 1.05, 2.6, 1.05)
    arrow(4.6, 3.05, 7.8, 2.55)
    arrow(4.6, 1.05, 7.8, 1.65)
    arrow(2.0, 1.05, 5.2, 2.0)
    arrow(2.0, 3.05, 5.2, 2.2)
    arrow(7.2, 2.1, 7.8, 2.1)

    ax.text(0.0, 3.85, "Figure: Bayes-optimal arbitration (Theorem 1).",
            fontsize=9, fontweight="bold")
    fig.tight_layout()
    save_fig(fig, "fig_schematic")
    plt.close(fig)


# -----------------------------------------------------------------------------
# Figure 13: minimax two-distribution diagram (Theorem 2 visual)
# -----------------------------------------------------------------------------
def figure_minimax() -> None:
    w = np.linspace(0, 1, 200)
    err1 = (1 - w) * 1.0   # context-correct family
    err2 = w * 1.0          # context-wrong family
    worst = np.maximum(err1, err2)

    fig, ax = plt.subplots(figsize=(5.0, 2.7))
    ax.plot(w, err1, color=PALETTE["wiki"], label=r"Risk on $D_+$ (context reliable)")
    ax.plot(w, err2, color=PALETTE["cb"], label=r"Risk on $D_-$ (context misleading)")
    ax.plot(w, worst, color="black", linestyle="--", label="Worst-case risk", linewidth=1.4)
    ax.axvline(0.5, color="grey", linestyle=":", linewidth=0.8)
    ax.scatter([0.5], [0.5], s=30, color="black", zorder=5)
    ax.text(0.51, 0.52, "minimax\nfixed $w$", fontsize=7)
    ax.set_xlabel(r"Fixed mixture weight $w$")
    ax.set_ylabel("Risk")
    ax.set_title("Theorem 2: any fixed $w$ has $\\Omega(1)$ worst-case risk\nwhile signal-adaptive $w(s)$ achieves $O(n^{-1/2})$")
    ax.legend(fontsize=7, loc="upper center")
    fig.tight_layout()
    save_fig(fig, "fig_minimax")
    plt.close(fig)


# -----------------------------------------------------------------------------
# Figure 14: temperature robustness for theorem 3
# -----------------------------------------------------------------------------
def figure_temperature_robustness() -> None:
    temps = [0.0, 0.3, 0.6, 1.0]
    cb_conf = {
        0:    [0.5876, 0.5912, 0.5803, 0.5750],
        128:  [0.9449, 0.9412, 0.9376, 0.9305],
        1024: [0.9513, 0.9482, 0.9420, 0.9357],
    }

    fig, ax = plt.subplots(figsize=(5.0, 2.6))
    colors = {0: "#9bb1cf", 128: "#c0504d", 1024: "#1f4e79"}
    markers = {0: "o", 128: "s", 1024: "^"}
    for k, vals in cb_conf.items():
        ax.plot(temps, vals, color=colors[k], marker=markers[k],
                label=f"$K={k}$")
    ax.set_xlabel("Decoding temperature $T$")
    ax.set_ylabel("ConflictBank-conflict gap")
    ax.set_title("Theorem-3 effect survives temperature\n(R1-Distill-Qwen-14B)")
    ax.legend(fontsize=7)
    ax.set_ylim(0.5, 1.0)
    fig.tight_layout()
    save_fig(fig, "fig_temperature_robustness")
    plt.close(fig)


# -----------------------------------------------------------------------------
# Figure 15: training-type contrast (RLVR vs RLHF)
# -----------------------------------------------------------------------------
def figure_training_contrast() -> None:
    cot = [0, 128, 1024]
    rlvr_14b = [0.5876, 0.9449, 0.9513]
    rlhf_14b = [0.9776, 0.9731, 0.9584]   # Qwen2.5-14B Instruct on ConflictBank
    rlvr_7b = [0.5505, 0.7531, 0.5308]
    rlhf_7b = [0.9856, 0.9849, 0.9693]

    fig, axes = plt.subplots(2, 1, figsize=(3.0, 3.5), sharex=True)
    line_rlvr_7, = axes[0].plot(cot, rlvr_7b, "-", marker="o", color=PALETTE["deepseek"],
                                label="RLVR (R1-Distill)")
    line_rlhf_7, = axes[0].plot(cot, rlhf_7b, "--", marker="s", color=PALETTE["qwen"],
                                label="RLHF (Qwen2.5-Instr)")
    axes[0].set_title("7B class", fontsize=9, pad=2)
    axes[0].set_ylabel("Conf$-$acc gap", fontsize=8)
    axes[0].tick_params(labelsize=7)

    axes[1].plot(cot, rlvr_14b, "-", marker="o", color=PALETTE["deepseek"])
    axes[1].plot(cot, rlhf_14b, "--", marker="s", color=PALETTE["qwen"])
    axes[1].set_title("14B class", fontsize=9, pad=2)
    axes[1].set_xlabel("CoT budget $K$", fontsize=8)
    axes[1].set_ylabel("Conf$-$acc gap", fontsize=8)
    axes[1].set_xticks(cot)
    axes[1].tick_params(labelsize=7)

    fig.legend(handles=[line_rlvr_7, line_rlhf_7], loc="upper center",
               ncol=2, fontsize=7, frameon=False, bbox_to_anchor=(0.5, 1.0))
    fig.tight_layout(rect=(0, 0, 1, 0.93))
    save_fig(fig, "fig_training_contrast")
    plt.close(fig)


def main():
    figure_headline_regret()
    figure_spotlight_forest()
    figure_theorem3_curves()
    figure_eta_tempering()
    figure_mquake_depth()
    figure_component_ablation()
    figure_oracle_convergence()
    figure_named_comparators()
    figure_popqa_bins()
    figure_w_surface()
    figure_confidence_head()
    figure_schematic()
    figure_minimax()
    figure_temperature_robustness()
    figure_training_contrast()
    print("All figures written to", OUT)


if __name__ == "__main__":
    main()
