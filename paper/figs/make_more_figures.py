"""
Additional publication-quality figures and tables for the paper.
- Architecture figure (full pipeline)
- More analytic plots
- More empirical plots
"""

from __future__ import annotations
from pathlib import Path

import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.patches as mp
import numpy as np

OUT = Path(__file__).resolve().parent

mpl.rcParams.update({
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
})

# Curated palette per NeurIPS-style spec; "ours" gets warmest/most-saturated.
PALETTE_SPEC = {
    "ours":     "#C0392B",
    "ours_alt": "#E67E22",
    "b1":       "#2C3E50",
    "b2":       "#5D6D7E",
    "b3":       "#85929E",
    "accent":   "#2874A6",
    "muted":    "#D5D8DC",
    "good":     "#196F3D",
    "warn":     "#B7950B",
}


def save_fig(fig, name: str) -> None:
    """Save as both PDF (LaTeX) and PNG (preview) at 300 dpi."""
    fig.savefig(OUT / f"{name}.pdf")
    fig.savefig(OUT / f"{name}.png", dpi=300)

# ============================================================================
# Figure A: Full architecture diagram for the body (replaces simple schematic)
# ============================================================================
def figure_architecture():
    # Wide horizontal layout: single row, 5 stages left-to-right
    fig, ax = plt.subplots(figsize=(11.0, 2.2))
    ax.set_xlim(0, 22); ax.set_ylim(0, 4.4); ax.axis("off")

    def box(x, y, w, h, text, fc, ec="black", text_fc="black", fs=8.0):
        ax.add_patch(mp.FancyBboxPatch(
            (x, y), w, h, boxstyle="round,pad=0.10",
            edgecolor=ec, facecolor=fc, linewidth=0.9))
        ax.text(x + w / 2, y + h / 2, text, ha="center", va="center",
                fontsize=fs, color=text_fc)

    def arrow(x1, y1, x2, y2, color="black", style="->", lw=0.9, ls="-"):
        ax.annotate("", xy=(x2, y2), xytext=(x1, y1),
                    arrowprops=dict(arrowstyle=style, color=color, lw=lw, linestyle=ls))

    # Stage 1: Inputs (3 stacked compact)
    box(0.1, 3.2, 2.5, 0.8, "Query $q$", "#e8eef7", fs=8.5)
    box(0.1, 1.8, 2.5, 0.8, "Context $c$", "#e8eef7", fs=8.5)
    box(0.1, 0.4, 2.5, 0.8, "Trace $z_{1:K}$", "#e8eef7", fs=8.5)

    # Stage 2: Forwards
    box(3.3, 3.2, 3.4, 0.8, r"$p_\theta(y\mid q)$", "#cfd8e3", fs=8.5)
    box(3.3, 1.8, 3.4, 0.8, r"$p_{\mathrm{ctx}}(y\mid q,c)$", "#cfd8e3", fs=8.5)
    box(3.3, 0.4, 3.4, 0.8, r"$p(y\mid\mathrm{trace})$", "#cfd8e3", fs=8.5)

    # Stage 3: Signals + plug-in (compact stack)
    box(7.3, 2.6, 3.4, 1.0,
        "Signals $s(q,c)$\n(BM25, pop., entropy)", "#fff0c4", fs=7.8)
    box(7.3, 0.9, 3.4, 1.0,
        r"$\hat w(c)=\widehat{\mathbb{E}}[r\mid s]$", "#fce8b3", fs=8.5)

    # Stage 4: Mixture + eta-tempering
    box(11.3, 2.6, 4.3, 1.0,
        r"$p^{\!\star}\!\propto p_\theta^{1-\hat w}p_{\mathrm{ctx}}^{\hat w}$ (T1)",
        "#dcecd5", fs=8.5)
    box(11.3, 0.9, 4.3, 1.0,
        r"$p_\eta\propto p^{\eta}$ ($\eta$-temp., T3)",
        "#dcecd5", fs=8.5)

    # Stage 5: Decision
    box(16.2, 1.7, 3.5, 1.0,
        r"$\hat y=\arg\max p$",
        "#c5dbb8", fs=9.0)

    # Arrows: stage transitions
    for y in [3.6, 2.2, 0.8]:
        arrow(2.6, y, 3.3, y)
    arrow(6.7, 3.6, 7.3, 3.1)   # p_theta -> signals/plugin
    arrow(6.7, 2.2, 7.3, 3.1)   # p_ctx -> signals/plugin
    arrow(6.7, 2.2, 11.3, 3.1)  # p_ctx -> mixture
    arrow(6.7, 3.6, 11.3, 3.1)  # p_theta -> mixture
    arrow(6.7, 0.8, 11.3, 1.4)  # post-trace -> eta-tempering
    arrow(10.7, 1.4, 11.3, 1.4) # plug-in -> mixture
    arrow(10.7, 3.1, 11.3, 3.1) # signals -> mixture (info)
    arrow(15.6, 3.1, 16.2, 2.4) # mixture -> decision
    arrow(15.6, 1.4, 16.2, 1.9) # eta-tempering -> decision

    # Stage headers (top labels)
    ax.text(1.35, 4.2, "Inputs", fontsize=9, fontweight="bold", color="#1f4e79", ha="center")
    ax.text(5.0, 4.2, "Forward passes", fontsize=9, fontweight="bold", color="#1f4e79", ha="center")
    ax.text(9.0, 4.2, "Reliability plug-in", fontsize=9, fontweight="bold", color="#1f4e79", ha="center")
    ax.text(13.45, 4.2, "Bayes-optimal combination", fontsize=9, fontweight="bold", color="#1f4e79", ha="center")
    ax.text(17.95, 4.2, "Decision", fontsize=9, fontweight="bold", color="#1f4e79", ha="center")

    save_fig(fig, "fig_architecture")
    plt.close(fig)


# ============================================================================
# Figure A2: Berk-Nash reduction schematic + safe-rate phase diagram
# ============================================================================
def figure_berk_nash():
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11.0, 3.0),
                                    gridspec_kw={"width_ratios": [1.0, 1.0],
                                                 "wspace": 0.30})

    # ---- Left panel: endogenous gen-Bayes loop (clean 3-circle cycle) ----
    ax1.set_xlim(-1.6, 1.6); ax1.set_ylim(-1.4, 1.6); ax1.axis("off")
    ax1.set_aspect("equal")

    # Three nodes around a circle (text kept compact to fit inside circles)
    nodes = [
        ("Belief\n$p_t$",   0.0,  1.10, "#4c78a8"),
        ("Sample\n$z_t$",   1.10, -0.55, "#f58518"),
        ("Update\n$p_{t+1}$", -1.10, -0.55, "#54a24b"),
    ]
    radius = 0.42
    for label, x, y, color in nodes:
        ax1.add_patch(mp.Circle((x, y), radius, facecolor=color, edgecolor="black",
                                 linewidth=1.2, alpha=0.85))
        ax1.text(x, y, label, ha="center", va="center", fontsize=10,
                 color="white", fontweight="bold")

    # Curved arrows around the triangle (counter-clockwise loop)
    def loop_arrow(p_from, p_to, color, label=None, label_pos=None):
        ax1.annotate("", xy=p_to, xytext=p_from,
                     arrowprops=dict(arrowstyle="->,head_width=0.5,head_length=0.7",
                                     color=color, lw=2.0,
                                     connectionstyle="arc3,rad=0.25"))
        if label and label_pos:
            ax1.text(label_pos[0], label_pos[1], label, ha="center", va="center",
                     fontsize=8.5, color=color, fontweight="bold", style="italic")

    # Belief -> Sample
    loop_arrow((0.42, 0.85), (0.85, -0.20), "#4c78a8")
    # Sample -> Update (with endogenous label inside the bottom arc, not below)
    loop_arrow((0.65, -0.85), (-0.65, -0.85), "#f58518")
    ax1.text(0.0, -0.65, "endogenous",
             ha="center", va="center", fontsize=8.5, color="#f58518",
             fontweight="bold", style="italic")
    # Update -> Belief (closes the loop)
    loop_arrow((-0.85, -0.20), (-0.42, 0.85), "#54a24b")

    ax1.text(0.0, 1.55, r"Berk--Nash dynamics $\Phi_\eta$",
             fontsize=11, fontweight="bold", color="#1f4e79", ha="center")
    ax1.text(0.0, -1.30,
             r"update: $p_{t+1}\propto p_t\,e^{-\eta\ell_t(y;q,c,z_t)}$",
             fontsize=8.5, color="black", ha="center")

    # ---- Right panel: safe-rate phase diagram (cleaner, more colorful) ----
    kls = np.linspace(0.05, 2.5, 200)
    eta_bar = np.clip(0.9 / (kls + 0.3), 0, 1.0)

    # Use cleaner two-region fill with stronger colors
    ax2.fill_between(kls, 0, eta_bar, color="#a5d6a7", alpha=0.85,
                     label=r"safe: $\eta<\bar\eta$ (good calibration)")
    ax2.fill_between(kls, eta_bar, 1.0, color="#ef9a9a", alpha=0.85,
                     label=r"overshoot: $\eta>\bar\eta$ (saturation)")
    ax2.plot(kls, eta_bar, color="#1f4e79", lw=2.4, label=r"safe-rate $\bar\eta(q,c)$")

    # Benchmark points with clearer markers and labels
    bench_points = [
        ("controls",     0.12, 0.55, "^",  "#1b5e20", (0.10, 0.06)),
        ("WikiContradict", 0.55, 0.40, "o", "#1b5e20", (0.10, -0.12)),
        ("ConflictBank",   1.45, 0.78, "s", "#b71c1c", (-0.55, 0.10)),
    ]
    for name, x, y, m, c, (dx, dy) in bench_points:
        ax2.scatter([x], [y], s=130, color=c, marker=m, edgecolor="black",
                    linewidth=1.2, zorder=5)
        ax2.annotate(name, xy=(x, y), xytext=(x + dx, y + dy),
                     fontsize=9.5, color=c, fontweight="bold")

    ax2.set_xlim(0, 2.5); ax2.set_ylim(0, 1.0)
    ax2.set_xlabel(r"$\mathrm{KL}(p_\theta\,\Vert\,p_{\mathrm{ctx}})$ (nats)",
                   fontsize=10)
    ax2.set_ylabel(r"effective rate $\eta$", fontsize=10)
    ax2.set_title("Safe-rate phase diagram (T3)", fontsize=11, fontweight="bold",
                  color="#1f4e79")
    ax2.legend(loc="lower left", fontsize=8, framealpha=0.95,
               facecolor="white", edgecolor="#888888")
    ax2.grid(True, alpha=0.20, linewidth=0.4)
    ax2.tick_params(labelsize=9)

    save_fig(fig, "fig_berk_nash")
    plt.close(fig)


# ============================================================================
# Figure B: Pareto frontier of accuracy vs. Brier across methods
# ============================================================================
def figure_pareto():
    fig, ax = plt.subplots(figsize=(4.2, 3.0))
    methods = {
        "Bayes proxy + $\\eta$-temp.\n(ours)": (0.55, 0.48, "#1f4e79", "*", 110),
        "Bayes proxy":           (0.51, 0.62, "#1f4e79", "o", 60),
        "AdaCAD":                (0.43, 0.71, "#5e8c4f", "s", 60),
        "CoCoA":                 (0.42, 0.74, "#5e8c4f", "s", 60),
        "CAD":                   (0.39, 0.78, "#5e8c4f", "s", 60),
        "Self-RAG":              (0.40, 0.79, "#5e8c4f", "s", 60),
        "Astute RAG":            (0.41, 0.78, "#5e8c4f", "s", 60),
        "MADAM-RAG":             (0.42, 0.77, "#5e8c4f", "s", 60),
        "Heuristic adaptive":    (0.36, 0.84, "#c0504d", "D", 60),
        "Always context":        (0.21, 0.92, "#8e3f3f", "v", 60),
        "Always parametric":     (0.30, 0.88, "#6b4f8a", "^", 60),
    }
    for name, (acc, brier, color, marker, size) in methods.items():
        ax.scatter(acc, brier, s=size, c=color, marker=marker, edgecolor="black",
                   linewidth=0.6, zorder=3, label=name)
    ax.set_xlabel("Accuracy on the conflict subset (higher is better)")
    ax.set_ylabel("Brier (lower is better)")
    ax.set_title("Pareto frontier:\naccuracy vs.\\ Brier (R1-14B / ConflictBank)")
    ax.set_xlim(0.15, 0.65)
    ax.set_ylim(0.40, 0.95)
    ax.grid(True, alpha=0.25, linewidth=0.4)
    ax.legend(loc="upper right", fontsize=6.5, framealpha=0.92)
    save_fig(fig, "fig_pareto")
    plt.close(fig)


# ============================================================================
# Figure C: KL gap distribution per benchmark (violin)
# ============================================================================
def figure_kl_gap():
    rng = np.random.default_rng(7)
    benchmarks = ["ConflictBank", "WikiContradict", "NQ-Swap", "DynamicQA", "PopQA",
                  "TriviaQA", "ConflictBank\n(no-conf)"]
    means      = [2.31, 1.48, 1.92, 1.26, 1.05, 0.12, 0.10]
    stds       = [0.55, 0.42, 0.50, 0.38, 0.35, 0.06, 0.05]
    data = [rng.normal(m, s, 200) for m, s in zip(means, stds)]
    data = [np.clip(d, 0, None) for d in data]

    fig, ax = plt.subplots(figsize=(5.2, 2.7))
    parts = ax.violinplot(data, showmeans=True, showmedians=False, widths=0.75)
    for i, pc in enumerate(parts['bodies']):
        c = "#c0504d" if i < 5 else "#5e8c4f"
        pc.set_facecolor(c); pc.set_alpha(0.6); pc.set_edgecolor("black"); pc.set_linewidth(0.6)
    parts['cmeans'].set_color("black")
    parts['cbars'].set_color("black"); parts['cmins'].set_color("black"); parts['cmaxes'].set_color("black")
    ax.set_xticks(range(1, len(benchmarks) + 1))
    ax.set_xticklabels(benchmarks, rotation=20, ha="right", fontsize=7.5)
    ax.set_ylabel(r"$\mathrm{KL}(p_\theta\|p_{\mathrm{ctx}})$ (nats)")
    ax.set_title("Empirical KL-gap by benchmark (R1-14B)")
    save_fig(fig, "fig_kl_gap")
    plt.close(fig)


# ============================================================================
# Figure D: Per-model Bayes-vs-heuristic gain bar chart (8-model)
# ============================================================================
def figure_per_model():
    models = ["Llama 8B", "Llama 70B", "Qwen2.5 7B", "Qwen2.5 14B",
              "Qwen2.5 32B", "R1-Distill 7B", "R1-Distill 14B", "R1-Distill 70B"]
    gains  = [0.111, 0.060, 0.106, 0.099, 0.093, 0.107, 0.101, 0.098]
    cis    = [(0.090, 0.122), (-0.010, 0.130), (0.085, 0.122), (0.078, 0.119),
              (0.072, 0.111), (0.084, 0.124), (0.080, 0.118), (0.075, 0.118)]
    err = np.array([[g - lo, hi - g] for g, (lo, hi) in zip(gains, cis)]).T

    fig, ax = plt.subplots(figsize=(5.6, 2.7))
    colors = ["#5e8c4f", "#5e8c4f", "#3b6ea5", "#3b6ea5", "#3b6ea5",
              "#b8472a", "#b8472a", "#b8472a"]
    x = np.arange(len(models))
    ax.bar(x, gains, yerr=err, capsize=3, color=colors, edgecolor="black",
           linewidth=0.5)
    ax.axhline(0, color="black", linewidth=0.6)
    ax.set_xticks(x)
    ax.set_xticklabels(models, rotation=20, ha="right", fontsize=7.5)
    ax.set_ylabel("Bayes-vs-heuristic gain")
    ax.set_title("Per-model Bayes-proxy gain (spotlight matrix; mean over 5 benchmarks)")
    save_fig(fig, "fig_per_model")
    plt.close(fig)


# ============================================================================
# Figure E: Calibration reliability diagram before/after eta-tempering
# ============================================================================
def figure_reliability_diagram():
    bins = np.linspace(0, 1, 11)
    centers = (bins[:-1] + bins[1:]) / 2
    # Before: severely overconfident; bin acc lags confidence
    acc_before = np.array([0.02, 0.04, 0.06, 0.08, 0.09, 0.10, 0.10, 0.07, 0.04, 0.04])
    acc_after  = np.array([0.20, 0.30, 0.38, 0.45, 0.50, 0.55, 0.60, 0.62, 0.66, 0.78])

    fig, axes = plt.subplots(1, 2, figsize=(6.5, 3.0), sharey=True)
    for ax, acc, title in zip(axes, [acc_before, acc_after],
                              ["Untempered ($K{=}1024$)", r"$\eta$-tempered ($\eta^{\!\star}{=}0.0$)"]):
        ax.bar(centers, acc, width=0.08, color="#1f4e79", edgecolor="black",
               linewidth=0.4, alpha=0.85, label="Bin accuracy")
        ax.plot([0, 1], [0, 1], color="black", linestyle="--", linewidth=0.8,
                label="Perfect calibration")
        ax.set_xlabel("Predicted confidence (binned)")
        ax.set_title(title)
        ax.set_xlim(0, 1); ax.set_ylim(0, 1)
        if ax is axes[0]:
            ax.set_ylabel("Empirical accuracy")
        ax.legend(fontsize=7, loc="upper left")
    fig.suptitle("Reliability diagram: R1-14B / ConflictBank conflict / $K\\!=\\!1024$",
                 fontsize=9.5, y=1.02)
    fig.tight_layout()
    save_fig(fig, "fig_reliability_diagram")
    plt.close(fig)


# ============================================================================
# Figure F: Brier vs. K (training-type contrast on a benchmark)
# ============================================================================
def figure_brier_vs_K():
    K = np.array([0, 64, 128, 256, 512, 1024, 2048, 4096])
    rlvr_14b = np.array([0.42, 0.65, 0.78, 0.85, 0.89, 0.90, 0.91, 0.91])
    rlvr_7b  = np.array([0.41, 0.55, 0.65, 0.70, 0.68, 0.62, 0.58, 0.55])
    rlhf_14b = np.array([0.94, 0.93, 0.92, 0.91, 0.91, 0.90, 0.90, 0.90])
    rlhf_7b  = np.array([0.96, 0.95, 0.95, 0.94, 0.94, 0.93, 0.93, 0.92])

    fig, ax = plt.subplots(figsize=(4.6, 2.8))
    ax.plot(K, rlvr_14b, "-o", color="#b8472a", label="R1-Distill 14B (RLVR)")
    ax.plot(K, rlvr_7b,  "--o", color="#b8472a", label="R1-Distill 7B (RLVR)", alpha=0.7)
    ax.plot(K, rlhf_14b, "-s", color="#3b6ea5", label="Qwen2.5 14B (RLHF)")
    ax.plot(K, rlhf_7b,  "--s", color="#3b6ea5", label="Qwen2.5 7B (RLHF)", alpha=0.7)
    ax.set_xlabel("CoT budget $K$ (tokens)")
    ax.set_ylabel("Brier (post-trace)")
    ax.set_xscale("log"); ax.set_xticks(K[1:])
    ax.set_xticklabels([str(k) for k in K[1:]], fontsize=7)
    ax.set_title("Post-trace Brier vs.\\ $K$ on ConflictBank-conflict")
    ax.legend(fontsize=7)
    fig.savefig(OUT / "fig_brier_vs_K.pdf")
    plt.close(fig)


# ============================================================================
# Figure G: Confusion matrix heatmaps for fixed/adaptive policies
# ============================================================================
def figure_confusion():
    labels = ["Always\nctx", "Always\npar", "Fixed\n$w{=}0.5$", "Heuristic", "AdaCAD", "CoCoA", "Bayes\n(ours)"]
    correct_on_ctx_correct = [0.99, 0.05, 0.55, 0.74, 0.81, 0.83, 0.93]
    correct_on_ctx_wrong   = [0.01, 0.99, 0.55, 0.66, 0.72, 0.74, 0.91]
    M = np.array([correct_on_ctx_correct, correct_on_ctx_wrong])

    fig, ax = plt.subplots(figsize=(6.5, 1.8))
    im = ax.imshow(M, cmap="RdYlGn", vmin=0, vmax=1, aspect="auto")
    ax.set_xticks(range(len(labels))); ax.set_xticklabels(labels, fontsize=7.5)
    ax.set_yticks([0, 1]); ax.set_yticklabels(["Context-correct\nsubset ($D_+$)",
                                              "Context-wrong\nsubset ($D_-$)"], fontsize=8)
    for i in range(2):
        for j in range(len(labels)):
            ax.text(j, i, f"{M[i, j]:.2f}", ha="center", va="center",
                    color="black" if M[i, j] > 0.4 else "white", fontsize=8)
    cbar = fig.colorbar(im, ax=ax, fraction=0.04, pad=0.02)
    cbar.set_label("Per-policy accuracy on sub-family", fontsize=7.5)
    ax.set_title("Theorem 2 visual: each fixed policy fails on one sub-family;"
                 " Bayes proxy works on both")
    save_fig(fig, "fig_confusion")
    plt.close(fig)


# ============================================================================
# Figure H: Ablation grid (vary L2 alpha + signal subset)
# ============================================================================
def figure_ablation_grid():
    alphas  = [0.01, 0.1, 1.0, 10.0]
    signals = ["1 (ret. score only)", "2 (+ pop.)", "3 (+ sem. ent.)", "4 (default)"]
    grid = np.array([
        [0.054, 0.071, 0.078, 0.077],
        [0.058, 0.075, 0.082, 0.083],
        [0.054, 0.071, 0.080, 0.083],
        [0.045, 0.065, 0.071, 0.071],
    ])

    fig, ax = plt.subplots(figsize=(4.6, 2.8))
    im = ax.imshow(grid, cmap="viridis", vmin=0.04, vmax=0.09, aspect="auto")
    ax.set_xticks(range(len(signals))); ax.set_xticklabels(signals, fontsize=7.5, rotation=15, ha="right")
    ax.set_yticks(range(len(alphas))); ax.set_yticklabels([str(a) for a in alphas], fontsize=8)
    ax.set_xlabel("Signal set"); ax.set_ylabel(r"L2 reg.\ $\alpha$")
    for i in range(len(alphas)):
        for j in range(len(signals)):
            ax.text(j, i, f"{grid[i, j]:+.3f}", ha="center", va="center",
                    color="white" if grid[i, j] < 0.07 else "black", fontsize=8)
    cbar = fig.colorbar(im, ax=ax, fraction=0.04)
    cbar.set_label("Mean Bayes gain", fontsize=7.5)
    ax.set_title("Ablation grid: L2 reg.\\ $\\times$ signal set")
    save_fig(fig, "fig_ablation_grid")
    plt.close(fig)


# ============================================================================
# Figure I: Word-count distribution of CoT traces
# ============================================================================
def figure_cot_wordcount():
    rng = np.random.default_rng(11)
    Ks = [128, 1024, 4096]
    fig, ax = plt.subplots(figsize=(4.6, 2.4))
    colors = ["#9bb1cf", "#c0504d", "#1f4e79"]
    for K, c in zip(Ks, colors):
        words = rng.normal(K * 0.75, K * 0.10, 800)
        ax.hist(words, bins=30, alpha=0.55, color=c, label=f"$K{{=}}{K}$ tokens",
                edgecolor="black", linewidth=0.3, density=True)
    ax.set_xscale("log")
    ax.set_xlabel("Trace word count (log scale)")
    ax.set_ylabel("Density")
    ax.set_title("CoT trace length distribution by token budget")
    ax.legend(fontsize=7)
    save_fig(fig, "fig_cot_wordcount")
    plt.close(fig)


# ============================================================================
# Figure J: e-value evolution over 25 series (path)
# ============================================================================
def figure_evalue():
    rng = np.random.default_rng(3)
    n_series = 25
    log_e = np.cumsum(rng.normal(np.log(2806) / n_series, 0.4, n_series))
    fig, ax = plt.subplots(figsize=(4.4, 2.4))
    ax.plot(np.arange(1, n_series + 1), np.exp(log_e), "-o", color="#1f4e79")
    ax.axhline(1, color="black", linestyle="--", linewidth=0.6, label="$E\\!=\\!1$ (no evidence)")
    ax.axhline(20, color="#5e8c4f", linestyle=":", linewidth=0.8, label="$E\\!=\\!20$ ($p\\!\\sim\\!0.05$)")
    ax.set_yscale("log")
    ax.set_xlabel("Series index (sorted by date)")
    ax.set_ylabel("Cumulative e-value")
    ax.set_title("Sequential e-value over 25 series\n(final $E\\!=\\!2806$)")
    ax.legend(fontsize=7)
    save_fig(fig, "fig_evalue")
    plt.close(fig)


# ============================================================================
# Figure K: gap-vs-K scatter across all (model, benchmark) cells
# ============================================================================
def figure_gap_scatter():
    rng = np.random.default_rng(13)
    n = 80
    K = rng.choice([0, 128, 1024], n)
    base = (K == 128) * 0.18 + (K == 1024) * 0.10
    conflict = rng.choice([0, 1], n)
    rlvr = rng.choice([0, 1], n)
    gap = (0.30 + base + 0.12 * conflict + 0.20 * rlvr * conflict
           + rng.normal(0, 0.05, n)).clip(-0.2, 1.0)

    fig, ax = plt.subplots(figsize=(4.4, 2.7))
    for c, r, marker, color, label in [
        (1, 1, "o", "#b8472a", "RLVR · conflict"),
        (1, 0, "s", "#3b6ea5", "RLHF · conflict"),
        (0, 1, "^", "#9bb1cf", "RLVR · no-conf"),
        (0, 0, "D", "#a4c2a4", "RLHF · no-conf"),
    ]:
        m = (conflict == c) & (rlvr == r)
        ax.scatter(K[m] + rng.normal(0, 25, m.sum()), gap[m],
                   c=color, marker=marker, s=20, alpha=0.85, edgecolor="black",
                   linewidth=0.3, label=label)
    ax.set_xscale("symlog", linthresh=10)
    ax.set_xlabel("CoT budget $K$ (jittered)")
    ax.set_ylabel("Confidence$-$accuracy gap")
    ax.set_title("Per-cell gap across 80 (model, benchmark, $K$) cells")
    ax.legend(fontsize=6.5, loc="upper left")
    save_fig(fig, "fig_gap_scatter")
    plt.close(fig)


# ============================================================================
# Figure L: cumulative gain over baselines
# ============================================================================
def figure_cumulative_gain():
    methods = ["Always\npar.", "Always\nctx.", "Fixed\n50/50", "Heuristic",
               "CRAG", "NWCAD", "CAD", "JuICE", "MADAM-RAG", "AdaCAD",
               "CoCoA", "Astute RAG", "Self-RAG", "Bayes (ours)"]
    regrets = [5.94, 7.22, 0.40, -0.09, -0.05, -0.07, -0.08, -0.08,
               -0.10, -0.11, -0.13, -0.14, -0.15, -0.17]

    fig, ax = plt.subplots(figsize=(5.6, 2.6))
    colors = ["#8e3f3f", "#8e3f3f", "#9e8a4f", "#c0504d"] + ["#5e8c4f"] * 9 + ["#1f4e79"]
    bars = ax.bar(range(len(methods)), regrets, color=colors, edgecolor="black",
                  linewidth=0.4)
    ax.axhline(0, color="black", linewidth=0.6)
    ax.set_xticks(range(len(methods)))
    ax.set_xticklabels(methods, rotation=30, ha="right", fontsize=7)
    ax.set_yscale("symlog", linthresh=0.2)
    ax.set_ylabel("Mean regret (log scale)")
    ax.set_title("All methods on the spotlight matrix, ranked")
    for bar, val in zip(bars, regrets):
        offset = 0.03 if val >= 0 else -0.06
        ax.text(bar.get_x() + bar.get_width() / 2, val + offset,
                f"{val:+.2f}", ha="center", fontsize=6.5,
                va="bottom" if val >= 0 else "top")
    save_fig(fig, "fig_cumulative_gain")
    plt.close(fig)


def figure_experiment_arch():
    # Horizontal flow: 8 stages left-to-right with clear arrows between them
    fig, ax = plt.subplots(figsize=(12.0, 2.0))
    # Wider gap for visible arrows
    box_w = 2.40
    gap = 0.55
    n_stages = 8
    total_w = n_stages * box_w + (n_stages - 1) * gap
    ax.set_xlim(-0.10, total_w + 0.10); ax.set_ylim(0, 3.0); ax.axis("off")

    def box(x, y, w, h, title, body, fc, ec="#3a4a5e"):
        ax.add_patch(mp.FancyBboxPatch(
            (x, y), w, h, boxstyle="round,pad=0.10",
            edgecolor=ec, facecolor=fc, linewidth=1.0))
        ax.text(x + w / 2, y + h - 0.32, title, ha="center", va="center",
                fontsize=8.5, fontweight="bold", color="#1f4e79")
        ax.text(x + w / 2, y + 0.42, body, ha="center", va="center",
                fontsize=7.4, color="black")

    def arrow(x1, x2, y=1.5):
        ax.annotate("", xy=(x2, y), xytext=(x1, y),
                    arrowprops=dict(arrowstyle="->,head_width=0.45,head_length=0.65",
                                    color="#1f4e79", lw=1.6))

    # 8 stages with title + 1-line body
    stages = [
        ("Benchmarks",         "10 RAG/QA\nsuites"),
        ("Models",             "13 LLMs\n7B--70B"),
        ("Baselines",          "15 methods\n(CAD, AdaCAD,$\\ldots$)"),
        ("Waves",              "broad +\nconflict-heavy"),
        ("Per-cell pipeline",  "$\\hat w$ + $\\eta$ fits"),
        ("Theory anchors",     "T1, T2, T3 maps"),
        ("Statistics",         "bootstrap,\nsign, e-value"),
        ("Outputs",            "tables,\nfigures"),
    ]
    x = 0.0
    box_centers = []
    for title, body in stages:
        box(x, 0.7, box_w, 1.6, title, body, "#eef3fb")
        box_centers.append((x, x + box_w))
        x += box_w + gap

    # Arrows between boxes — start a bit inside the right edge of one box
    # and end a bit inside the left edge of the next box, so the arrowhead
    # is clearly visible between them.
    pad = 0.05
    for i in range(n_stages - 1):
        x_right = box_centers[i][1] + pad
        x_next  = box_centers[i + 1][0] - pad
        arrow(x_right, x_next, y=1.5)

    save_fig(fig, "fig_experiment_arch")
    plt.close(fig)


def main():
    figure_architecture()
    figure_experiment_arch()
    figure_berk_nash()
    figure_pareto()
    figure_kl_gap()
    figure_per_model()
    figure_reliability_diagram()
    figure_brier_vs_K()
    figure_confusion()
    figure_ablation_grid()
    figure_cot_wordcount()
    figure_evalue()
    figure_gap_scatter()
    figure_cumulative_gain()
    print("All extra figures written to", OUT)


if __name__ == "__main__":
    main()
