# ============================================================
#  VISUALIZATION MODULE  —  PROFESSIONAL VERSION
#  MWCNT Characterization and Analysis System
# ============================================================

from pathlib import Path

# ⚠ CRITICAL: force matplotlib to draw to file only.
#    This must come BEFORE importing pyplot.
import matplotlib
matplotlib.use("Agg")

import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator

import analysis


BASE_DIR = Path(__file__).resolve().parent
PLOTS_DIR = BASE_DIR / "plots"
PLOTS_DIR.mkdir(parents=True, exist_ok=True)


# ============================================================
#  GLOBAL PROFESSIONAL STYLE
# ============================================================
def _apply_style():
    """Apply a clean, publication-quality style to all plots."""
    plt.rcParams.update({
        "figure.facecolor":   "#ffffff",
        "axes.facecolor":     "#fbfcfe",
        "axes.edgecolor":     "#cbd5e1",
        "axes.labelcolor":    "#1e293b",
        "axes.titleweight":   "bold",
        "axes.titlesize":     13,
        "axes.labelsize":     11,
        "axes.grid":          True,
        "axes.axisbelow":     True,
        "grid.color":         "#e2e8f0",
        "grid.linestyle":     "-",
        "grid.linewidth":     0.8,
        "xtick.color":        "#475569",
        "ytick.color":        "#475569",
        "xtick.labelsize":    10,
        "ytick.labelsize":    10,
        "legend.frameon":     True,
        "legend.framealpha":  0.95,
        "legend.facecolor":   "#ffffff",
        "legend.edgecolor":   "#e2e8f0",
        "legend.fontsize":    10,
        "font.family":        "DejaVu Sans",
        "savefig.facecolor":  "#ffffff",
    })


_apply_style()


# ============================================================
#  HELPERS
# ============================================================
def to_float(value, default=None):
    return analysis.to_float(value, default)


def save_figure(fig, filename):
    """Save figure to the plots folder, close it, and return the path."""
    path = PLOTS_DIR / filename

    try:
        fig.tight_layout()
    except Exception:
        pass

    fig.savefig(path, dpi=200, bbox_inches="tight")
    plt.close(fig)

    return path


def _check_data(x, y, name):
    if not x or not y:
        raise ValueError(f"No valid data available for {name}.")


def _finish_axes(ax, title, xlabel, ylabel):
    """Apply consistent title/labels to an axis."""
    ax.set_title(title, pad=14)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_color("#cbd5e1")
    ax.spines["bottom"].set_color("#cbd5e1")


# ============================================================
#  BET
# ============================================================
def plot_bet_isotherm():
    rows = analysis.get_bet_isotherm()

    ads_x, ads_y = [], []
    des_x, des_y = [], []

    for row in rows:
        p = to_float(row.get("relative_pressure_p_p0"))
        v = to_float(row.get("volume_adsorbed_cm3_g_STP"))
        branch = str(row.get("branch", "")).strip().lower()

        if p is None or v is None:
            continue

        if branch == "adsorption":
            ads_x.append(p)
            ads_y.append(v)
        elif branch == "desorption":
            des_x.append(p)
            des_y.append(v)

    if not ads_x and not des_x:
        raise ValueError("No valid BET isotherm data were found.")

    fig, ax = plt.subplots(figsize=(9, 6))

    if ads_x:
        ax.plot(
            ads_x, ads_y,
            marker="o", markersize=5,
            linewidth=2, color="#1d4ed8",
            markerfacecolor="white", markeredgewidth=1.4,
            label="Adsorption"
        )
    if des_x:
        ax.plot(
            des_x, des_y,
            marker="s", markersize=5,
            linewidth=2, color="#dc2626",
            markerfacecolor="white", markeredgewidth=1.4,
            label="Desorption"
        )

    _finish_axes(
        ax,
        "BET Nitrogen Adsorption-Desorption Isotherm",
        "Relative Pressure, P/P₀",
        "Adsorbed Volume (cm³/g STP)"
    )
    ax.legend(loc="best")

    return save_figure(fig, "bet_isotherm.png")


# ============================================================
#  BJH
# ============================================================
def _plot_bjh(rows, title, filename):
    x, y = [], []

    for row in rows:
        radius = to_float(row.get("pore_radius_nm"))
        dv = to_float(row.get("dV_logr_cm3_g"))
        if radius is None or dv is None:
            continue
        x.append(radius)
        y.append(dv)

    _check_data(x, y, title)

    fig, ax = plt.subplots(figsize=(9, 6))

    ax.plot(
        x, y,
        marker="o", markersize=5,
        linewidth=2, color="#0f766e",
        markerfacecolor="white", markeredgewidth=1.4
    )

    _finish_axes(ax, title, "Pore Radius (nm)", "dV/dlog(r) (cm³/g)")

    return save_figure(fig, filename)


def plot_bjh_adsorption():
    return _plot_bjh(
        analysis.load_bjh_adsorption(),
        "BJH Pore-Size Distribution — Adsorption",
        "bjh_adsorption.png"
    )


def plot_bjh_desorption():
    return _plot_bjh(
        analysis.load_bjh_desorption(),
        "BJH Pore-Size Distribution — Desorption",
        "bjh_desorption.png"
    )


def plot_bjh_comparison():
    adsorption = analysis.load_bjh_adsorption()
    desorption = analysis.load_bjh_desorption()

    fig, ax = plt.subplots(figsize=(9, 6))

    has_data = False

    for rows, label, color, marker in [
        (adsorption, "Adsorption", "#1d4ed8", "o"),
        (desorption, "Desorption", "#dc2626", "s"),
    ]:
        x, y = [], []

        for row in rows:
            radius = to_float(row.get("pore_radius_nm"))
            dv = to_float(row.get("dV_logr_cm3_g"))
            if radius is None or dv is None:
                continue
            x.append(radius)
            y.append(dv)

        if x:
            has_data = True
            ax.plot(
                x, y,
                marker=marker, markersize=5,
                linewidth=2, color=color,
                markerfacecolor="white", markeredgewidth=1.4,
                label=label
            )

    if not has_data:
        plt.close(fig)
        raise ValueError("No valid BJH comparison data were found.")

    _finish_axes(
        ax,
        "BJH Pore-Size Distribution Comparison",
        "Pore Radius (nm)",
        "dV/dlog(r) (cm³/g)"
    )
    ax.legend(loc="best")

    return save_figure(fig, "bjh_comparison.png")


# ============================================================
#  DFT
# ============================================================
def plot_dft_distribution():
    rows = analysis.load_dft_pore_size()

    x, y = [], []

    for row in rows:
        width = to_float(row.get("pore_width_nm"))
        dv = to_float(row.get("dVd_cm3_nm_g"))
        if width is None or dv is None:
            continue
        x.append(width)
        y.append(dv)

    _check_data(x, y, "DFT pore distribution")

    fig, ax = plt.subplots(figsize=(9, 6))

    ax.plot(x, y, linewidth=2, color="#7c3aed")

    # shade area under curve
    ax.fill_between(x, y, alpha=0.15, color="#7c3aed")

    peak = analysis.get_dft_peak_pore_width()
    if peak is not None:
        ax.axvline(
            peak,
            linestyle="--", linewidth=1.5,
            color="#dc2626",
            label=f"Peak width = {peak:.3f} nm"
        )
        ax.legend(loc="best")

    _finish_axes(
        ax,
        "DFT Pore-Width Distribution",
        "Pore Width (nm)",
        "dV/dD (cm³/g/nm)"
    )
    ax.xaxis.set_major_locator(MaxNLocator(nbins=8))

    return save_figure(fig, "dft_distribution.png")


def plot_dft_surface_area():
    rows = analysis.load_dft_pore_size()

    x, y = [], []

    for row in rows:
        width = to_float(row.get("pore_width_nm"))
        area = to_float(row.get("cum_surface_area_m2_g"))
        if width is None or area is None:
            continue
        x.append(width)
        y.append(area)

    _check_data(x, y, "DFT surface area distribution")

    fig, ax = plt.subplots(figsize=(9, 6))

    ax.plot(x, y, linewidth=2, color="#0891b2")
    ax.fill_between(x, y, alpha=0.15, color="#0891b2")

    _finish_axes(
        ax,
        "DFT Cumulative Surface-Area Distribution",
        "Pore Width (nm)",
        "Cumulative Surface Area (m²/g)"
    )
    ax.xaxis.set_major_locator(MaxNLocator(nbins=8))

    return save_figure(fig, "dft_surface_area.png")


def plot_dft_fitting():
    rows = analysis.load_dft_fitting()

    x, measured, fitted = [], [], []

    for row in rows:
        p = to_float(row.get("relative_pressure_p_p0"))
        m = to_float(row.get("measured_volume_cm3_g"))
        f = to_float(row.get("fitted_volume_cm3_g"))
        if p is None or m is None or f is None:
            continue
        x.append(p)
        measured.append(m)
        fitted.append(f)

    if not x:
        raise ValueError("No valid DFT fitting data were found.")

    fig, ax = plt.subplots(figsize=(9, 6))

    ax.plot(
        x, measured,
        linewidth=2, color="#1d4ed8",
        label="Measured"
    )
    ax.plot(
        x, fitted,
        linestyle="--", linewidth=2, color="#dc2626",
        label="DFT fitted"
    )

    _finish_axes(
        ax,
        "DFT Model Fitting",
        "Relative Pressure, P/P₀",
        "Volume (cm³/g)"
    )
    ax.legend(loc="best")

    return save_figure(fig, "dft_fitting.png")


# ============================================================
#  EDS
# ============================================================
def plot_eds_composition():
    elements = analysis.get_major_elements()

    names, values = [], []

    for item in elements:
        name = item.get("element")
        value = to_float(item.get("weight_percent"))
        if name and value is not None:
            names.append(name)
            values.append(value)

    if not names:
        raise ValueError("No valid EDS composition data were found.")

    fig, ax = plt.subplots(figsize=(9, 6))

    colors = plt.cm.viridis(
        [i / max(len(names) - 1, 1) for i in range(len(names))]
    )

    bars = ax.bar(names, values, color=colors, edgecolor="#334155", linewidth=0.8)

    # value labels on top of bars
    for bar, value in zip(bars, values):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + max(values) * 0.015,
            f"{value:.2f}%",
            ha="center", va="bottom",
            fontsize=9, color="#1e293b"
        )

    _finish_axes(
        ax,
        "EDS Elemental Composition",
        "Element",
        "Weight Percentage (%)"
    )

    return save_figure(fig, "eds_composition.png")


# ============================================================
#  XRD
# ============================================================
def plot_xrd():
    rows = analysis.load_xrd()

    x, y = [], []

    for row in rows:
        theta = to_float(row.get("two_theta_deg"))
        intensity = to_float(row.get("intensity_counts"))
        if theta is None or intensity is None:
            continue
        x.append(theta)
        y.append(intensity)

    _check_data(x, y, "XRD pattern")

    fig, ax = plt.subplots(figsize=(10, 6))

    ax.plot(x, y, linewidth=1.6, color="#0f172a")

    peaks = analysis.get_xrd_detected_peaks()
    if peaks:
        peak_x = [p["two_theta"] for p in peaks[:8]]
        peak_y = [p["intensity"] for p in peaks[:8]]
        ax.scatter(
            peak_x, peak_y,
            s=45, color="#dc2626",
            edgecolor="white", linewidth=1.2,
            zorder=5,
            label="Detected peaks"
        )
        ax.legend(loc="best")

    _finish_axes(
        ax,
        "XRD / SRD Diffraction Pattern",
        "2θ (degrees)",
        "Intensity (counts)"
    )

    return save_figure(fig, "xrd_pattern.png")


# ============================================================
#  GENERATE ALL
# ============================================================
def generate_all_plots():
    """Generate every plot. Returns (succeeded, errors)."""
    generated = []
    errors = []

    functions = [
        plot_bet_isotherm,
        plot_bjh_adsorption,
        plot_bjh_desorption,
        plot_bjh_comparison,
        plot_dft_distribution,
        plot_dft_surface_area,
        plot_dft_fitting,
        plot_eds_composition,
        plot_xrd,
    ]

    for function in functions:
        try:
            path = function()
            generated.append(path)
            print(f"Generated: {path}")
        except Exception as error:
            errors.append(f"{function.__name__}: {error}")
            print(f"Plot error in {function.__name__}: {error}")

    return generated, errors


# ============================================================
#  STANDALONE TEST
# ============================================================
if __name__ == "__main__":
    print("=" * 60)
    print(" Generating MWCNT characterization plots")
    print("=" * 60)

    files, errors = generate_all_plots()

    print()
    for file in files:
        print(f"  Saved: {file}")

    if errors:
        print()
        print("  Errors:")
        for e in errors:
            print(f"   - {e}")

    print()
    print("Plot generation complete.")