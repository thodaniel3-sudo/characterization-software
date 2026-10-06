# ============================================================
#  MWCNT CHARACTERIZATION AND ANALYSIS SYSTEM
#  main.py  —  PROFESSIONAL REDESIGN (PyInstaller-ready)
# ============================================================

import tkinter as tk
from tkinter import ttk, messagebox
from pathlib import Path
from datetime import datetime
import os
import sys                                   # ← NEW: needed for frozen check

import analysis
import visualization
import database
import reports

from output_window import OutputWindow, output_image, output_report, output_analysis


# ============================================================
#  PATHS  (works both as .py and as packaged .exe)
# ============================================================
if getattr(sys, "frozen", False):
    # Running inside a PyInstaller bundle (.exe)
    # PyInstaller unpacks data into a temp folder -> sys._MEIPASS
    RESOURCE_DIR = Path(sys._MEIPASS)
    # Where the .exe itself lives (for writing user output next to it)
    BASE_DIR = Path(sys.executable).resolve().parent
else:
    # Normal Python execution
    RESOURCE_DIR = Path(__file__).resolve().parent
    BASE_DIR = Path(__file__).resolve().parent

# Bundled resources (read from here) — plots/reports folders we ship
PLOTS_DIR = RESOURCE_DIR / "plots"
REPORTS_DIR = RESOURCE_DIR / "reports"

# User-writable output folders (write next to the .exe or to project dir)
USER_PLOTS_DIR = BASE_DIR / "plots"
USER_REPORTS_DIR = BASE_DIR / "reports"
USER_DATA_DIR = BASE_DIR / "data"

for folder in (PLOTS_DIR, REPORTS_DIR, USER_PLOTS_DIR, USER_REPORTS_DIR, USER_DATA_DIR):
    try:
        folder.mkdir(parents=True, exist_ok=True)
    except Exception:
        pass


# ============================================================
#  DESIGN TOKENS
# ============================================================
class Theme:
    # Backgrounds
    BG_APP        = "#f1f5f9"
    BG_SURFACE    = "#ffffff"
    BG_HEADER     = "#0f172a"
    BG_SIDEBAR    = "#1e293b"
    BG_SIDEBAR_HI = "#334155"
    BG_STATUS     = "#e2e8f0"

    # Foregrounds
    FG_PRIMARY    = "#0f172a"
    FG_SECONDARY  = "#475569"
    FG_MUTED      = "#94a3b8"
    FG_INVERSE    = "#f8fafc"

    # Accents
    ACCENT        = "#2563eb"
    ACCENT_HOVER  = "#1d4ed8"
    SUCCESS       = "#16a34a"
    WARNING       = "#d97706"
    DANGER        = "#dc2626"

    # Borders
    BORDER        = "#e2e8f0"
    DIVIDER       = "#cbd5e1"

    # Fonts
    FONT_FAMILY   = "Segoe UI"
    FONT_TITLE    = (FONT_FAMILY, 22, "bold")
    FONT_SUBTITLE = (FONT_FAMILY, 10)
    FONT_HEAD     = (FONT_FAMILY, 20, "bold")
    FONT_NAV      = (FONT_FAMILY, 10)
    FONT_CARD_T   = (FONT_FAMILY, 9, "bold")
    FONT_CARD_V   = (FONT_FAMILY, 18, "bold")
    FONT_CARD_S   = (FONT_FAMILY, 9)
    FONT_SECTION  = (FONT_FAMILY, 12, "bold")
    FONT_BODY     = (FONT_FAMILY, 10)
    FONT_SMALL    = (FONT_FAMILY, 9)


# ============================================================
#  MAIN APPLICATION
# ============================================================
class MWCNTApplication(tk.Tk):

    def __init__(self):
        super().__init__()

        self.title("MWCNT Characterization and Analysis System")
        self.geometry("1380x850")
        self.minsize(1150, 720)
        self.configure(bg=Theme.BG_APP)

        database.initialize_database()

        self.output_win = OutputWindow("MWCNT Results Viewer")

        self.nav_buttons = {}
        self.active_page = None

        self.setup_style()
        self.build_interface()
        self.show_dashboard()

        self.protocol("WM_DELETE_WINDOW", self._on_close)

    def _on_close(self):
        try:
            self.output_win.close()
        except Exception:
            pass
        self.destroy()

    # ========================================================
    #  TTK STYLE
    # ========================================================
    def setup_style(self):
        style = ttk.Style(self)
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass

        style.configure(
            "Treeview",
            background=Theme.BG_SURFACE,
            fieldbackground=Theme.BG_SURFACE,
            foreground=Theme.FG_PRIMARY,
            rowheight=32,
            font=(Theme.FONT_FAMILY, 10),
            borderwidth=0,
        )
        style.configure(
            "Treeview.Heading",
            background="#f8fafc",
            foreground=Theme.FG_SECONDARY,
            font=(Theme.FONT_FAMILY, 10, "bold"),
            relief="flat",
            borderwidth=0,
            padding=(8, 10),
        )
        style.map("Treeview.Heading", background=[("active", "#eef2f7")])
        style.map(
            "Treeview",
            background=[("selected", Theme.ACCENT)],
            foreground=[("selected", "#ffffff")],
        )

        style.configure(
            "Primary.TButton",
            font=(Theme.FONT_FAMILY, 10, "bold"),
            padding=(14, 9),
            foreground="#ffffff",
            background=Theme.ACCENT,
            borderwidth=0,
            focuscolor=Theme.ACCENT_HOVER,
        )
        style.map(
            "Primary.TButton",
            background=[("active", Theme.ACCENT_HOVER), ("pressed", Theme.ACCENT_HOVER)],
            foreground=[("active", "#ffffff")],
        )

        style.configure(
            "Secondary.TButton",
            font=(Theme.FONT_FAMILY, 10),
            padding=(12, 8),
            foreground=Theme.FG_PRIMARY,
            background="#e2e8f0",
            borderwidth=0,
        )
        style.map(
            "Secondary.TButton",
            background=[("active", "#cbd5e1"), ("pressed", "#cbd5e1")],
        )

        style.configure(
            "Danger.TButton",
            font=(Theme.FONT_FAMILY, 10, "bold"),
            padding=(12, 8),
            foreground="#ffffff",
            background=Theme.DANGER,
            borderwidth=0,
        )
        style.map("Danger.TButton", background=[("active", "#b91c1c")])

        style.configure("TNotebook", background=Theme.BG_APP, borderwidth=0)
        style.configure(
            "TNotebook.Tab",
            padding=(14, 8),
            font=(Theme.FONT_FAMILY, 10),
        )

    # ========================================================
    #  MAIN LAYOUT
    # ========================================================
    def build_interface(self):
        self._build_header()

        body = tk.Frame(self, bg=Theme.BG_APP)
        body.pack(fill="both", expand=True)

        self._build_sidebar(body)

        content_wrap = tk.Frame(body, bg=Theme.BG_APP)
        content_wrap.pack(side="left", fill="both", expand=True)

        self.content = tk.Frame(content_wrap, bg=Theme.BG_APP)
        self.content.pack(fill="both", expand=True)

        self._build_status_bar()

    # --------------------------------------------------------
    #  HEADER
    # --------------------------------------------------------
    def _build_header(self):
        header = tk.Frame(self, bg=Theme.BG_HEADER, height=82)
        header.pack(side="top", fill="x")
        header.pack_propagate(False)

        brand = tk.Frame(header, bg=Theme.BG_HEADER)
        brand.pack(side="left", padx=(28, 0))

        dot = tk.Canvas(brand, width=14, height=14, bg=Theme.BG_HEADER,
                        highlightthickness=0)
        dot.create_oval(2, 2, 12, 12, fill=Theme.ACCENT, outline="")
        dot.pack(side="left", padx=(0, 12), pady=(0, 2))

        text_block = tk.Frame(brand, bg=Theme.BG_HEADER)
        text_block.pack(side="left")

        tk.Label(
            text_block,
            text="MWCNT CHARACTERIZATION",
            bg=Theme.BG_HEADER, fg=Theme.FG_INVERSE,
            font=Theme.FONT_HEAD,
        ).pack(anchor="w")

        tk.Label(
            text_block,
            text="Characterization · Analysis · Reporting",
            bg=Theme.BG_HEADER, fg="#94a3b8",
            font=Theme.FONT_SMALL,
        ).pack(anchor="w", pady=(2, 0))

        right = tk.Frame(header, bg=Theme.BG_HEADER)
        right.pack(side="right", padx=24)

        self._make_status_pill(right, "System Ready", Theme.SUCCESS).pack(
            side="left", padx=(0, 14)
        )

        ttk.Button(
            right,
            text="📊  Results Viewer",
            style="Primary.TButton",
            command=self.show_results_viewer,
        ).pack(side="left")

    def _make_status_pill(self, parent, text, color):
        pill = tk.Frame(parent, bg="#1e293b", bd=0)
        inner = tk.Frame(pill, bg="#1e293b")
        inner.pack(padx=12, pady=5)

        dot = tk.Canvas(inner, width=8, height=8, bg="#1e293b",
                        highlightthickness=0)
        dot.create_oval(1, 1, 7, 7, fill=color, outline="")
        dot.pack(side="left", padx=(0, 8))

        tk.Label(
            inner, text=text, bg="#1e293b", fg="#cbd5e1",
            font=(Theme.FONT_FAMILY, 9, "bold")
        ).pack(side="left")

        return pill

    # --------------------------------------------------------
    #  SIDEBAR
    # --------------------------------------------------------
    def _build_sidebar(self, parent):
        self.sidebar = tk.Frame(parent, bg=Theme.BG_SIDEBAR, width=250)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        tk.Label(
            self.sidebar,
            text="ANALYSIS MODULES",
            bg=Theme.BG_SIDEBAR, fg=Theme.FG_MUTED,
            font=(Theme.FONT_FAMILY, 9, "bold"),
        ).pack(anchor="w", padx=24, pady=(28, 12))

        items = [
            ("Dashboard",        "🏠", self.show_dashboard),
            ("BET Analysis",     "📈", self.show_bet),
            ("BJH Analysis",     "🧪", self.show_bjh),
            ("DFT Analysis",     "🧮", self.show_dft),
            ("EDS Analysis",     "⚛",  self.show_eds),
            ("XRD / SRD",        "🔬", self.show_xrd),
            ("SEM / TEM",        "🖼", self.show_morphology),
            ("Reports",          "📄", self.show_reports),
        ]

        for label, icon, command in items:
            self._make_nav_button(label, icon, command)

        spacer = tk.Frame(self.sidebar, bg=Theme.BG_SIDEBAR)
        spacer.pack(fill="both", expand=True)

        info = tk.Frame(self.sidebar, bg="#172032")
        info.pack(fill="x", padx=12, pady=12)

        tk.Label(
            info, text="Session", bg="#172032", fg=Theme.FG_MUTED,
            font=(Theme.FONT_FAMILY, 8, "bold")
        ).pack(anchor="w", padx=12, pady=(10, 2))

        self.session_label = tk.Label(
            info,
            text=datetime.now().strftime("%Y-%m-%d  %H:%M"),
            bg="#172032", fg="#cbd5e1",
            font=(Theme.FONT_FAMILY, 9),
        )
        self.session_label.pack(anchor="w", padx=12, pady=(0, 10))

    def _make_nav_button(self, label, icon, command):
        btn = tk.Frame(self.sidebar, bg=Theme.BG_SIDEBAR, cursor="hand2")
        btn.pack(fill="x", padx=10, pady=1)

        accent = tk.Frame(btn, bg=Theme.BG_SIDEBAR, width=4)
        accent.pack(side="left", fill="y")

        inner = tk.Frame(btn, bg=Theme.BG_SIDEBAR)
        inner.pack(side="left", fill="both", expand=True)

        icon_lbl = tk.Label(
            inner, text=icon, bg=Theme.BG_SIDEBAR, fg=Theme.FG_INVERSE,
            font=(Theme.FONT_FAMILY, 12), width=3,
        )
        icon_lbl.pack(side="left", padx=(10, 0), pady=11)

        text_lbl = tk.Label(
            inner, text=label, bg=Theme.BG_SIDEBAR, fg="#cbd5e1",
            font=Theme.FONT_NAV, anchor="w",
        )
        text_lbl.pack(side="left", fill="x", expand=True, pady=11)

        widgets = (btn, inner, icon_lbl, text_lbl, accent)

        def on_enter(_):
            if self.nav_buttons.get(label, (None, None))[1] is True:
                return
            for w in widgets:
                w.configure(bg=Theme.BG_SIDEBAR_HI)

        def on_leave(_):
            if self.nav_buttons.get(label, (None, None))[1] is True:
                return
            for w in widgets:
                w.configure(bg=Theme.BG_SIDEBAR)

        def on_click(_):
            command()

        for w in widgets:
            w.bind("<Enter>", on_enter)
            w.bind("<Leave>", on_leave)
            w.bind("<Button-1>", on_click)

        self.nav_buttons[label] = (widgets, False)

    def _set_active_nav(self, label):
        for key, (widgets, _) in self.nav_buttons.items():
            for w in widgets:
                w.configure(bg=Theme.BG_SIDEBAR)
            self.nav_buttons[key] = (widgets, False)

        if label in self.nav_buttons:
            widgets, _ = self.nav_buttons[label]
            for w in widgets:
                w.configure(bg=Theme.BG_SIDEBAR_HI)
            widgets[-1].configure(bg=Theme.ACCENT)
            self.nav_buttons[label] = (widgets, True)

    # --------------------------------------------------------
    #  STATUS BAR
    # --------------------------------------------------------
    def _build_status_bar(self):
        bar = tk.Frame(self, bg=Theme.BG_STATUS, height=30)
        bar.pack(side="bottom", fill="x")
        bar.pack_propagate(False)

        self.status_label = tk.Label(
            bar,
            text="Ready",
            bg=Theme.BG_STATUS, fg=Theme.FG_SECONDARY,
            font=Theme.FONT_SMALL,
        )
        self.status_label.pack(side="left", padx=18)

        tk.Label(
            bar,
            text=f"Plots: {USER_PLOTS_DIR}",
            bg=Theme.BG_STATUS, fg=Theme.FG_MUTED,
            font=Theme.FONT_SMALL,
        ).pack(side="right", padx=18)

    def set_status(self, message, color=None):
        try:
            self.status_label.configure(
                text=message,
                fg=color or Theme.FG_SECONDARY,
            )
        except Exception:
            pass

    # ========================================================
    #  CONTENT HELPERS
    # ========================================================
    def clear_content(self):
        for widget in self.content.winfo_children():
            widget.destroy()

    def page_title(self, title, description, breadcrumb=None):
        wrap = tk.Frame(self.content, bg=Theme.BG_APP)
        wrap.pack(fill="x", padx=32, pady=(24, 14))

        if breadcrumb:
            tk.Label(
                wrap, text=breadcrumb, bg=Theme.BG_APP, fg=Theme.FG_MUTED,
                font=Theme.FONT_SMALL,
            ).pack(anchor="w", pady=(0, 2))

        tk.Label(
            wrap, text=title, bg=Theme.BG_APP, fg=Theme.FG_PRIMARY,
            font=Theme.FONT_TITLE,
        ).pack(anchor="w")

        tk.Label(
            wrap, text=description, bg=Theme.BG_APP, fg=Theme.FG_SECONDARY,
            font=Theme.FONT_SUBTITLE,
        ).pack(anchor="w", pady=(4, 0))

        div = tk.Frame(wrap, bg=Theme.DIVIDER, height=1)
        div.pack(fill="x", pady=(12, 0))

    def card(self, parent, title, value, subtitle="", accent=None):
        outer = tk.Frame(parent, bg=Theme.BORDER)
        inner = tk.Frame(outer, bg=Theme.BG_SURFACE)
        inner.pack(fill="both", expand=True, padx=1, pady=1)

        bar_color = accent or Theme.ACCENT
        accent_bar = tk.Frame(inner, bg=bar_color, width=4)
        accent_bar.pack(side="left", fill="y")

        body = tk.Frame(inner, bg=Theme.BG_SURFACE)
        body.pack(side="left", fill="both", expand=True)

        tk.Label(
            body, text=title, bg=Theme.BG_SURFACE, fg=Theme.FG_SECONDARY,
            font=Theme.FONT_CARD_T,
        ).pack(anchor="w", padx=18, pady=(16, 4))

        tk.Label(
            body, text=value, bg=Theme.BG_SURFACE, fg=Theme.FG_PRIMARY,
            font=Theme.FONT_CARD_V,
        ).pack(anchor="w", padx=18)

        if subtitle:
            tk.Label(
                body, text=subtitle, bg=Theme.BG_SURFACE, fg=Theme.FG_MUTED,
                font=Theme.FONT_CARD_S,
            ).pack(anchor="w", padx=18, pady=(4, 16))
        else:
            tk.Frame(body, bg=Theme.BG_SURFACE, height=16).pack()

        return outer

    def panel(self, parent, title=None, padding=16):
        outer = tk.Frame(parent, bg=Theme.BORDER)
        inner = tk.Frame(outer, bg=Theme.BG_SURFACE)
        inner.pack(fill="both", expand=True, padx=1, pady=1)

        if title:
            tk.Label(
                inner, text=title, bg=Theme.BG_SURFACE, fg=Theme.FG_PRIMARY,
                font=Theme.FONT_SECTION,
            ).pack(anchor="w", padx=padding, pady=(padding, 6))

        return outer, inner

    def action_button(self, parent, text, command, kind="primary"):
        style = {
            "primary":   "Primary.TButton",
            "secondary": "Secondary.TButton",
            "danger":    "Danger.TButton",
        }.get(kind, "Primary.TButton")

        return ttk.Button(parent, text=text, command=command, style=style)

    # ========================================================
    #  FILE OPENING
    # ========================================================
    def open_file(self, path):
        try:
            path = Path(path)
            if not path.exists():
                messagebox.showerror(
                    "File Not Found",
                    f"The file could not be found:\n\n{path}"
                )
                return False
            if hasattr(os, "startfile"):
                os.startfile(str(path))
            else:
                messagebox.showinfo("File Location", str(path))
            return True
        except Exception as error:
            messagebox.showerror("Open File Error", str(error))
            return False

    def open_folder(self, folder):
        try:
            folder = Path(folder)
            folder.mkdir(parents=True, exist_ok=True)
            if hasattr(os, "startfile"):
                os.startfile(str(folder))
            return True
        except Exception as error:
            messagebox.showerror("Folder Error", str(error))
            return False

    # ========================================================
    #  RESULTS VIEWER
    # ========================================================
    def show_results_viewer(self):
        try:
            self.output_win.show()
        except Exception:
            self.output_win = OutputWindow("MWCNT Results Viewer")
            self.output_win.show()

    # ========================================================
    #  DASHBOARD
    # ========================================================
    def show_dashboard(self):
        self.clear_content()
        self._set_active_nav("Dashboard")

        self.page_title(
            "Characterization Dashboard",
            "Overview of the available MWCNT characterization datasets.",
            breadcrumb="Home / Dashboard",
        )

        summary = analysis.get_characterization_summary()

        cards = tk.Frame(self.content, bg=Theme.BG_APP)
        cards.pack(fill="x", padx=32, pady=(4, 6))

        values = [
            ("BET Surface Area",  summary["BET surface area (m²/g)"],        "m²/g",     "#2563eb"),
            ("BJH Mode Radius",   summary["BJH adsorption mode radius (nm)"], "adsorption","#0f766e"),
            ("DFT Peak Width",    summary["DFT peak pore width (nm)"],       "nm",       "#7c3aed"),
            ("EDS Composition",   summary["EDS total weight (%)"],           "% total",  "#0891b2"),
            ("SEM Images",        summary["SEM image count"],                "images",   "#d97706"),
            ("TEM Images",        summary["TEM image count"],                "images",   "#dc2626"),
        ]

        for index, (title, value, subtitle, color) in enumerate(values):
            if value is None:
                display = "N/A"
            elif isinstance(value, float):
                display = f"{value:.4f}"
            else:
                display = str(value)

            self.card(cards, title, display, subtitle, accent=color).grid(
                row=index // 3, column=index % 3,
                padx=6, pady=6, sticky="nsew"
            )

        for column in range(3):
            cards.columnconfigure(column, weight=1)

        outer, inner = self.panel(self.content, "Characterization Status")
        outer.pack(fill="both", expand=True, padx=32, pady=(10, 24))

        statistics = analysis.get_dataset_statistics()

        tk.Label(
            inner,
            text=(f"Processed datasets available: "
                  f"{statistics['available']} / {statistics['total']}  "
                  f"({statistics['percentage']:.1f}%)"),
            bg=Theme.BG_SURFACE, fg=Theme.FG_PRIMARY,
            font=(Theme.FONT_FAMILY, 11, "bold"),
        ).pack(anchor="w", padx=20, pady=(4, 10))

        bar = tk.Frame(inner, bg="#e2e8f0", height=8)
        bar.pack(fill="x", padx=20, pady=(0, 14))
        fill = tk.Frame(bar, bg=Theme.ACCENT, height=8)
        fill.place(relx=0, rely=0, relwidth=statistics["percentage"] / 100.0, relheight=1)

        for item in analysis.evaluate_characterization():
            row = tk.Frame(inner, bg=Theme.BG_SURFACE)
            row.pack(fill="x", padx=20, pady=3)
            tk.Label(
                row, text="●", bg=Theme.BG_SURFACE, fg=Theme.ACCENT,
                font=(Theme.FONT_FAMILY, 8),
            ).pack(side="left", padx=(0, 8))
            tk.Label(
                row, text=item, bg=Theme.BG_SURFACE, fg=Theme.FG_SECONDARY,
                font=Theme.FONT_BODY, anchor="w",
            ).pack(side="left", fill="x")

        self.set_status("Dashboard loaded", Theme.SUCCESS)

    # ========================================================
    #  BET
    # ========================================================
    def show_bet(self):
        self.clear_content()
        self._set_active_nav("BET Analysis")

        self.page_title(
            "BET Surface Area Analysis",
            "Nitrogen adsorption-desorption and specific surface area.",
            breadcrumb="Home / BET Analysis",
        )

        area = analysis.get_bet_surface_area()
        points = analysis.get_bet_isotherm_summary()

        top = tk.Frame(self.content, bg=Theme.BG_APP)
        top.pack(fill="x", padx=32)

        self.card(
            top, "BET Surface Area",
            "N/A" if area is None else f"{area:.3f} m²/g",
            "Multi-point BET",
            accent="#2563eb",
        ).pack(side="left", padx=(0, 10), fill="y")

        self.card(
            top, "Isotherm Points",
            str(points["total_points"]),
            "adsorption + desorption",
            accent="#0f766e",
        ).pack(side="left", fill="y")

        controls = tk.Frame(self.content, bg=Theme.BG_APP)
        controls.pack(fill="x", padx=32, pady=16)
        self.action_button(controls, "📈  Generate BET Plot",
                           self.generate_bet_plot, kind="primary").pack(side="left")

        outer, inner = self.panel(self.content, "BET Parameters")
        outer.pack(fill="both", expand=True, padx=32, pady=(0, 24))

        columns = ("parameter", "method", "value", "unit")
        tree = ttk.Treeview(inner, columns=columns, show="headings")

        headings = {"parameter": "Parameter", "method": "Method",
                    "value": "Value", "unit": "Unit"}
        widths = {"parameter": 260, "method": 240, "value": 140, "unit": 100}

        for column in columns:
            tree.heading(column, text=headings[column])
            tree.column(column, width=widths[column], anchor="w")

        for row in analysis.get_bet_parameters():
            tree.insert("", "end", values=(
                row["parameter"], row["method"], row["value"], row["unit"]
            ))

        tree.pack(fill="both", expand=True, padx=12, pady=(0, 12))

        self.set_status("BET Analysis loaded")

    # ========================================================
    #  BJH
    # ========================================================
    def show_bjh(self):
        self.clear_content()
        self._set_active_nav("BJH Analysis")

        self.page_title(
            "BJH Pore Size Analysis",
            "Separate adsorption and desorption pore-size distributions.",
            breadcrumb="Home / BJH Analysis",
        )

        summary = analysis.get_bjh_summary()

        cards = tk.Frame(self.content, bg=Theme.BG_APP)
        cards.pack(fill="x", padx=32)

        card_data = [
            ("Adsorption Radius",       summary["adsorption_mode_radius_nm"],           "nm",     "#2563eb"),
            ("Adsorption Diameter",     summary["adsorption_mode_diameter_nm"],         "nm",     "#2563eb"),
            ("Adsorption Pore Volume",  summary["adsorption_total_pore_volume_cm3_g"],  "cm³/g",  "#2563eb"),
            ("Desorption Radius",       summary["desorption_mode_radius_nm"],           "nm",     "#dc2626"),
            ("Desorption Diameter",     summary["desorption_mode_diameter_nm"],         "nm",     "#dc2626"),
            ("Desorption Pore Volume",  summary["desorption_total_pore_volume_cm3_g"],  "cm³/g",  "#dc2626"),
        ]

        for i, (title, value, unit, color) in enumerate(card_data):
            text = "N/A" if value is None else f"{value:.4f}"
            self.card(cards, title, text, unit, accent=color).grid(
                row=i // 3, column=i % 3, padx=6, pady=6, sticky="nsew"
            )

        for i in range(3):
            cards.columnconfigure(i, weight=1)

        buttons = tk.Frame(self.content, bg=Theme.BG_APP)
        buttons.pack(fill="x", padx=32, pady=16)

        self.action_button(buttons, "Adsorption Plot",
                           self.generate_bjh_adsorption).pack(side="left", padx=(0, 8))
        self.action_button(buttons, "Desorption Plot",
                           self.generate_bjh_desorption).pack(side="left", padx=8)
        self.action_button(buttons, "Comparison Plot",
                           self.generate_bjh_comparison).pack(side="left", padx=8)

        outer, inner = self.panel(self.content, "Notes")
        outer.pack(fill="x", padx=32, pady=(0, 24))

        tk.Label(
            inner,
            text=("BJH reporting distinguishes pore radius from pore diameter. "
                  "The mode is obtained from the maximum dV/dlog(r) value "
                  "in the selected distribution."),
            bg=Theme.BG_SURFACE, fg=Theme.FG_SECONDARY,
            font=Theme.FONT_BODY, wraplength=1000, justify="left",
        ).pack(anchor="w", padx=20, pady=(0, 18))

        self.set_status("BJH Analysis loaded")

    # ========================================================
    #  DFT
    # ========================================================
    def show_dft(self):
        self.clear_content()
        self._set_active_nav("DFT Analysis")

        self.page_title(
            "DFT Pore Structure Analysis",
            "Pore-width distribution and model-fitting evaluation.",
            breadcrumb="Home / DFT Analysis",
        )

        summary = analysis.get_dft_summary()
        fit = analysis.calculate_dft_fit_statistics()

        cards = tk.Frame(self.content, bg=Theme.BG_APP)
        cards.pack(fill="x", padx=32)

        data = [
            ("Peak Pore Width",          summary["peak_pore_width_nm"],               "nm",         "#7c3aed"),
            ("Peak Differential Volume", summary["peak_differential_volume_cm3_nm_g"],"cm³/g/nm",   "#7c3aed"),
            ("Total Pore Volume",        summary["total_pore_volume_cm3_g"],          "cm³/g",      "#7c3aed"),
            ("Surface Area",             summary["total_surface_area_m2_g"],          "m²/g",       "#7c3aed"),
            ("Fit RMSE",                 fit["rmse"],                                 "cm³/g",      "#0891b2"),
            ("Fit R²",                   fit["r2"],                                   "dimensionless","#0891b2"),
        ]

        for i, (title, value, unit, color) in enumerate(data):
            if value is None:
                text = "N/A"
            elif isinstance(value, float):
                text = f"{value:.5f}"
            else:
                text = str(value)

            self.card(cards, title, text, unit, accent=color).grid(
                row=i // 3, column=i % 3, padx=6, pady=6, sticky="nsew"
            )

        for i in range(3):
            cards.columnconfigure(i, weight=1)

        buttons = tk.Frame(self.content, bg=Theme.BG_APP)
        buttons.pack(fill="x", padx=32, pady=16)

        self.action_button(buttons, "Pore Distribution",
                           self.generate_dft_distribution).pack(side="left", padx=(0, 8))
        self.action_button(buttons, "Surface Area Plot",
                           self.generate_dft_surface).pack(side="left", padx=8)
        self.action_button(buttons, "Fitting Plot",
                           self.generate_dft_fitting).pack(side="left", padx=8)

        self.set_status("DFT Analysis loaded")

    # ========================================================
    #  EDS
    # ========================================================
    def show_eds(self):
        self.clear_content()
        self._set_active_nav("EDS Analysis")

        self.page_title(
            "EDS Elemental Analysis",
            "Elemental composition obtained from the processed EDS dataset.",
            breadcrumb="Home / EDS Analysis",
        )

        summary = analysis.get_eds_summary()

        top = tk.Frame(self.content, bg=Theme.BG_APP)
        top.pack(fill="x", padx=32)

        self.card(
            top, "Total Composition",
            f"{summary['total_weight_percent']:.2f}%",
            "sum of detected elements",
            accent="#0891b2",
        ).pack(side="left", padx=(0, 10), fill="y")

        self.card(
            top, "Detected Elements",
            str(summary["element_count"]), "elements",
            accent="#16a34a",
        ).pack(side="left", fill="y")

        buttons = tk.Frame(self.content, bg=Theme.BG_APP)
        buttons.pack(fill="x", padx=32, pady=16)

        self.action_button(buttons, "⚛  Generate EDS Plot",
                           self.generate_eds_plot, kind="primary").pack(side="left")

        outer, inner = self.panel(self.content, "Elemental Composition")
        outer.pack(fill="both", expand=True, padx=32, pady=(0, 24))

        columns = ("element", "weight", "sigma")
        tree = ttk.Treeview(inner, columns=columns, show="headings")
        tree.heading("element", text="Element")
        tree.heading("weight", text="Weight (%)")
        tree.heading("sigma", text="Sigma")

        tree.column("element", width=180)
        tree.column("weight", width=180, anchor="e")
        tree.column("sigma", width=180, anchor="e")

        for item in summary["elements"]:
            tree.insert("", "end", values=(
                item["element"], item["weight_percent"], item["sigma"]
            ))

        tree.pack(fill="both", expand=True, padx=12, pady=(0, 12))

        self.set_status("EDS Analysis loaded")

    # ========================================================
    #  XRD
    # ========================================================
    def show_xrd(self):
        self.clear_content()
        self._set_active_nav("XRD / SRD")

        self.page_title(
            "XRD / SRD Analysis",
            "Diffraction-pattern inspection and local peak detection.",
            breadcrumb="Home / XRD / SRD",
        )

        summary = analysis.get_xrd_summary()
        strongest = summary["strongest_point"]

        if strongest:
            theta = strongest["two_theta"]
            intensity = strongest["intensity"]
        else:
            theta = None
            intensity = None

        top = tk.Frame(self.content, bg=Theme.BG_APP)
        top.pack(fill="x", padx=32)

        self.card(top, "Strongest Intensity Point",
                  "N/A" if theta is None else f"{theta:.4f}°", "2θ",
                  accent="#0f172a"
                  ).pack(side="left", padx=(0, 10), fill="y")

        self.card(top, "Intensity",
                  "N/A" if intensity is None else f"{intensity:.0f}", "counts",
                  accent="#0f172a"
                  ).pack(side="left", padx=10, fill="y")

        self.card(top, "Detected Local Peaks",
                  str(summary["detected_peak_count"]), "candidate peaks",
                  accent="#0f172a"
                  ).pack(side="left", padx=10, fill="y")

        buttons = tk.Frame(self.content, bg=Theme.BG_APP)
        buttons.pack(fill="x", padx=32, pady=16)

        self.action_button(buttons, "🔬  Generate XRD Plot",
                           self.generate_xrd_plot, kind="primary").pack(side="left")

        outer, inner = self.panel(self.content, "Detected Peaks")
        outer.pack(fill="both", expand=True, padx=32, pady=(0, 24))

        columns = ("theta", "intensity", "prominence")
        tree = ttk.Treeview(inner, columns=columns, show="headings")
        tree.heading("theta", text="2θ (degrees)")
        tree.heading("intensity", text="Intensity")
        tree.heading("prominence", text="Prominence")

        tree.column("theta", width=180, anchor="e")
        tree.column("intensity", width=180, anchor="e")
        tree.column("prominence", width=180, anchor="e")

        for peak in summary["detected_peaks"]:
            tree.insert("", "end", values=(
                f"{peak['two_theta']:.4f}",
                f"{peak['intensity']:.0f}",
                f"{peak['prominence']:.2f}"
            ))

        tree.pack(fill="both", expand=True, padx=12, pady=(0, 12))

        self.set_status("XRD Analysis loaded")

    # ========================================================
    #  SEM / TEM
    # ========================================================
    def show_morphology(self):
        self.clear_content()
        self._set_active_nav("SEM / TEM")

        self.page_title(
            "SEM / TEM Morphology",
            "Available microscopy images and acquisition metadata.",
            breadcrumb="Home / SEM / TEM",
        )

        images = analysis.get_image_paths()

        top = tk.Frame(self.content, bg=Theme.BG_APP)
        top.pack(fill="x", padx=32)

        self.card(top, "SEM Images", str(len(images["sem"])), "available",
                  accent="#d97706"
                  ).pack(side="left", padx=(0, 10), fill="y")

        self.card(top, "TEM Images", str(len(images["tem"])), "available",
                  accent="#dc2626"
                  ).pack(side="left", fill="y")

        outer, inner = self.panel(self.content, "Important Note")
        outer.pack(fill="x", padx=32, pady=16)

        tk.Label(
            inner,
            text=("Important: this system records the available SEM/TEM images "
                  "but does not invent CNT diameter, length, dispersion or "
                  "morphological measurements. Quantitative image measurements "
                  "should be obtained from properly calibrated images."),
            bg=Theme.BG_SURFACE, fg=Theme.FG_SECONDARY,
            font=Theme.FONT_BODY, wraplength=1050, justify="left",
        ).pack(anchor="w", padx=20, pady=(0, 18))

        outer2, inner2 = self.panel(self.content, "SEM Metadata")
        outer2.pack(fill="both", expand=True, padx=32, pady=(0, 24))

        columns = ("file", "magnification", "eht", "wd", "pixel")
        tree = ttk.Treeview(inner2, columns=columns, show="headings")

        headings = {
            "file": "Image", "magnification": "Magnification",
            "eht": "EHT", "wd": "Working Distance", "pixel": "Pixel Size"
        }
        for column in columns:
            tree.heading(column, text=headings[column])
            tree.column(column, width=180)

        for row in analysis.load_sem_metadata():
            tree.insert("", "end", values=(
                row.get("file", ""),
                row.get("magnification", ""),
                row.get("eht_kv", ""),
                row.get("wd_mm", ""),
                row.get("pixel_size_nm", "")
            ))

        tree.pack(fill="both", expand=True, padx=12, pady=(0, 12))

        self.set_status("SEM / TEM loaded")

    # ========================================================
    #  REPORTS
    # ========================================================
    def show_reports(self):
        self.clear_content()
        self._set_active_nav("Reports")

        self.page_title(
            "Scientific Reports",
            "Generate, open and manage MWCNT characterization reports.",
            breadcrumb="Home / Reports",
        )

        controls = tk.Frame(self.content, bg=Theme.BG_APP)
        controls.pack(fill="x", padx=32, pady=(0, 8))

        self.action_button(controls, "📄  Generate Complete Report",
                           self.generate_report, kind="primary").pack(side="left", padx=(0, 8))

        self.action_button(controls, "Open Reports Folder",
                           lambda: self.open_folder(USER_REPORTS_DIR),
                           kind="secondary").pack(side="left", padx=8)

        self.action_button(controls, "Open Plots Folder",
                           lambda: self.open_folder(USER_PLOTS_DIR),
                           kind="secondary").pack(side="left", padx=8)

        outer, inner = self.panel(self.content, "Available Reports")
        outer.pack(fill="both", expand=True, padx=32, pady=(10, 24))

        database_reports = database.get_reports()
        reports_map = {}

        for item in database_reports:
            filename = item.get("filename", "")
            if filename:
                reports_map[filename] = {
                    "id": item.get("id", ""),
                    "filename": filename,
                    "created_at": item.get("created_at", "")
                }

        # Scan both bundled and user reports folders
        scanned = set()
        for base in (REPORTS_DIR, USER_REPORTS_DIR):
            try:
                for pdf in sorted(base.glob("*.pdf"),
                                  key=lambda p: p.stat().st_mtime, reverse=True):
                    filename = pdf.name
                    if filename not in reports_map:
                        reports_map[filename] = {
                            "id": "", "filename": filename, "created_at": ""
                        }
                    scanned.add(filename)
            except Exception:
                pass

        reports_list = list(reports_map.values())
        reports_list.sort(key=lambda item: item.get("created_at", ""), reverse=True)

        if not reports_list:
            tk.Label(
                inner, text="No reports are available yet.",
                bg=Theme.BG_SURFACE, fg=Theme.FG_MUTED,
                font=(Theme.FONT_FAMILY, 11),
            ).pack(pady=50)
            self.set_status("No reports found", Theme.WARNING)
            return

        columns = ("id", "filename", "created")
        tree = ttk.Treeview(inner, columns=columns,
                            show="headings", selectmode="browse")
        tree.heading("id", text="ID")
        tree.heading("filename", text="Report")
        tree.heading("created", text="Created")

        tree.column("id", width=70, anchor="center")
        tree.column("filename", width=560)
        tree.column("created", width=220)

        for item in reports_list:
            tree.insert("", "end", values=(
                item.get("id", ""),
                item.get("filename", ""),
                item.get("created_at", "")
            ))

        tree.pack(fill="both", expand=True, padx=12, pady=(0, 12))

        def open_selected_report(event=None):
            selected = tree.selection()
            if not selected:
                return
            values = tree.item(selected[0], "values")
            if not values:
                return
            filename = values[1]
            # Try user folder first, then bundled
            for base in (USER_REPORTS_DIR, REPORTS_DIR):
                candidate = base / filename
                if candidate.exists():
                    self.open_file(candidate)
                    return
            # Fallback
            self.open_file(USER_REPORTS_DIR / filename)

        tree.bind("<Double-1>", open_selected_report)

        bottom = tk.Frame(inner, bg=Theme.BG_SURFACE)
        bottom.pack(fill="x", padx=12, pady=(0, 12))

        self.action_button(bottom, "Open Selected Report",
                           open_selected_report, kind="secondary").pack(side="left")

        tk.Label(
            bottom, text="Double-click a report to open it.",
            bg=Theme.BG_SURFACE, fg=Theme.FG_MUTED,
            font=Theme.FONT_SMALL,
        ).pack(side="left", padx=15)

        self.set_status(f"{len(reports_list)} report(s) available")

    # ========================================================
    #  PLOT ACTIONS
    # ========================================================
    def notify_plot(self, function, caption="Plot"):
        try:
            self.set_status(f"Generating {caption}…", Theme.ACCENT)
            self.update_idletasks()

            path = function()
            if path is None:
                raise RuntimeError("The plotting function did not return a file path.")

            path = Path(path)
            if not path.exists():
                raise FileNotFoundError(f"Generated plot was not found:\n{path}")

            output_image(str(path), caption=caption)
            self.show_results_viewer()

            self.set_status(f"{caption} displayed", Theme.SUCCESS)

        except Exception as error:
            self.set_status(f"Error: {caption}", Theme.DANGER)
            messagebox.showerror("Plot Error", str(error))

    def generate_bet_plot(self):
        self.notify_plot(visualization.plot_bet_isotherm, "BET Isotherm")

    def generate_bjh_adsorption(self):
        self.notify_plot(visualization.plot_bjh_adsorption, "BJH Adsorption")

    def generate_bjh_desorption(self):
        self.notify_plot(visualization.plot_bjh_desorption, "BJH Desorption")

    def generate_bjh_comparison(self):
        self.notify_plot(visualization.plot_bjh_comparison, "BJH Comparison")

    def generate_dft_distribution(self):
        self.notify_plot(visualization.plot_dft_distribution, "DFT Pore Distribution")

    def generate_dft_surface(self):
        self.notify_plot(visualization.plot_dft_surface_area, "DFT Surface Area")

    def generate_dft_fitting(self):
        self.notify_plot(visualization.plot_dft_fitting, "DFT Fitting")

    def generate_eds_plot(self):
        self.notify_plot(visualization.plot_eds_composition, "EDS Composition")

    def generate_xrd_plot(self):
        self.notify_plot(visualization.plot_xrd, "XRD Pattern")

    # ========================================================
    #  COMPLETE REPORT
    # ========================================================
    def generate_report(self):
        try:
            self.set_status("Generating all plots…", Theme.ACCENT)
            self.update_idletasks()

            generated, errors = visualization.generate_all_plots()

            if errors:
                output_report("Plot generation warnings:\n" + "\n".join(errors))

            self.set_status("Building PDF report…", Theme.ACCENT)
            self.update_idletasks()

            path = reports.generate_report()
            path = Path(path)

            if not path.exists():
                raise FileNotFoundError(
                    f"The generated report was not found:\n{path}"
                )

            database.save_report(str(path))
            database.save_analysis_history(
                "Complete characterization report generated"
            )

            output_report(
                f"Complete report generated\n"
                f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
                f"Saved to: {path}\n"
                f"Plots generated: {len(generated)}\n"
            )

            for png in sorted(PLOTS_DIR.glob("*.png"),
                              key=lambda p: p.stat().st_mtime):
                output_image(str(png), caption=png.stem)

            self.show_results_viewer()
            self.set_status("Report generated successfully", Theme.SUCCESS)

            messagebox.showinfo(
                "Report Generated",
                f"Complete characterization report generated.\n\n"
                f"Saved to:\n{path}\n\n"
                f"View plots in the Results Viewer."
            )

            self.show_reports()

        except Exception as error:
            self.set_status("Report generation failed", Theme.DANGER)
            messagebox.showerror("Report Error", str(error))


# ============================================================
#  ENTRY POINT
# ============================================================
def run_application():
    app = MWCNTApplication()
    app.mainloop()


if __name__ == "__main__":
    run_application()